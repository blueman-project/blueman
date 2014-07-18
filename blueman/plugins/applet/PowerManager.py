from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
import blueman.bluez as Bluez
from blueman.bluez.errors import BluezDBusException
from blueman.main.SignalTracker import SignalTracker
import types


class PowerManager(AppletPlugin):
    __depends__ = ["StatusIcon", "Menu"]
    __unloadable__ = True
    __description__ = _("Controls Bluetooth adapter power states")
    __author__ = "Walmis"
    __icon__ = "gnome-power-manager"

    def on_load(self, applet):
        AppletPlugin.add_method(self.on_power_state_query)
        AppletPlugin.add_method(self.on_power_state_change_requested)
        AppletPlugin.add_method(self.on_power_state_changed)

        self.add_dbus_method(self.SetBluetoothStatus,
                             in_signature="b",
                             out_signature="")

        self.add_dbus_method(self.GetBluetoothStatus,
                             in_signature="",
                             out_signature="b")

        self.BluetoothStatusChanged = self.add_dbus_signal(
            "BluetoothStatusChanged",
            signature="b")

        self.Applet = applet

        self.item = create_menuitem(_("<b>Bluetooth Off</b>"), get_icon("gtk-stop", 16))
        self.item.get_child().set_markup(_("<b>Turn Bluetooth Off</b>"))

        self.item.props.tooltip_text = _("Turn off all adapters")

        self.signals = SignalTracker()
        self.signals.Handle('bluez', Bluez.Adapter(), self.adapter_property_changed, "PropertyChanged",
                            path_keyword="path")

        self.signals.Handle(self.item, "activate", lambda x: self.on_bluetooth_toggled())

        self.Applet.Plugins.Menu.Register(self, self.item, 0)

        self.adapter_state = True
        self.current_state = True
        self.power_changeable = True

        self.request_in_progress = False

        self.STATE_ON = 2
        self.STATE_OFF = 1
        self.STATE_OFF_FORCED = 0

    def on_unload(self):
        self.signals.DisconnectAll()
        self.Applet.Plugins.Menu.Unregister(self)

    @property
    def CurrentState(self):
        return self.current_state

    def on_manager_state_changed(self, state):
        if state:
            def timeout():
                self.adapter_state = self.get_adapter_state()
                self.RequestPowerState(self.adapter_state)

            GObject.timeout_add(1000, timeout)

    def get_adapter_state(self):
        adapters = self.Applet.Manager.list_adapters()
        for adapter in adapters:
            props = adapter.get_properties()
            if not props["Powered"]:
                return False
        return bool(adapters)

    def set_adapter_state(self, state):
        try:
            dprint(state)
            adapters = self.Applet.Manager.list_adapters()
            for adapter in adapters:
                adapter.set("Powered", state)

            self.adapter_state = state
        except Exception as e:
            dprint("Exception occurred", e)


    class Callback(object):
        def __init__(self, parent, state):
            self.parent = parent
            self.num_cb = 0
            self.called = 0
            self.state = state
            self.success = False
            self.timer = GObject.timeout_add(5000, self.timeout)

        def __call__(self, result):
            self.called += 1

            if result:
                self.success = True

            self.check()

        def check(self):
            if self.called == self.num_cb:
                dprint("callbacks done")
                self.parent.set_adapter_state(self.state)
                GObject.source_remove(self.timer)
                self.parent.request_in_progress = False

        def timeout(self):
            dprint("Timeout reached while setting power state")
            self.parent.UpdatePowerState()
            self.parent.request_in_progress = False

    def RequestPowerState(self, state):
        if self.current_state != state:
            if not self.request_in_progress:
                self.request_in_progress = True
                dprint("Requesting", state)
                cb = PowerManager.Callback(self, state)

                rets = self.Applet.Plugins.Run("on_power_state_change_requested", self, state, cb)
                cb.num_cb = len(rets)
                cb.check()
                self.UpdatePowerState()
            else:
                dprint("Another request in progress")

    def on_power_state_change_requested(self, pm, state, cb):
        cb(None)

    def on_power_state_query(self, pm):
        if self.adapter_state:
            return self.STATE_ON
        else:
            return self.STATE_OFF

    def on_power_state_changed(self, manager, state):
        pass


    #queries other plugins to determine the current power state
    def UpdatePowerState(self):
        rets = self.Applet.Plugins.Run("on_power_state_query", self)

        off = True in map(lambda x: x < self.STATE_ON, rets)
        foff = self.STATE_OFF_FORCED in rets
        on = self.STATE_ON in rets

        new_state = True
        if foff or off:

            self.item.get_child().set_markup(_("<b>Turn Bluetooth On</b>"))
            self.item.props.tooltip_text = _("Turn on all adapters")
            self.item.set_image(Gtk.Image.new_from_pixbuf(get_icon("gtk-yes", 16)))

            if foff:
                self.item.props.sensitive = False
            else:
                self.item.props.sensitive = True

            new_state = False

        elif on and self.current_state != True:
            self.item.get_child().set_markup(_("<b>Turn Bluetooth Off</b>"))
            self.item.props.tooltip_text = _("Turn off all adapters")
            self.item.set_image(Gtk.Image.new_from_pixbuf(get_icon("gtk-stop", 16)))
            self.item.props.sensitive = True

            new_state = True

        dprint("off", off, "\nfoff", foff, "\non", on, "\ncurrent state", self.current_state, "\nnew state", new_state)

        if self.current_state != new_state:
            dprint("Signalling", new_state)
            self.current_state = new_state

            self.BluetoothStatusChanged(new_state)
            self.Applet.Plugins.Run("on_power_state_changed", self, new_state)
            self.Applet.Plugins.StatusIcon.IconShouldChange()

    #dbus method
    def SetBluetoothStatus(self, status):
        self.RequestPowerState(status)

    #dbus method
    def GetBluetoothStatus(self):
        return self.CurrentState

    def adapter_property_changed(self, key, value, path):
        if key == "Powered":
            if value and not self.CurrentState:
                dprint("adapter powered on while in off state, turning bluetooth on")
                self.RequestPowerState(True)

            self.UpdatePowerState()

    def on_bluetooth_toggled(self):
        self.RequestPowerState(not self.CurrentState)

    def on_status_icon_query_icon(self):
        #opacity = 255 if self.GetBluetoothStatus() else 100
        #pixbuf = opacify_pixbuf(pixbuf, opacity)

        #if opacity < 255:
        #	x_size = int(pixbuf.props.height)
        #	x = get_icon("blueman-x", x_size)
        #	pixbuf = composite_icon(pixbuf, [(x, pixbuf.props.height - x_size, pixbuf.props.height - x_size, 255)])

        #return pixbuf
        if not self.GetBluetoothStatus():
            return ("blueman-disabled", "blueman-disabled")

    def on_adapter_added(self, path):
        adapter = Bluez.Adapter(path)

        def on_ready():
            if not self.adapter_state:
                adapter.set("Powered", False)
            else:
                adapter.set("Powered", True)

        wait_for_adapter(adapter, on_ready)


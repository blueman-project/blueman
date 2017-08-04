# coding=utf-8
import dbus.service
import logging
from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
import blueman.bluez as Bluez

from gi.repository import GLib


class PowerManager(AppletPlugin):
    __depends__ = ["StatusIcon", "Menu"]
    __unloadable__ = True
    __description__ = _("Controls Bluetooth adapter power states")
    __author__ = "Walmis"
    __icon__ = "gnome-power-manager"

    __gsettings__ = {
        "schema": "org.blueman.plugins.powermanager",
        "path": None
    }

    __options__ = {
        "auto-power-on": {
            "type": bool,
            "default": True,
            "name": _("Auto power-on"),
            "desc": _("Automatically power on adapters")
        }
    }

    def on_load(self, applet):
        AppletPlugin.add_method(self.on_power_state_query)
        AppletPlugin.add_method(self.on_power_state_change_requested)
        AppletPlugin.add_method(self.on_power_state_changed)

        self.Applet = applet

        self.item = create_menuitem("Should be overwritten", "blueman-disabled")
        self.item.get_child().get_children()[1].set_markup_with_mnemonic(_("<b>Turn Bluetooth _Off</b>"))

        self.item.props.tooltip_text = _("Turn off all adapters")

        self.item.connect("activate", lambda x: self.on_bluetooth_toggled())

        self.Applet.Plugins.Menu.Register(self, self.item, 0)

        self.adapter_state = True
        self.current_state = True

        self.request_in_progress = False

        self.STATE_ON = 2
        self.STATE_OFF = 1
        self.STATE_OFF_FORCED = 0

    def on_unload(self):
        self.Applet.Plugins.Menu.Unregister(self)

    @property
    def CurrentState(self):
        return self.current_state

    def on_manager_state_changed(self, state):
        if state:
            def timeout():
                self.adapter_state = self.get_adapter_state()
                if self.get_option("auto-power-on"):
                    self.RequestPowerState(True, force=True)
                else:
                    self.RequestPowerState(self.adapter_state)

            GLib.timeout_add(1000, timeout)

    def get_adapter_state(self):
        adapters = self.Applet.Manager.get_adapters()
        for adapter in adapters:
            if not adapter["Powered"]:
                return False
        return bool(adapters)

    def set_adapter_state(self, state):
        try:
            logging.info(state)
            adapters = self.Applet.Manager.get_adapters()
            for adapter in adapters:
                adapter.set("Powered", state)

            self.adapter_state = state
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    class Callback(object):
        def __init__(self, parent, state):
            self.parent = parent
            self.num_cb = 0
            self.called = 0
            self.state = state
            self.success = False
            self.timer = GLib.timeout_add(5000, self.timeout)

        def __call__(self, result):
            self.called += 1

            if result:
                self.success = True

            self.check()

        def check(self):
            if self.called == self.num_cb:
                logging.info("callbacks done")
                self.parent.set_adapter_state(self.state)
                GLib.source_remove(self.timer)
                self.parent.request_in_progress = False

        def timeout(self):
            logging.info("Timeout reached while setting power state")
            self.parent.UpdatePowerState()
            self.parent.request_in_progress = False

    def RequestPowerState(self, state, force=False):
        if self.current_state != state or force:
            if not self.request_in_progress:
                self.request_in_progress = True
                logging.info("Requesting %s" % state)
                cb = PowerManager.Callback(self, state)

                rets = self.Applet.Plugins.Run("on_power_state_change_requested", self, state, cb)
                cb.num_cb = len(rets)
                cb.check()
                self.UpdatePowerState()
            else:
                logging.info("Another request in progress")

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

        icon, label = self.item.get_child().get_children()

        new_state = True
        if foff or off:

            label.set_markup_with_mnemonic(_("<b>Turn Bluetooth _On</b>"))
            icon.props.icon_name = "blueman"
            self.item.props.tooltip_text = _("Turn on all adapters")

            if foff:
                self.item.props.sensitive = False
            else:
                self.item.props.sensitive = True

            new_state = False

        elif on and not self.current_state:

            label.set_markup_with_mnemonic(_("<b>Turn Bluetooth _Off</b>"))
            icon.props.icon_name = "blueman-disabled"
            self.item.props.tooltip_text = _("Turn off all adapters")
            self.item.props.sensitive = True

            new_state = True

        logging.info("off %s | foff %s | on %s | current state %s | new state %s" %
                     (off, foff, on, self.current_state, new_state))

        if self.current_state != new_state:
            logging.info("Signalling %s" % new_state)
            self.current_state = new_state

            self.BluetoothStatusChanged(new_state)
            self.Applet.Plugins.Run("on_power_state_changed", self, new_state)
            self.Applet.Plugins.StatusIcon.IconShouldChange()

    @dbus.service.signal('org.blueman.Applet', signature="b")
    def BluetoothStatusChanged(self, status):
        pass

    @dbus.service.method('org.blueman.Applet', in_signature="b", out_signature="")
    def SetBluetoothStatus(self, status):
        self.RequestPowerState(status)

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="b")
    def GetBluetoothStatus(self):
        return self.CurrentState

    def on_adapter_property_changed(self, _path, key, value):
        if key == "Powered":
            if value and not self.CurrentState:
                logging.warning("adapter powered on while in off state, turning bluetooth on")
                self.RequestPowerState(True)

            self.UpdatePowerState()

    def on_bluetooth_toggled(self):
        self.RequestPowerState(not self.CurrentState)

    def on_status_icon_query_icon(self):
        if not self.GetBluetoothStatus():
            return "blueman-disabled", "blueman-disabled"

    def on_adapter_added(self, path):
        adapter = Bluez.Adapter(path)

        def on_ready():
            if not self.adapter_state:
                adapter.set("Powered", False)
            else:
                adapter.set("Powered", True)

        wait_for_adapter(adapter, on_ready)


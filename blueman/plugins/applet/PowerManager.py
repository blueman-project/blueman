# coding=utf-8

import logging
from blueman.plugins.AppletPlugin import AppletPlugin
import blueman.bluez as bluez

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

    def on_load(self):
        AppletPlugin.add_method(self.on_power_state_query)
        AppletPlugin.add_method(self.on_power_state_change_requested)
        AppletPlugin.add_method(self.on_power_state_changed)

        self.item = self.parent.Plugins.Menu.add(self, 0, text=_("<b>Turn Bluetooth _Off</b>"), markup=True,
                                                 icon_name="blueman-disabled", tooltip=_("Turn off all adapters"),
                                                 callback=self.on_bluetooth_toggled)
        self.adapter_state = True
        self.current_state = True

        self.request_in_progress = False

        self.STATE_ON = 2
        self.STATE_OFF = 1
        self.STATE_OFF_FORCED = 0

        self._add_dbus_signal("BluetoothStatusChanged", "b")
        self._add_dbus_method("SetBluetoothStatus", ("b",), "", self.request_power_state)
        self._add_dbus_method("GetBluetoothStatus", (), "b", self.get_bluetooth_status)

    def on_unload(self):
        self.parent.Plugins.Menu.unregister(self)

    @property
    def CurrentState(self):
        return self.current_state

    def on_manager_state_changed(self, state):
        if state:
            def timeout():
                self.adapter_state = self.get_adapter_state()
                if self.get_option("auto-power-on"):
                    self.request_power_state(True, force=True)
                else:
                    self.request_power_state(self.adapter_state)

            GLib.timeout_add(1000, timeout)

    def get_adapter_state(self):
        adapters = self.parent.Manager.get_adapters()
        for adapter in adapters:
            if not adapter["Powered"]:
                return False
        return bool(adapters)

    def set_adapter_state(self, state):
        try:
            logging.info(state)
            adapters = self.parent.Manager.get_adapters()
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
                GLib.source_remove(self.timer)
                logging.info("callbacks done")
                self.parent.set_adapter_state(self.state)
                self.parent.update_power_state()
                self.parent.request_in_progress = False

        def timeout(self):
            logging.info("Timeout reached while setting power state")
            self.parent.update_power_state()
            self.parent.request_in_progress = False
            return False

    def request_power_state(self, state, force=False):
        if self.current_state != state or force:
            if not self.request_in_progress:
                self.request_in_progress = True
                logging.info("Requesting %s" % state)
                cb = PowerManager.Callback(self, state)

                rets = self.parent.Plugins.run("on_power_state_change_requested", self, state, cb)
                cb.num_cb = len(rets)
                cb.check()
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

    # queries other plugins to determine the current power state
    def update_power_state(self):
        rets = self.parent.Plugins.run("on_power_state_query", self)

        off = True in map(lambda x: x < self.STATE_ON, rets)
        foff = self.STATE_OFF_FORCED in rets
        on = self.STATE_ON in rets

        new_state = True
        if foff or off:

            self.item.set_text(_("<b>Turn Bluetooth _On</b>"), markup=True)
            self.item.set_icon_name("blueman")
            self.item.set_tooltip(_("Turn on all adapters"))
            self.item.set_sensitive(not foff)

            new_state = False

        elif on and not self.current_state:

            self.item.set_text(_("<b>Turn Bluetooth _Off</b>"), markup=True)
            self.item.set_icon_name("blueman-disabled")
            self.item.set_tooltip(_("Turn off all adapters"))
            self.item.set_sensitive(True)

            new_state = True

        logging.info("off %s | foff %s | on %s | current state %s | new state %s" %
                     (off, foff, on, self.current_state, new_state))

        if self.current_state != new_state:
            logging.info("Signalling %s" % new_state)
            self.current_state = new_state

            self._emit_dbus_signal("BluetoothStatusChanged", new_state)
            self.parent.Plugins.run("on_power_state_changed", self, new_state)
            self.parent.Plugins.StatusIcon.icon_should_change()

    def get_bluetooth_status(self):
        return self.current_state

    def on_adapter_property_changed(self, _path, key, value):
        if key == "Powered":
            if value and not self.current_state:
                logging.warning("adapter powered on while in off state, turning bluetooth on")
                self.request_power_state(True)

            self.update_power_state()

    def on_bluetooth_toggled(self):
        self.request_power_state(not self.current_state)

    def on_status_icon_query_icon(self):
        if not self.get_bluetooth_status():
            return "blueman-disabled", "blueman-disabled"

    def on_adapter_added(self, path):
        adapter = bluez.Adapter(path)
        adapter.set("Powered", self.adapter_state)

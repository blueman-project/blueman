from enum import Enum
from gettext import gettext as _
import logging
from typing import Callable, Any, Optional

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Adapter import Adapter

from gi.repository import GLib

from blueman.plugins.applet.StatusIcon import StatusIconProvider


class PowerStateListener:
    def on_power_state_changed(self, manager: "PowerManager", state: bool) -> None:
        ...


class PowerStateHandler:
    def on_power_state_query(self) -> "PowerManager.State":
        ...

    def on_power_state_change_requested(self, manager: "PowerManager", state: bool,
                                        cb: Callable[[bool], None]) -> None:
        ...


class PowerManager(AppletPlugin, StatusIconProvider):
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

    class State(Enum):
        ON = 2
        OFF = 1
        OFF_FORCED = 0

    def on_load(self) -> None:
        self.item = self.parent.Plugins.Menu.add(self, 0, text=_("<b>Turn Bluetooth _Off</b>"), markup=True,
                                                 icon_name="blueman-disabled", tooltip=_("Turn off all adapters"),
                                                 callback=self.on_bluetooth_toggled)
        self.adapter_state = True
        self.current_state = True

        self.request_in_progress = False

        self._add_dbus_signal("BluetoothStatusChanged", "b")
        self._add_dbus_method("SetBluetoothStatus", ("b",), "", self.request_power_state)
        self._add_dbus_method("GetBluetoothStatus", (), "b", self.get_bluetooth_status)

    def on_unload(self) -> None:
        self.parent.Plugins.Menu.unregister(self)

    @property
    def CurrentState(self) -> bool:
        return self.current_state

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            def timeout() -> bool:
                self.adapter_state = self.get_adapter_state()
                if self.get_option("auto-power-on"):
                    self.request_power_state(True, force=True)
                else:
                    self.request_power_state(self.adapter_state)
                return False

            GLib.timeout_add(1000, timeout)

    def get_adapter_state(self) -> bool:
        adapters = self.parent.Manager.get_adapters()
        for adapter in adapters:
            if not adapter["Powered"]:
                return False
        return bool(adapters)

    def set_adapter_state(self, state: bool) -> None:
        try:
            logging.info(state)
            adapters = self.parent.Manager.get_adapters()
            for adapter in adapters:
                adapter.set("Powered", state)

            self.adapter_state = state
        except Exception:
            logging.error("Exception occurred", exc_info=True)

    class Callback:
        def __init__(self, parent: "PowerManager", state: bool):
            self.parent = parent
            self.num_cb = 0
            self.called = 0
            self.state = state
            self.success = False
            self.timer = GLib.timeout_add(5000, self.timeout)

        def __call__(self, result: bool) -> None:
            self.called += 1

            if result:
                self.success = True

            self.check()

        def check(self) -> None:
            if self.called == self.num_cb:
                GLib.source_remove(self.timer)
                logging.info("callbacks done")
                self.parent.set_adapter_state(self.state)
                self.parent.update_power_state()
                self.parent.request_in_progress = False

        def timeout(self) -> bool:
            logging.info("Timeout reached while setting power state")
            self.parent.update_power_state()
            self.parent.request_in_progress = False
            return False

    def request_power_state(self, state: bool, force: bool = False) -> None:
        if self.current_state != state or force:
            if not self.request_in_progress:
                self.request_in_progress = True
                logging.info(f"Requesting {state}")
                cb = PowerManager.Callback(self, state)

                handlers = list(self.parent.Plugins.get_loaded_plugins(PowerStateHandler))
                for handler in handlers:
                    handler.on_power_state_change_requested(self, state, cb)
                cb.num_cb = len(handlers)
                cb.check()
            else:
                logging.info("Another request in progress")

    # queries other plugins to determine the current power state
    def update_power_state(self) -> None:
        rets = [plugin.on_power_state_query()
                for plugin in self.parent.Plugins.get_loaded_plugins(PowerStateHandler)]

        off = any(x != self.State.ON for x in rets) or not self.adapter_state
        foff = self.State.OFF_FORCED in rets
        on = self.State.ON in rets or self.adapter_state

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

        logging.info(f"off {off} | foff {foff} | on {on} | current state {self.current_state} | new state {new_state}")

        if self.current_state != new_state:
            logging.info(f"Signalling {new_state}")
            self.current_state = new_state

            self._emit_dbus_signal("BluetoothStatusChanged", new_state)
            for plugin in self.parent.Plugins.get_loaded_plugins(PowerStateListener):
                plugin.on_power_state_changed(self, new_state)

            if new_state:
                self.parent.Plugins.StatusIcon.set_text_line(0, _("Bluetooth Enabled"))
                self.parent.Plugins.StatusIcon.query_visibility(delay_hiding=True)
            else:
                self.parent.Plugins.StatusIcon.set_text_line(0, _("Bluetooth Disabled"))
                self.parent.Plugins.StatusIcon.query_visibility()
            self.parent.Plugins.StatusIcon.icon_should_change()

    def get_bluetooth_status(self) -> bool:
        return self.current_state

    def on_adapter_property_changed(self, _path: str, key: str, value: Any) -> None:
        if key == "Powered":
            if value and not self.current_state:
                logging.warning("adapter powered on while in off state, turning bluetooth on")
                self.request_power_state(True)

            self.adapter_state = self.get_adapter_state()
            self.update_power_state()

    def on_bluetooth_toggled(self) -> None:
        self.request_power_state(not self.current_state)

    def on_status_icon_query_icon(self) -> Optional[str]:
        return "blueman-disabled" if not self.get_bluetooth_status() else None

    def on_adapter_added(self, path: str) -> None:
        adapter = Adapter(obj_path=path)
        adapter.set("Powered", self.adapter_state)

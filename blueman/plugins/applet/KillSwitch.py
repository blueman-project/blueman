from blueman.Functions import dprint

from blueman.main.SignalTracker import SignalTracker
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.KillSwitchNG import KillSwitchNG, RFKillType


class KillSwitch(AppletPlugin):
    __author__ = "Walmis"
    __description__ = _(
        "Toggles a platform Bluetooth killswitch when Bluetooth power state changes. Useless with USB dongles.")
    __depends__ = ["PowerManager", "StatusIcon"]
    __icon__ = "system-shutdown"
    __options__ = {
        "checked": {"type": bool, "default": False}
    }

    def on_load(self, applet):
        self.signals = SignalTracker()

        self.Manager = KillSwitchNG()

        self.signals.Handle(self.Manager, "switch-changed", self.on_switch_changed)
        self.signals.Handle(self.Manager, "switch-added", self.on_switch_added)
        self.signals.Handle(self.Manager, "switch-removed", self.on_switch_removed)

    def on_switch_added(self, manager, switch):
        if switch.type == RFKillType.BLUETOOTH:
            dprint("killswitch registered", switch.idx)

    def on_switch_changed(self, manager, switch):
        if switch.type == RFKillType.BLUETOOTH:
            s = manager.GetGlobalState()
            dprint("Global state:", s, "\nswitch.soft:", switch.soft, "\nswitch.hard:", switch.hard)
            self.Applet.Plugins.PowerManager.UpdatePowerState()
            self.Applet.Plugins.StatusIcon.QueryVisibility()

    def on_switch_removed(self, manager, switch):
        if switch.type == RFKillType.BLUETOOTH:
            if len(manager.devices) == 0:
                self.Applet.Plugins.StatusIcon.QueryVisibility()

    def on_power_state_query(self, manager):
        if self.Manager.HardBlocked:
            return manager.STATE_OFF_FORCED
        else:
            dprint(self.Manager.GetGlobalState())
            if self.Manager.GetGlobalState():
                return manager.STATE_ON
            else:
                return manager.STATE_OFF

    def on_power_state_change_requested(self, manager, state, cb):
        dprint(state)

        def reply(*_):
            cb(True)

        def error(*_):
            cb(False)

        if not self.Manager.HardBlocked:
            self.Manager.SetGlobalState(state, reply_handler=reply, error_handler=error)
        else:
            cb(True)

    def on_unload(self):
        self.signals.DisconnectAll()

    def on_query_status_icon_visibility(self):
        if self.Manager.HardBlocked:
            return 1

        state = self.Manager.GetGlobalState()
        if state:
            if isinstance(self.Manager, KillSwitchNG) and len(self.Manager.devices) > 0 and self.Applet.Manager:
                return 2

            return 1  # StatusIcon.SHOW
        elif len(self.Manager.devices) > 0 and not state:
            #if killswitch removes the bluetooth adapter, dont hide the statusicon,
            #so that the user could turn bluetooth back on.
            return 2  # StatusIcon.FORCE_SHOW

        return 1

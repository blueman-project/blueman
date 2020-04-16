from gettext import gettext as _
import os
from typing import Dict

from gi.repository import GLib, Gio
import struct
import logging

from blueman.main.DBusProxies import Mechanism
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.applet.StatusIcon import StatusIcon


RFKILL_TYPE_BLUETOOTH = 2

RFKILL_OP_ADD = 0
RFKILL_OP_DEL = 1
RFKILL_OP_CHANGE = 2
RFKILL_OP_CHANGE_ALL = 3

RFKILL_EVENT_SIZE_V1 = 8

if not os.path.exists('/dev/rfkill'):
    raise ImportError('Hardware kill switch not found')


class Switch:
    def __init__(self, idx, switch_type, soft, hard):
        self.idx = idx
        self.type = switch_type
        self.soft = soft
        self.hard = hard


class KillSwitch(AppletPlugin):
    __author__ = "Walmis"
    __description__ = _("Switches Bluetooth killswitch status to match Bluetooth power state."
                        "Allows turning Bluetooth back on from an icon that shows its status; "
                        "provided it isn't unplugged by the system, or physically.")
    __depends__ = ["PowerManager", "StatusIcon"]
    __icon__ = "system-shutdown"

    __gsettings__ = {
        "schema": "org.blueman.plugins.killswitch",
        "path": None
    }
    __options__ = {
        "checked": {"type": bool, "default": False}
    }

    _switches: Dict[int, Switch] = {}
    _iom = None
    _enabled = True
    _hardblocked = False

    def on_load(self):
        self._connman_proxy = None
        self._connman_watch_id = Gio.bus_watch_name(Gio.BusType.SYSTEM, "net.connman", Gio.BusNameWatcherFlags.NONE,
                                                    self._on_connman_appeared, self._on_connman_vanished)

        channel = GLib.IOChannel.new_file("/dev/rfkill", "r")
        if channel is None:
            raise ImportError('Could not access RF kill switch')

        channel.set_encoding(None)

        self._iom = GLib.io_add_watch(channel, GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP, self.io_event)

    def on_unload(self):
        Gio.bus_unwatch_name(self._connman_watch_id)
        self._connman_proxy = None
        if self._iom:
            GLib.source_remove(self._iom)

    def _on_connman_appeared(self, connection, name, owner):
        logging.info(f"{name} appeared")
        self._connman_proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SYSTEM,
            Gio.DBusProxyFlags.DO_NOT_AUTO_START,
            None,
            'net.connman',
            '/net/connman/technology/bluetooth',
            'net.connman.Technology',
            None)

    def _on_connman_vanished(self, connection, name):
        logging.info(f"{name} vanished")
        self._connman_proxy = None

    def io_event(self, channel, condition):
        if condition & GLib.IO_ERR or condition & GLib.IO_HUP:
            return False

        data = channel.read(RFKILL_EVENT_SIZE_V1)
        if len(data) != RFKILL_EVENT_SIZE_V1:
            logging.warning("Bad rfkill event size")
            return True

        (idx, switch_type, op, soft, hard) = struct.unpack(str("IBBBB"), data)

        if switch_type != RFKILL_TYPE_BLUETOOTH:
            return True

        if op == RFKILL_OP_ADD:
            self._switches[idx] = Switch(idx, switch_type, soft, hard)
            logging.info(f"killswitch registered {idx}")
        elif op == RFKILL_OP_DEL:
            del self._switches[idx]
            logging.info(f"killswitch removed {idx}")
        elif op == RFKILL_OP_CHANGE and (self._switches[idx].soft != soft or self._switches[idx].hard != hard):
            self._switches[idx] = Switch(idx, switch_type, soft, hard)
            logging.info(f"killswitch changed {idx}")
        else:
            return True

        self._enabled = True
        self._hardblocked = False
        for s in self._switches.values():
            self._hardblocked |= s.hard
            self._enabled &= (s.soft == 0 and s.hard == 0)

        logging.info(f"State: {self._enabled}")

        self.parent.Plugins.StatusIcon.query_visibility(delay_hiding=not self._hardblocked)
        self.parent.Plugins.PowerManager.update_power_state()

        return True

    def on_power_state_query(self, manager):
        if self._hardblocked:
            return manager.STATE_OFF_FORCED
        elif self._enabled:
            return manager.STATE_ON
        else:
            return manager.STATE_OFF

    def on_power_state_change_requested(self, _, state, cb):
        logging.info(state)

        def reply(*_):
            cb(True)

        def error(*_):
            cb(False)

        if self._connman_proxy:
            logging.debug(f"Using connman to set state: {state}")
            self._connman_proxy.SetProperty('(sv)', 'Powered', GLib.Variant.new_boolean(state),
                                            result_handler=reply, error_handler=error)
        else:
            logging.debug(f"Using mechanism to set state: {state}")
            Mechanism().SetRfkillState('(b)', state, result_handler=reply, error_handler=error)

    def on_query_status_icon_visibility(self):
        # Force status icon to show if Bluetooth is soft-blocked
        if not self._hardblocked and not self._enabled:
            return StatusIcon.FORCE_SHOW

        return StatusIcon.SHOW

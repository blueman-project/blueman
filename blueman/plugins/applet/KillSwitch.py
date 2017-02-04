# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import weakref
from gi.repository import GLib
import struct
import logging

from blueman.main.Mechanism import Mechanism

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
    __description__ = _("Toggles a platform Bluetooth killswitch when Bluetooth power state changes (Useless with USB dongles) and makes sure a status icon is shown if there is a bluetooth killswitch but no adapter.")
    __depends__ = ["PowerManager", "StatusIcon"]
    __icon__ = "system-shutdown"

    __gsettings__ = {
        "schema": "org.blueman.plugins.killswitch",
        "path": None
    }
    __options__ = {
        "checked": {"type": bool, "default": False}
    }

    _switches = {}
    _iom = None
    _fd = None
    _enabled = True
    _hardblocked = False

    def on_load(self, applet):
        self._fd = os.open('/dev/rfkill', os.O_RDONLY | os.O_NONBLOCK)

        ref = weakref.ref(self)
        self._iom = GLib.io_add_watch(self._fd, GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP,
                                      lambda *args: ref() and ref().io_event(*args))

    def on_unload(self):
        if self._iom:
            GLib.source_remove(self._iom)
        if self._fd:
            os.close(self._fd)

    def io_event(self, _, condition):
        if condition & GLib.IO_ERR or condition & GLib.IO_HUP:
            return False

        data = os.read(self._fd, RFKILL_EVENT_SIZE_V1)
        if len(data) != RFKILL_EVENT_SIZE_V1:
            logging.warning("Bad rfkill event size")
            return True

        (idx, switch_type, op, soft, hard) = struct.unpack(str("IBBBB"), data)

        if switch_type != RFKILL_TYPE_BLUETOOTH:
            return True

        if op == RFKILL_OP_ADD:
            self._switches[idx] = Switch(idx, switch_type, soft, hard)
            logging.info("killswitch registered %s" % idx)
        elif op == RFKILL_OP_DEL:
            del self._switches[idx]
            logging.info("killswitch removed %s" % idx)
        elif op == RFKILL_OP_CHANGE and (self._switches[idx].soft != soft or self._switches[idx].hard != hard):
            self._switches[idx] = Switch(idx, switch_type, soft, hard)
            logging.info("killswitch changed %s" % idx)
        else:
            return True

        self._enabled = True
        self._hardblocked = False
        for s in self._switches.values():
            self._hardblocked |= s.hard
            self._enabled &= (s.soft == 0 and s.hard == 0)

        logging.info("State: %s" % self._enabled)

        self.Applet.Plugins.StatusIcon.QueryVisibility(delay_hiding=not self._hardblocked)
        self.Applet.Plugins.PowerManager.UpdatePowerState()

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

        Mechanism().SetRfkillState(str('(b)'), state, result_handler=reply, error_handler=error)

    def on_query_status_icon_visibility(self):
        # Force status icon to show if bluetooth is soft-blocked
        if not self._hardblocked and not self._enabled:
            return StatusIcon.FORCE_SHOW

        return StatusIcon.SHOW

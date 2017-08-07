# coding=utf-8
import logging

import blueman.bluez as bluez
from blueman.Functions import launch
from blueman.plugins.AppletPlugin import AppletPlugin

import gi
gi.require_version('GdkX11', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GdkX11

if not isinstance(Gdk.Screen.get_default(), GdkX11.X11Screen):
    raise ImportError('This is not an X11 screen')


class GameControllerWakelock(AppletPlugin):
    __description__ = _("Temporarily suspends the screensaver when a bluetooth game controller is connected.")
    __author__ = "bwRavencl"
    __icon__ = "input-gaming"

    def on_load(self):
        self.wake_lock = 0
        self.root_window_id = "0x%x" % Gdk.Screen.get_default().get_root_window().get_xid()

    def on_unload(self):
        if self.wake_lock:
            self.wake_lock = 1
            self.xdg_screensaver("resume")

    def on_device_property_changed(self, path, key, value):
        if key == "Connected":
            klass = bluez.Device(path)["Class"] & 0x1fff

            if klass == 0x504 or klass == 0x508:
                if value:
                    self.xdg_screensaver("suspend")
                else:
                    self.xdg_screensaver("resume")

    def xdg_screensaver(self, action):
        command = "xdg-screensaver %s %s" % (action, self.root_window_id)

        if action == "resume":
            if self.wake_lock <= 0:
                self.wake_lock = 0
            elif self.wake_lock > 1:
                self.wake_lock -= 1
            else:
                ret = launch(command, sn=False)
                if ret:
                    self.wake_lock -= 1
                else:
                    logging.error("%s failed" % action)

        elif action == "suspend":
            if self.wake_lock >= 1:
                self.wake_lock += 1
            else:
                ret = launch(command, sn=False)
                if ret:
                    self.wake_lock += 1
                else:
                    logging.error("%s failed" % action)

        logging.info("Number of locks: %s" % self.wake_lock)

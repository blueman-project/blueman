import blueman.bluez as bluez
from blueman.Functions import *
from blueman.main.SignalTracker import SignalTracker
from blueman.main.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import Gdk, GdkX11
import subprocess

class GameControllerWakelock(AppletPlugin):
    __description__ = _("Temporarily suspends the screensaver when a bluetooth game controller is connected.")
    __author__ = "bwRavencl"
    __icon__ = "input-gaming"

    def on_load(self, applet):
        self.wake_lock = 0
        self.root_window_id = "0x%x" % Gdk.Screen.get_default().get_root_window().get_xid()

        self.signals = SignalTracker()
        self.signals.Handle("bluez", bluez.Device(), self.on_device_property_changed, "PropertyChanged", path_keyword="path")
        
    def on_unload(self):
        if self.wake_lock:
            self.wake_lock = 1
            self.suspend_screensaver("resume")
        self.signals.DisconnectAll()

    def on_device_property_changed(self, key, value, path):
        if key == "Connected":
            klass = Device(path).get_properties()["Class"] & 0x1fff

            if klass == 0x504 or klass == 0x508:
                if value:
                    self.xdg_screensaver("suspend")
                else:
                    self.xdg_screensaver("resume")

    def xdg_screensaver(self, action):
        if action == "resume":
            if self.wake_lock == 0:
                pass
            elif self.wake_lock > 1:
                self.wake_lock -= 1
                pass
        elif action == "suspend" and self.wake_lock >= 1:
             self.wake_lock += 1
             pass

        command = ["xdg-screensaver", action, self.root_window_id]

        try:
            process = subprocess.Popen(command, stderr=subprocess.PIPE)
            _, stderr = process.communicate()

            if process.returncode != 0:
                dprint(" ".join(command) + " failed with: " + stderr)
                pass

            if action == "suspend":
                self.wake_lock += 1
            elif action == "resume":
                self.wake_lock = 0
        except:
            dprint(traceback.format_exc())

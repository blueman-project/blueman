from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.main.BluezConfig import BluezConfig
import os
from gi.repository import GObject


class Config(MechanismPlugin):
    def on_load(self):
        self.add_dbus_method(self.SetBluezConfig, in_signature="ssss", out_signature="", sender_keyword="caller")
        self.add_dbus_method(self.SaveBluezConfig, in_signature="s", out_signature="", sender_keyword="caller")
        self.add_dbus_method(self.RestartBluez, in_signature="", out_signature="", sender_keyword="caller")

        self.configs = {}

    def SetBluezConfig(self, file, section, key, value, caller):
        self.confirm_authorization(caller, "org.blueman.bluez.config")

        if file in self.configs:
            c = self.configs[file]
        else:
            c = self.configs[file] = BluezConfig(file)

        c.set(section, key, value)

    def SaveBluezConfig(self, file, caller):
        self.confirm_authorization(caller, "org.blueman.bluez.config")

        if file in self.configs:
            self.configs[file].write()
            del self.configs[file]

    def RestartBluez(self, caller):
        self.confirm_authorization(caller, "org.blueman.bluez.config")

        os.system("killall bluetoothd")
        GObject.timeout_add(1000, os.system, "bluetoothd")

from gi.repository import GObject, Gio
from operator import attrgetter
import os
from blueman.Functions import dprint

import blueman.plugins.config
from blueman.plugins.ConfigPlugin import ConfigPlugin

print("Loading configuration plugins")

path = os.path.dirname(blueman.plugins.config.__file__)
plugins = []
for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith(".py") and not (f.endswith(".pyc") or f.endswith("_.py")):
            plugins.append(f[0:-3])

for plugin in plugins:
    try:
        __import__("blueman.plugins.config.%s" % plugin, None, None, [])
    except ImportError as e:
        dprint("Skipping plugin %s\n%s" % (plugin, e))

class OldConfig(object):
    def __new__(c, section=""):
        classes = ConfigPlugin.__subclasses__()
        classes.sort(key=attrgetter("__priority__"))

        for cls in classes:
            try:
                inst = cls(section)
                print("Using %s config backend" % cls.__plugin__)
                return inst
            except Exception as e:
                print("Skipping plugin", cls.__plugin__)
                print(e)

            print("No suitable configuration backend found, exitting")
            exit(1)

class Config(Gio.Settings):
    def __init__(self, schema, path=None):
        Gio.Settings.__init__(self, schema, path)

    def bind_to_widget(self, key, widget, prop, flags=Gio.SettingsBindFlags.DEFAULT):
        self.bind(key, widget, prop, flags)

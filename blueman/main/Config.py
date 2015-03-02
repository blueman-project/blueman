from gi.repository import Gio

class Config(Gio.Settings):
    def __init__(self, schema, path=None):
        Gio.Settings.__init__(self, schema, path)

    def bind_to_widget(self, key, widget, prop, flags=Gio.SettingsBindFlags.DEFAULT):
        self.bind(key, widget, prop, flags)

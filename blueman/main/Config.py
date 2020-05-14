# coding=utf-8
from gi.repository import Gio
import logging


class Config(Gio.Settings):
    def __init__(self, schema_id, path=None):
        # Add backwards compat with pygobject < 3.11.2
        if Gio.Settings.__init__.__name__ == "new_init":
            super().__init__(schema_id=schema_id, path=path)
        else:
            super().__init__(schema=schema_id, path=path)

    def bind_to_widget(self, key, widget, prop, flags=Gio.SettingsBindFlags.DEFAULT):
        self.bind(key, widget, prop, flags)

    def __setitem__(self, key, value):
        if not self.is_writable(key):
            logging.error("GSetting not writable, settings not saved")
        super().__setitem__(key, value)

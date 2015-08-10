from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gio

class Config(Gio.Settings):
    def __init__(self, schema_id, path=None, **kwargs):
        Gio.Settings.__init__(self, schema=schema_id, path=path, **kwargs)

    def bind_to_widget(self, key, widget, prop, flags=Gio.SettingsBindFlags.DEFAULT):
        self.bind(key, widget, prop, flags)

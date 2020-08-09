from typing import Any, Optional

from gi.repository import Gio, GObject
import logging


class Config(Gio.Settings):
    def __init__(self, schema_id: str, path: Optional[str] = None) -> None:
        # Add backwards compat with pygobject < 3.11.2
        if Gio.Settings.__init__.__name__ == "new_init":
            super().__init__(schema_id=schema_id, path=path)
        else:
            super().__init__(schema=schema_id, path=path)

    def bind_to_widget(self, key: str, widget: GObject.Object, prop: str,
                       flags: Gio.SettingsBindFlags = Gio.SettingsBindFlags.DEFAULT) -> None:
        self.bind(key, widget, prop, flags)

    def __setitem__(self, key: str, value: Any) -> None:
        if not self.is_writable(key):
            logging.error("GSetting not writable, settings not saved")
        super().__setitem__(key, value)

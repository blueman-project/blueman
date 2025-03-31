from typing import TypeVar

import gi
from blueman.Constants import UI_PATH

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Builder(Gtk.Builder):
    def __init__(self, filename: str):
        super().__init__(translation_domain="blueman")
        self.add_from_file(UI_PATH.joinpath(filename).as_posix())

    T = TypeVar("T", bound=Gtk.Widget)

    def get_widget(self, name: str, widget_type: type[T]) -> T:
        widget = self.get_object(name)
        assert isinstance(widget, widget_type)
        return widget

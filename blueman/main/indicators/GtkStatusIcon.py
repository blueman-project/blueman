from typing import Callable, Iterable, TYPE_CHECKING, overload, Any, cast, Mapping, Optional

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from blueman.Functions import create_menuitem

if TYPE_CHECKING:
    from typing_extensions import Protocol

    from blueman.plugins.applet.Menu import MenuItemDict, SubmenuItemDict

    class MenuItemActivator(Protocol):
        @overload
        def __call__(self, idx: int) -> None:
            ...

        @overload
        def __call__(self, idx: int, subid: int) -> None:
            ...


@overload
def build_menu(items: Iterable["MenuItemDict"], activate: "MenuItemActivator") -> Gtk.Menu:
    ...


@overload
def build_menu(items: Iterable["SubmenuItemDict"], activate: Callable[[int], None]) -> Gtk.Menu:
    ...


def build_menu(items: Iterable[Mapping[str, Any]], activate: Callable[..., None]) -> Gtk.Menu:
    menu = Gtk.Menu()
    for index, item in enumerate(items):
        if 'text' in item and 'icon_name' in item:
            gtk_item: Gtk.MenuItem = create_menuitem(item['text'], item['icon_name'])
            label = gtk_item.get_child()
            assert isinstance(label, Gtk.Label)
            if item['markup']:
                label.set_markup_with_mnemonic(item['text'])
            else:
                label.set_text_with_mnemonic(item['text'])
            gtk_item.connect('activate', cast(Callable[[Gtk.MenuItem], None], lambda _, idx=index: activate(idx)))
            if 'submenu' in item:
                gtk_item.set_submenu(build_menu(item['submenu'], cast(Callable[[int], None],
                                                                      lambda subid, idx=index: activate(idx, subid))))
            if 'tooltip' in item:
                gtk_item.props.tooltip_text = item['tooltip']
            gtk_item.props.sensitive = item['sensitive']
        else:
            gtk_item = Gtk.SeparatorMenuItem()
        gtk_item.show()
        menu.append(gtk_item)
    return menu


class GtkStatusIcon:
    def __init__(self, icon_name: str, on_activate_menu_item: "MenuItemActivator",
                 on_activate_status_icon: Callable[[], None]) -> None:
        self._on_activate = on_activate_menu_item
        self.indicator = Gtk.StatusIcon(icon_name=icon_name)
        self.indicator.set_title('blueman')
        self.indicator.connect('popup-menu', self.on_popup_menu)
        self.indicator.connect('activate', lambda _status_icon: on_activate_status_icon())
        self._menu: Optional[Gtk.Menu] = None

    def on_popup_menu(self, _status_icon: Gtk.StatusIcon, _button: int, _activate_time: int) -> None:
        if self._menu:
            self._menu.popup_at_pointer(None)

    def set_icon(self, icon_name: str) -> None:
        self.indicator.props.icon_name = icon_name

    def set_text(self, text: str) -> None:
        self.indicator.props.tooltip_markup = text

    def set_visibility(self, visible: bool) -> None:
        self.indicator.props.visible = visible

    def set_menu(self, menu: Iterable["MenuItemDict"]) -> None:
        self._menu = build_menu(menu, self._on_activate)

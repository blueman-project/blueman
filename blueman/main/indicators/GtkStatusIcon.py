from typing import Callable, Iterable, TYPE_CHECKING, overload, cast, Optional, Tuple

import gi

from blueman.main.Tray import BluemanTray
from blueman.main.indicators.IndicatorInterface import IndicatorInterface

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from blueman.Functions import create_menuitem

if TYPE_CHECKING:
    from typing_extensions import Protocol

    from blueman.plugins.applet.Menu import MenuItemDict, SubmenuItemDict

    class MenuItemActivator(Protocol):
        def __call__(self, *idx: int) -> None:
            ...


@overload
def build_menu(items: Iterable[Tuple[int, "MenuItemDict"]], activate: "MenuItemActivator") -> Gtk.Menu:
    ...


@overload
def build_menu(items: Iterable[Tuple[int, "SubmenuItemDict"]], activate: Callable[[int], None]) -> Gtk.Menu:
    ...


def build_menu(items: Iterable[Tuple[int, "SubmenuItemDict"]], activate: Callable[..., None]) -> Gtk.Menu:
    menu = Gtk.Menu()
    for index, item in items:
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
                gtk_item.set_submenu(
                    build_menu(enumerate(item['submenu']),  # type: ignore
                               cast(Callable[[int], None], lambda subid, idx=index: activate(idx, subid))))
            if 'tooltip' in item:
                gtk_item.props.tooltip_text = item['tooltip']
            gtk_item.props.sensitive = item['sensitive']
        else:
            gtk_item = Gtk.SeparatorMenuItem()
        gtk_item.show()
        menu.append(gtk_item)
    return menu


class GtkStatusIcon(IndicatorInterface):
    def __init__(self, tray: BluemanTray, icon_name: str) -> None:
        self._on_activate = tray.activate_menu_item
        self.indicator = Gtk.StatusIcon(icon_name=icon_name)
        self.indicator.set_title('blueman')
        self.indicator.connect('popup-menu', self.on_popup_menu)
        self.indicator.connect('activate', lambda _status_icon: tray.activate_status_icon())
        self._tooltip_title = ""
        self._tooltip_text = ""
        self._menu: Optional[Gtk.Menu] = None

    def on_popup_menu(self, _status_icon: Gtk.StatusIcon, _button: int, _activate_time: int) -> None:
        if self._menu:
            self._menu.popup_at_pointer(None)

    def set_icon(self, icon_name: str) -> None:
        self.indicator.props.icon_name = icon_name

    def set_tooltip_title(self, title: str) -> None:
        self._tooltip_title = title
        self._update_tooltip()

    def set_tooltip_text(self, text: str) -> None:
        self._tooltip_text = text
        self._update_tooltip()

    def _update_tooltip(self) -> None:
        text = self._tooltip_title
        if self._tooltip_text:
            text += "\n" + self._tooltip_text
        self.indicator.props.tooltip_markup = text

    def set_visibility(self, visible: bool) -> None:
        self.indicator.props.visible = visible

    def set_menu(self, menu: Iterable["MenuItemDict"]) -> None:
        self._menu = build_menu(((item["id"], item) for item in menu), self._on_activate)

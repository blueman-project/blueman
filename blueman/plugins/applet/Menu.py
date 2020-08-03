from gettext import gettext as _
from typing import List, Union, Iterable, Dict, Optional, Callable, \
    TYPE_CHECKING, Tuple, Iterator, Mapping, Sequence

from gi.repository import GLib

from blueman.plugins.AppletPlugin import AppletPlugin
from operator import attrgetter

if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class SubmenuItemDict(TypedDict):
        text: str
        markup: bool
        icon_name: str
        sensitive: bool
        tooltip: Optional[str]
        callback: Callable[[], None]

    class MenuItemDict(SubmenuItemDict, total=False):
        submenu: Iterable["SubmenuItemDict"]


class MenuItem:
    def __init__(self, menu_plugin: "Menu", owner: AppletPlugin, priority: int, text: Optional[str], markup: bool,
                 icon_name: Optional[str], tooltip: Optional[str], callback: Optional[Callable[[], None]],
                 submenu_function: Optional[Callable[[], Iterable["SubmenuItemDict"]]], visible: bool, sensitive: bool):
        self._menu_plugin = menu_plugin
        self._owner = owner
        self._priority = priority
        self._text = text
        self._markup = markup
        self._icon_name = icon_name
        self._tooltip = tooltip
        self._callback = callback
        self._submenu_function = submenu_function
        self._visible = visible
        self._sensitive = sensitive

        assert text and icon_name and (callback or submenu_function) or \
            not any([text, icon_name, tooltip, callback, submenu_function])

    @property
    def owner(self) -> AppletPlugin:
        return self._owner

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def callback(self) -> Optional[Callable[[], None]]:
        return self._callback

    @property
    def visible(self) -> bool:
        return self._visible

    def _iter_base(self) -> Iterator[Tuple[str, Union[str, bool]]]:
        for key in ['text', 'markup', 'icon_name', 'tooltip', 'sensitive']:
            value = getattr(self, '_' + key)
            if value is not None:
                yield key, value

    def __iter__(self) -> Iterator[Tuple[str, Union[str, bool, List[Dict[str, Union[str, bool]]]]]]:
        yield from self._iter_base()
        submenu = list(self.submenu_items)
        if submenu:
            yield 'submenu', [dict(item) for item in submenu]

    @property
    def submenu_items(self) -> Iterable["SubmenuItem"]:
        if not self._submenu_function:
            return
        submenu_items = self._submenu_function()
        if not submenu_items:
            return
        for item in submenu_items:
            assert not set(item.keys()) - {'text', 'markup', 'icon_name', 'tooltip', 'callback', 'sensitive'}
            yield SubmenuItem(self._menu_plugin, self._owner, 0, item.get('text'), item.get('markup', False),
                              item.get('icon_name'), item.get('tooltip'), item.get('callback'), None, True,
                              item.get('sensitive', True))

    def set_text(self, text: str, markup: bool = False) -> None:
        self._text = text
        self._markup = markup
        self._menu_plugin.on_menu_changed()

    def set_icon_name(self, icon_name: str) -> None:
        self._icon_name = icon_name
        self._menu_plugin.on_menu_changed()

    def set_tooltip(self, tooltip: str) -> None:
        self._tooltip = tooltip
        self._menu_plugin.on_menu_changed()

    def set_visible(self, visible: bool) -> None:
        self._visible = visible
        self._menu_plugin.on_menu_changed()

    def set_sensitive(self, sensitive: bool) -> None:
        self._sensitive = sensitive
        self._menu_plugin.on_menu_changed()


class SubmenuItem(MenuItem):
    def __iter__(self) -> Iterator[Tuple[str, Union[str, bool]]]:
        yield from self._iter_base()


class Menu(AppletPlugin):
    __description__ = _("Provides a menu for the applet and an API for other plugins to manipulate it")
    __icon__ = "menu-editor"
    __author__ = "Walmis"
    __unloadable__ = False

    def on_load(self) -> None:
        self.__plugins_loaded = False

        self.__menuitems: List[MenuItem] = []

        self._add_dbus_signal("MenuChanged", "aa{sv}")
        self._add_dbus_method("GetMenu", (), "aa{sv}", self._get_menu)
        self._add_dbus_method("ActivateMenuItem", ("ai",), "", self._activate_menu_item)

    def __sort(self) -> None:
        self.__menuitems.sort(key=attrgetter('priority'))

    def add(self, owner: AppletPlugin, priority: int, text: Optional[str] = None, markup: bool = False,
            icon_name: Optional[str] = None, tooltip: Optional[str] = None,
            callback: Optional[Callable[[], None]] = None,
            submenu_function: Optional[Callable[[], Iterable["SubmenuItemDict"]]] = None,
            visible: bool = True, sensitive: bool = True) -> MenuItem:
        item = MenuItem(self, owner, priority, text, markup, icon_name, tooltip, callback, submenu_function, visible,
                        sensitive)
        self.__menuitems.append(item)
        if self.__plugins_loaded:
            self.__sort()
        self.on_menu_changed()
        return item

    def unregister(self, owner: AppletPlugin) -> None:
        for item in reversed(self.__menuitems):
            if item.owner == owner:
                self.__menuitems.remove(item)
        self.on_menu_changed()

    def on_plugins_loaded(self) -> None:
        self.__plugins_loaded = True
        self.__sort()

    def on_menu_changed(self) -> None:
        self._emit_dbus_signal("MenuChanged", self._get_menu())

    def _get_menu(self) -> List[Dict[str, GLib.Variant]]:
        return self._prepare_menu(dict(item) for item in self.__menuitems if item.visible)

    def _prepare_menu(self, data: Iterable[Mapping[str, Union[str, bool, Iterable[Mapping[str, Union[str, bool]]]]]]) \
            -> List[Dict[str, GLib.Variant]]:
        return [{k: self._build_variant(v) for k, v in item.items()} for item in data]

    def _build_variant(self, value: Union[str, bool, Iterable[Mapping[str, Union[str, bool]]]]) -> GLib.Variant:
        if isinstance(value, str):
            return GLib.Variant("s", value)
        if isinstance(value, bool):
            return GLib.Variant("b", value)
        return GLib.Variant("aa{sv}", self._prepare_menu(value))

    def _activate_menu_item(self, indexes: Sequence[int]) -> None:
        node = [item for item in self.__menuitems if item.visible][indexes[0]]
        for index in list(indexes)[1:]:
            node = [item for item in node.submenu_items if item.visible][index]
        if node.callback:
            node.callback()

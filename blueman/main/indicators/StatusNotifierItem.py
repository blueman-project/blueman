from typing import Iterable, TYPE_CHECKING, Callable, List, Tuple, Dict, Union, TypeVar

from gi.repository import Gio, GLib, Pango

from blueman.main.DbusService import DbusService
from blueman.main.indicators.IndicatorInterface import IndicatorInterface, IndicatorNotAvailable

if TYPE_CHECKING:
    from blueman.plugins.applet.Menu import MenuItemDict, SubmenuItemDict
    from blueman.main.indicators.GtkStatusIcon import MenuItemActivator


class MenuService(DbusService):
    def __init__(self, on_activate_menu_item: "MenuItemActivator") -> None:
        super().__init__(None, "com.canonical.dbusmenu", "/org/blueman/sni/menu", Gio.BusType.SESSION)
        self._items: List["MenuItemDict"] = []
        self._revision = 0
        self._on_activate = on_activate_menu_item

        self.add_method("GetLayout", ("i", "i", "as"), ("u", "(ia{sv}av)"), self._get_layout)
        self.add_method("Event", ("i", "s", "v", "u"), (), self._on_event)

        self.add_method("GetGroupProperties", ("ai", "as"), ("a(ia{sv})",),
                        lambda ids, props: [(idx, self._render_item(item)) for idx, item in self._iterate_items()
                                            if idx in ids])

        self.add_signal("LayoutUpdated", ("u", "i"))

    def set_items(self, items: Iterable["MenuItemDict"]) -> None:
        self._items = list(items)
        self._revision += 1
        self.emit_signal("LayoutUpdated", self._revision, 0)

    def _get_layout(self, parent_id: int, _recursion_depth: int, _property_names: List[str]
                    ) -> Tuple[int, Tuple[int, Dict[str, GLib.Variant], List[GLib.Variant]]]:
        if parent_id == 0:
            return self._revision, (0, {}, self._render_menu(self._items, 1, self._render_submenu))
        else:
            return self._revision, (parent_id, self._render_item(self._items[parent_id - 1]), [])

    def _render_submenu(self, item: "MenuItemDict", idx: int) -> List[GLib.Variant]:
        if "submenu" in item:
            return self._render_menu(item["submenu"], idx * 100 + 1, lambda _item, _isx: [])
        else:
            return []

    _T = TypeVar("_T", bound="SubmenuItemDict")

    def _render_menu(self, items: Iterable[_T], start: int, submenu_callback: Callable[[_T, int], List[GLib.Variant]]
                     ) -> List[GLib.Variant]:
        return [GLib.Variant("(ia{sv}av)", (idx, self._render_item(item), submenu_callback(item, idx)))
                for idx, item in enumerate(items, start)]

    def _iterate_items(self) -> Iterable[Tuple[int, "SubmenuItemDict"]]:
        for idx, item in enumerate(self._items, 1):
            yield idx, item
            if "submenu" in item:
                yield from enumerate(item["submenu"], idx * 100 + 1)

    def _render_item(self, item: Union["MenuItemDict", "SubmenuItemDict"]) -> Dict[str, GLib.Variant]:
        if "text" in item and "icon_name" in item:
            label = Pango.parse_markup(item["text"], -1, "\0")[2] if item.get("markup", False) else item["text"]
            props = {
                "label": GLib.Variant("s", label),
                "icon-name": GLib.Variant("s", item["icon_name"]),
                "enabled": GLib.Variant("b", item["sensitive"]),
            }
            if "submenu" in item:
                props["children-display"] = GLib.Variant("s", "submenu")
            return props
        else:
            return {"type": GLib.Variant("s", "separator")}

    def _on_event(self, idx: int, event_id: str, _data: GLib.Variant, _timestamp: int) -> None:
        if event_id == "clicked":
            if idx < 100:
                self._on_activate(idx - 1)
            else:
                self._on_activate(int(idx / 100) - 1, idx % 100 - 1)


class StatusNotifierItemService(DbusService):
    Category = "Hardware"
    Id = "blueman"
    Title = "blueman"

    def __init__(self, icon_name: str, on_activate_status_icon: Callable[[], None],
                 on_activate_menu_item: "MenuItemActivator") -> None:
        super().__init__(None, "org.kde.StatusNotifierItem", "/org/blueman/sni", Gio.BusType.SESSION,
                         {"Category": "s", "Id": "s", "IconName": "s", "Status": "s", "Title": "s",
                          "ToolTip": "(sa(iiay)ss)", "Menu": "o"})
        self.add_method("Activate", ("i", "i"), "", lambda x, y: on_activate_status_icon())

        self.menu = MenuService(on_activate_menu_item)

        self.IconName = icon_name
        self.Status = "Active"
        self.ToolTip: Tuple[str, List[Tuple[int, int, List[int]]], str, str] = ("", [], "", "")
        self.Menu = "/org/blueman/sni/menu"

        self.add_signal("NewIcon", "")
        self.add_signal("NewStatus", "")
        self.add_signal("NewToolTip", "")

    def register(self) -> None:
        self.menu.register()
        super().register()

    def unregister(self) -> None:
        super().unregister()
        self.menu.unregister()


class StatusNotifierItem(IndicatorInterface):
    def __init__(self, icon_name: str, on_activate_menu_item: "MenuItemActivator",
                 on_activate_status_icon: Callable[[], None]) -> None:
        self._sni = StatusNotifierItemService(icon_name, on_activate_status_icon, on_activate_menu_item)
        self._sni.register()

        self._bus = Gio.bus_get_sync(Gio.BusType.SESSION)

        try:
            Gio.bus_get_sync(Gio.BusType.SESSION).call_sync(
                "org.kde.StatusNotifierWatcher", "/StatusNotifierWatcher", "org.kde.StatusNotifierWatcher",
                "RegisterStatusNotifierItem", GLib.Variant("(s)", ("/org/blueman/sni",)),
                None, Gio.DBusCallFlags.NONE, -1)
        except GLib.Error:
            raise IndicatorNotAvailable

    def set_icon(self, icon_name: str) -> None:
        self._sni.IconName = icon_name
        self._sni.emit_signal("NewIcon")

    def set_tooltip_title(self, title: str) -> None:
        self._sni.ToolTip = ("", [], title, self._sni.ToolTip[3])
        self._sni.emit_signal("NewToolTip")

    def set_tooltip_text(self, text: str) -> None:
        self._sni.ToolTip = ("", [], self._sni.ToolTip[2], text)
        self._sni.emit_signal("NewToolTip")

    def set_visibility(self, visible: bool) -> None:
        self._sni.Status = "Active" if visible else "Passive"
        self._sni.emit_signal("NewStatus")

    def set_menu(self, menu: Iterable["MenuItemDict"]) -> None:
        self._sni.menu.set_items(menu)

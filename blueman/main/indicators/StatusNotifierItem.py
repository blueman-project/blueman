from collections import OrderedDict
from typing import Iterable, TYPE_CHECKING, Callable, List, Tuple, Dict, Union, TypeVar, Any

from gi.repository import Gio, GLib, Pango

from blueman.main.DbusService import DbusService
from blueman.main.Tray import BluemanTray
from blueman.main.indicators.IndicatorInterface import IndicatorInterface, IndicatorNotAvailable

if TYPE_CHECKING:
    from blueman.plugins.applet.Menu import MenuItemDict, SubmenuItemDict
    from blueman.main.indicators.GtkStatusIcon import MenuItemActivator


class MenuService(DbusService):
    def __init__(self, on_activate_menu_item: "MenuItemActivator") -> None:
        super().__init__(None, "com.canonical.dbusmenu", "/org/blueman/sni/menu", Gio.BusType.SESSION)
        self._items: OrderedDict[int, "MenuItemDict"] = OrderedDict()
        self._revision = 0
        self._revision_advertised = -1
        self._on_activate = on_activate_menu_item

        self.add_method("GetLayout", ("i", "i", "as"), ("u", "(ia{sv}av)"), self._get_layout)
        self.add_method("Event", ("i", "s", "v", "u"), (), self._on_event)
        self.add_method("AboutToShow", ("i",), ("b",), lambda _: self._revision > self._revision_advertised)

        self.add_method("GetGroupProperties", ("ai", "as"), ("a(ia{sv})",),
                        lambda ids, props: [(idx, self._render_item(item)) for idx, item in self._iterate_items()
                                            if idx in ids])

        self.add_signal("LayoutUpdated", ("u", "i"))

        GLib.timeout_add(100, self._advertise_revision)

    def set_items(self, items: Iterable["MenuItemDict"]) -> None:
        self._items = OrderedDict((item["id"], item) for item in items)
        self._revision += 1

    def _advertise_revision(self) -> bool:
        if self._revision != self._revision_advertised:
            self.emit_signal("LayoutUpdated", self._revision, 0)
            self._revision_advertised = self._revision
        return True

    def _get_layout(self, parent_id: int, _recursion_depth: int, _property_names: List[str]
                    ) -> Tuple[int, Tuple[int, Dict[str, GLib.Variant], List[GLib.Variant]]]:
        if parent_id == 0:
            return self._revision, (0, {}, self._render_menu(((item["id"] << 8, item) for item in self._items.values()),
                                                             self._render_submenu))
        else:
            item = self._items[parent_id >> 8]
            if "submenu" in item and _recursion_depth != 0:
                return self._revision, (parent_id, self._render_item(item), self._render_submenu(item, parent_id))
            return self._revision, (parent_id, self._render_item(item), [])

    def _render_submenu(self, item: "MenuItemDict", idx: int) -> List[GLib.Variant]:
        if "submenu" in item:
            return self._render_menu(enumerate(item["submenu"], idx + 1), lambda _item, _isx: [])
        else:
            return []

    _T = TypeVar("_T", bound="SubmenuItemDict")

    def _render_menu(self, items: Iterable[Tuple[int, _T]], submenu_callback: Callable[[_T, int], List[GLib.Variant]]
                     ) -> List[GLib.Variant]:
        return [GLib.Variant("(ia{sv}av)", (idx, self._render_item(item), submenu_callback(item, idx)))
                for (idx, item) in items]

    def _iterate_items(self) -> Iterable[Tuple[int, "SubmenuItemDict"]]:
        for item in self._items.values():
            yield item["id"] << 8, item
            if "submenu" in item:
                yield from enumerate(item["submenu"], (item["id"] << 8) + 1)

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
            if idx % (1 << 8) == 0:
                self._on_activate(idx >> 8)
            else:
                self._on_activate(idx >> 8, idx % (1 << 8) - 1)


class StatusNotifierItemService(DbusService):
    Category = "Hardware"
    Id = "blueman"
    Title = "blueman"
    ItemIsMenu = False

    def __init__(self, tray: BluemanTray, icon_name: str) -> None:
        super().__init__(None, "org.kde.StatusNotifierItem", "/org/blueman/sni", Gio.BusType.SESSION,
                         {"Category": "s", "Id": "s", "IconName": "s", "Status": "s", "Title": "s",
                          "ToolTip": "(sa(iiay)ss)", "Menu": "o", "ItemIsMenu": "b"})
        self.add_method("Activate", ("i", "i"), "", lambda x, y: tray.activate_status_icon())

        self.menu = MenuService(tray.activate_menu_item)

        self.IconName = icon_name
        self.Status = "Active"
        self.ToolTip: Tuple[str, List[Tuple[int, int, List[int]]], str, str] = ("", [], "", "")
        self.Menu = "/org/blueman/sni/menu"

        self.add_signal("NewIcon", "")
        self.add_signal("NewStatus", "s")
        self.add_signal("NewToolTip", "")

    def register(self) -> None:
        self.menu.register()
        super().register()

    def unregister(self) -> None:
        super().unregister()
        self.menu.unregister()


class StatusNotifierItem(IndicatorInterface):
    _SNI_BUS_NAME = _SNI_INTERFACE_NAME = "org.kde.StatusNotifierWatcher"

    def __init__(self, tray: BluemanTray, icon_name: str) -> None:
        self._sni = StatusNotifierItemService(tray, icon_name)
        self._sni.register()

        self._bus = Gio.bus_get_sync(Gio.BusType.SESSION)

        watcher_expected: bool

        def on_watcher_appeared(*args: Any) -> None:
            nonlocal watcher_expected

            if watcher_expected:
                watcher_expected = False
            else:
                tray.activate()

        Gio.bus_watch_name(Gio.BusType.SESSION, self._SNI_BUS_NAME, Gio.BusNameWatcherFlags.NONE,
                           on_watcher_appeared, None)

        try:
            Gio.bus_get_sync(Gio.BusType.SESSION).call_sync(
                self._SNI_BUS_NAME, "/StatusNotifierWatcher", self._SNI_INTERFACE_NAME,
                "RegisterStatusNotifierItem", GLib.Variant("(s)", ("/org/blueman/sni",)),
                None, Gio.DBusCallFlags.NONE, -1)
            watcher_expected = True
        except GLib.Error:
            watcher_expected = False
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
        self._sni.Status = status = "Active" if visible else "Passive"
        self._sni.emit_signal("NewStatus", status)

    def set_menu(self, menu: Iterable["MenuItemDict"]) -> None:
        self._sni.menu.set_items(menu)

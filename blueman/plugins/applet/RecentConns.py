from gettext import gettext as _
from operator import itemgetter
import time
import logging
from typing import Dict, List, TYPE_CHECKING, Optional, Callable, cast, Union

from blueman.bluez.Device import Device
from blueman.bluez.errors import DBusNoSuchAdapterError
from blueman.gui.Notification import Notification
from blueman.Sdp import ServiceUUID
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.applet.PowerManager import PowerManager, PowerStateListener

if TYPE_CHECKING:
    from blueman.plugins.applet.Menu import MenuItemDict

    from typing_extensions import TypedDict

    class _ItemBase(TypedDict):
        adapter: str
        address: str
        alias: str
        icon: str
        name: str
        uuid: str

    class Item(_ItemBase):
        time: float
        device: Optional[str]
        mitem: Optional[MenuItemDict]

    class StoredIcon(_ItemBase):
        time: str

REGISTRY_VERSION = 0


class RecentConns(AppletPlugin, PowerStateListener):
    __depends__ = ["DBusService", "Menu"]
    __icon__ = "document-open-recent"
    __description__ = _("Provides a menu item that contains last used connections for quick access")
    __author__ = "Walmis"

    __gsettings__ = {
        "schema": "org.blueman.plugins.recentconns",
        "path": None
    }
    __options__ = {
        "max-items": {"type": int,
                      "default": 6,
                      # the maximum number of items RecentConns menu will display
                      "name": _("Maximum items"),
                      "desc": _("The maximum number of items recent connections menu will display."),
                      "range": (6, 20)},
        "recent-connections": {"type": list, "default": "[]"}
    }

    _items = None

    def on_load(self) -> None:
        self._adapters: Dict[str, str] = {}
        self.__menuitems: List["MenuItemDict"] = []

        self.item = self.parent.Plugins.Menu.add(self, 52, text=_("Recent _Connections") + "…",
                                                 icon_name="document-open-recent", submenu_function=self.get_menu)
        self.parent.Plugins.Menu.add(self, 53)

        self.deferred = False

    def _store_state(self) -> None:
        self.set_option("recent-connections", [
            {
                "adapter": item["adapter"],
                "address": item["address"],
                "alias": item["alias"],
                "icon": item["icon"],
                "name": item["name"],
                "uuid": item["uuid"],
                "time": str(item["time"]),
            } for item in self.items
        ])

    def change_sensitivity(self, sensitive: bool) -> None:
        if 'PowerManager' in self.parent.Plugins.get_loaded():
            power = self.parent.Plugins.PowerManager.get_bluetooth_status()
        else:
            power = True

        sensitive = sensitive and \
            self.parent.Manager is not None and \
            power and \
            self.items is not None and \
            (len(self.items) > 0)

        self.item.set_sensitive(sensitive)

    def on_power_state_changed(self, manager: PowerManager, state: bool) -> None:
        self.change_sensitivity(state)
        if state and self.deferred:
            self.deferred = False
            self.on_manager_state_changed(state)

    def on_unload(self) -> None:
        self.parent.Plugins.Menu.unregister(self)

    def initialize(self) -> None:
        logging.info("rebuilding menu")

        self.__menuitems = []
        self.parent.Plugins.Menu.on_menu_changed()

        self.items.sort(key=itemgetter("time"), reverse=True)

        self._items = self.items[0:self.get_option("max-items")]
        self.items.reverse()

        if len(self.items) == 0:
            self.change_sensitivity(False)
        else:
            self.change_sensitivity(True)

        count = 0
        for item in self.items:
            if count < self.get_option("max-items"):
                self.add_item(item)
                count += 1

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            if 'PowerManager' in self.parent.Plugins.get_loaded():
                if not self.parent.Plugins.PowerManager.get_bluetooth_status():
                    self.deferred = True
                    self.item.set_sensitive(False)
                    return

            self.item.set_sensitive(True)
            adapters = self.parent.Manager.get_adapters()

            self._adapters = {adapter.get_object_path(): adapter["Address"]
                              for adapter in adapters}

            for i in self.items:
                device_path = self._get_device_path(i["adapter"], i["address"])
                if device_path:
                    i["device"] = device_path

            self.initialize()
        else:
            self.item.set_sensitive(False)
            return

        self.change_sensitivity(state)

    def on_device_created(self, path: str) -> None:
        self._items = None
        self.initialize()

    def on_device_removed(self, path: str) -> None:
        for item in reversed(self.items):
            if item['device'] == path:
                self.items.remove(item)
                self.initialize()

    def on_adapter_added(self, path: str) -> None:
        a = self.parent.Manager.get_adapter(path)
        self._adapters[path] = a["Address"]
        self.initialize()

    def on_adapter_removed(self, path: str) -> None:
        if path in self._adapters:
            del self._adapters[path]
        else:
            logging.warning("Adapter not found in list")

        self.initialize()

    def notify(self, object_path: str, uuid: str) -> None:
        device = Device(obj_path=object_path)
        logging.info(f"{device} {uuid}")
        try:
            adapter = self.parent.Manager.get_adapter(device['Adapter'])
        except DBusNoSuchAdapterError:
            logging.warning("adapter not found")
            return

        item: "Item" = {
            "adapter": adapter["Address"],
            "address": device['Address'],
            "alias": device['Alias'],
            "icon": device['Icon'],
            "name": ServiceUUID(uuid).name,
            "uuid": uuid,
            "time": time.time(),
            "device": object_path,
            "mitem": None
        }

        for i in self.items:
            if i["adapter"] == item["adapter"] and \
                    i["address"] == item["address"] and \
                    i["uuid"] == item["uuid"]:
                i["time"] = item["time"]

                i["device"] = item["device"]
                self.initialize()
                return

        self.items.append(item)
        self.initialize()

        self._store_state()

    def on_item_activated(self, item: "Item") -> None:
        logging.info(f"Connect {item['address']} {item['uuid']}")

        assert item["mitem"] is not None

        item["mitem"]["sensitive"] = False
        self.parent.Plugins.Menu.on_menu_changed()

        def reply() -> None:
            assert item["mitem"] is not None  # https://github.com/python/mypy/issues/2608
            Notification(_("Connected"), _("Connected to %s") % item["mitem"]["text"],
                         icon_name=item["icon"]).show()
            item["mitem"]["sensitive"] = True
            self.parent.Plugins.Menu.on_menu_changed()

        def err(reason: Union[Exception, str]) -> None:
            Notification(_("Failed to connect"), str(reason).split(": ")[-1],
                         icon_name="dialog-error").show()
            assert item["mitem"] is not None  # https://github.com/python/mypy/issues/2608
            item["mitem"]["sensitive"] = True
            self.parent.Plugins.Menu.on_menu_changed()

        self.parent.Plugins.DBusService.connect_service(item["device"], item["uuid"], reply, err)

    def add_item(self, item: "Item") -> None:
        if item["adapter"] not in self._adapters.values():
            item["device"] = None
        elif not item["device"] and item["adapter"] in self._adapters.values():
            device = self._get_device_path(item["adapter"], (item["address"]))
            if device is not None:
                item["device"] = device
            else:
                self.items.remove(item)
                self.initialize()

        mitem: "MenuItemDict" = {
            "text": _("%(service)s on %(device)s") % {"service": item["name"], "device": item["alias"]},
            "markup": True,
            "icon_name": item["mitem"]["icon_name"] if item["mitem"] is not None else item["icon"],
            "sensitive": item["device"] is not None,
            "tooltip": None if item["device"] is None else _("Adapter for this connection is not available"),
            "callback": (item["mitem"]["callback"] if item["mitem"] is not None
                         else cast(Callable[[], None], lambda itm=item: self.on_item_activated(itm)))
        }

        item["mitem"] = mitem

        self.__menuitems.append(mitem)
        self.parent.Plugins.Menu.on_menu_changed()

    def get_menu(self) -> List["MenuItemDict"]:
        return self.__menuitems

    def _get_device_path(self, adapter_path: str, address: str) -> Optional[str]:
        try:
            adapter = self.parent.Manager.get_adapter(adapter_path)
        except DBusNoSuchAdapterError:
            return None

        device = self.parent.Manager.find_device(address, adapter.get_object_path())
        return device.get_object_path() if device is not None else None

    @property
    def items(self) -> List["Item"]:
        if self._items is not None:
            return self._items

        items = self.get_option("recent-connections")

        if not items:
            self._items = []
            return self._items

        self._items = [
            {
                "adapter": i["adapter"],
                "address": i["address"],
                "alias": i["alias"],
                "icon": i["icon"],
                "name": i["name"],
                "uuid": i["uuid"],
                "time": float(i["time"]),
                "device": (self._get_device_path(i["adapter"], i["address"])
                           if i["adapter"] in self._adapters.values() else None),
                "mitem": None
            }
            for i in items
            if i["adapter"] not in self._adapters.values() or self._get_device_path(i["adapter"], i["address"])
        ]

        return self._items

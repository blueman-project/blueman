from gettext import gettext as _
from operator import itemgetter
import time
import logging
from typing import List, TYPE_CHECKING, Optional, Callable, cast, Union

from blueman.bluez.Device import Device
from blueman.bluez.errors import DBusNoSuchAdapterError
from blueman.gui.Notification import Notification
from blueman.Sdp import ServiceUUID
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.applet.PowerManager import PowerManager, PowerStateListener

if TYPE_CHECKING:
    from blueman.plugins.applet.Menu import SubmenuItemDict

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
        mitem: Optional[SubmenuItemDict]

    class StoredIcon(_ItemBase):
        time: str

REGISTRY_VERSION = 0


class RecentConns(AppletPlugin, PowerStateListener):
    __depends__ = ["DBusService", "Menu"]
    __icon__ = "document-open-recent-symbolic"
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
        self.__menuitems: List["SubmenuItemDict"] = []

        self._item = self.parent.Plugins.Menu.add(self, 52, text=_("Recent _Connections") + "…",
                                                  icon_name="document-open-recent-symbolic",
                                                  submenu_function=self.get_menu)
        self.parent.Plugins.Menu.add(self, 53)

    def on_power_state_changed(self, manager: PowerManager, state: bool) -> None:
        self._rebuild()

    def on_unload(self) -> None:
        self.parent.Plugins.Menu.unregister(self)

    def _rebuild(self) -> None:
        if 'PowerManager' in self.parent.Plugins.get_loaded() and \
                not self.parent.Plugins.PowerManager.get_bluetooth_status():
            self._item.set_sensitive(False)
            return

        self._items = self._get_items()

        if len(self._items) == 0:
            self._item.set_sensitive(False)
            return

        self._item.set_sensitive(True)

        self.__menuitems = [self._build_menu_item(item) for item in self._items[:self.get_option("max-items")]]

        self.parent.Plugins.Menu.on_menu_changed()

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            self._rebuild()
        else:
            self._item.set_sensitive(False)

    def on_device_created(self, path: str) -> None:
        self._rebuild()

    def on_device_removed(self, path: str) -> None:
        self._rebuild()

    def on_adapter_added(self, path: str) -> None:
        self._rebuild()

    def on_adapter_removed(self, path: str) -> None:
        self._rebuild()

    def notify(self, object_path: str, uuid: str) -> None:
        device = Device(obj_path=object_path)
        logging.info(f"{device} {uuid}")
        try:
            adapter = self.parent.Manager.get_adapter(device['Adapter'])
        except DBusNoSuchAdapterError:
            logging.warning("adapter not found")
            return

        item = {
            "adapter": adapter["Address"],
            "address": device['Address'],
            "alias": device['Alias'],
            "icon": device['Icon'],
            "name": ServiceUUID(uuid).name,
            "uuid": uuid,
            "time": str(time.time()),
        }

        stored_items = self.get_option("recent-connections")

        for i in stored_items:
            if i["adapter"] == item["adapter"] and \
                    i["address"] == item["address"] and \
                    i["uuid"] == item["uuid"]:
                i["time"] = item["time"]
                i["device"] = object_path
                break
        else:
            stored_items.append(item)

        self.set_option("recent-connections", stored_items)

        self._rebuild()

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

    def _build_menu_item(self, item: "Item") -> "SubmenuItemDict":
        mitem: "SubmenuItemDict" = {
            "text": _("%(service)s on %(device)s") % {"service": item["name"], "device": item["alias"]},
            "markup": True,
            "icon_name": item["mitem"]["icon_name"] if item["mitem"] is not None else item["icon"],
            "sensitive": item["device"] is not None,
            "tooltip": None if item["device"] is None else _("Adapter for this connection is not available"),
            "callback": (item["mitem"]["callback"] if item["mitem"] is not None
                         else cast(Callable[[], None], lambda itm=item: self.on_item_activated(itm)))
        }

        item["mitem"] = mitem

        return mitem

    def get_menu(self) -> List["SubmenuItemDict"]:
        return self.__menuitems

    def _get_device_path(self, adapter_path: str, address: str) -> Optional[str]:
        try:
            adapter = self.parent.Manager.get_adapter(adapter_path)
        except DBusNoSuchAdapterError:
            return None

        device = self.parent.Manager.find_device(address, adapter.get_object_path())
        return device.get_object_path() if device is not None else None

    def _get_items(self) -> List["Item"]:
        adapter_addresses = {adapter["Address"] for adapter in self.parent.Manager.get_adapters()}

        return sorted(
            ({
                "adapter": i["adapter"],
                "address": i["address"],
                "alias": i["alias"],
                "icon": i["icon"],
                "name": i["name"],
                "uuid": i["uuid"],
                "time": float(i["time"]),
                "device": (self._get_device_path(i["adapter"], i["address"])
                           if i["adapter"] in adapter_addresses else None),
                "mitem": None
            }
                for i in self.get_option("recent-connections")
                if i["adapter"] not in adapter_addresses or self._get_device_path(i["adapter"], i["address"])),
            key=itemgetter("time"),
            reverse=True
        )

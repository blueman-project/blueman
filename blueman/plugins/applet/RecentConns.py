# coding=utf-8
from operator import itemgetter
import time
import logging
from blueman.bluez.Device import Device
from blueman.bluez.Manager import DBusNoSuchAdapterError
from blueman.gui.Notification import Notification
from blueman.Sdp import ServiceUUID
from blueman.plugins.AppletPlugin import AppletPlugin


REGISTRY_VERSION = 0


class AdapterNotFound(Exception):
    pass


class DeviceNotFound(Exception):
    pass


class RecentConns(AppletPlugin):
    __depends__ = ["Menu"]
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

    def on_load(self):
        self.Adapters = {}
        self.__menuitems = []

        self.item = self.parent.Plugins.Menu.add(self, 52, text=_("Recent _Connections") + "…",
                                                 icon_name="document-open-recent", submenu_function=self.get_menu)
        self.parent.Plugins.Menu.add(self, 53)

        self.deferred = False

    def store_state(self):
        to_store = []
        for item in self.items:
            x = item.copy()
            x["time"] = str(x["time"])
            x["uuid"] = str(x["uuid"])
            x["device"] = ''
            x["mitem"] = ''
            to_store.append(x)

        self.set_option("recent-connections", to_store)

    def change_sensitivity(self, sensitive):
        if 'PowerManager' in self.parent.Plugins.get_loaded():
            power = self.parent.Plugins.PowerManager.get_bluetooth_status()
        else:
            power = True

        sensitive = sensitive and \
            self.parent.Manager and \
            power and \
            self.items is not None and \
            (len(self.items) > 0)

        self.item.set_sensitive(sensitive)

    def on_power_state_changed(self, manager, state):
        self.change_sensitivity(state)
        if state and self.deferred:
            self.deferred = False
            self.on_manager_state_changed(state)

    def on_unload(self):
        self.parent.Plugins.Menu.unregister(self)

    def initialize(self):
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

    def on_manager_state_changed(self, state):
        if state:
            if 'PowerManager' in self.parent.Plugins.get_loaded():
                if not self.parent.Plugins.PowerManager.get_bluetooth_status():
                    self.deferred = True
                    self.item.set_sensitive(False)
                    return

            self.item.set_sensitive(True)
            adapters = self.parent.Manager.get_adapters()

            self.Adapters = {}
            for adapter in adapters:
                self.Adapters[str(adapter.get_object_path())] = str(adapter["Address"])

            for i in reversed(self.items):
                try:
                    i["device"] = self.get_device_path(i)
                except (AdapterNotFound, DeviceNotFound):
                    pass

            self.initialize()
        else:
            self.item.set_sensitive(False)
            return

        self.change_sensitivity(state)

    def on_device_removed(self, path):
        for item in reversed(self.items):
            if item['device'] == path:
                self.items.remove(item)
                self.initialize()

    def on_adapter_added(self, path):
        a = self.parent.Manager.get_adapter(path)
        self.Adapters[path] = a["Address"]
        self.initialize()

    def on_adapter_removed(self, path):
        if str(path) in self.Adapters:
            del self.Adapters[str(path)]
        else:
            logging.warning("Adapter not found in list")

        self.initialize()

    def notify(self, object_path, uuid):
        device = Device(object_path)
        logging.info("%s %s" % (device, uuid))
        item = {}
        try:
            adapter = self.parent.Manager.get_adapter(device['Adapter'])
        except DBusNoSuchAdapterError:
            logging.warning("adapter not found")
            return

        item["adapter"] = adapter["Address"]
        item["address"] = device['Address']
        item["alias"] = device['Alias']
        item["icon"] = device['Icon']
        item["name"] = ServiceUUID(uuid).name
        item["uuid"] = uuid
        item["time"] = time.time()
        item["device"] = object_path
        item["mitem"] = None  # menu item object

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

        self.store_state()

    def on_item_activated(self, item):
        logging.info("Connect %s %s" % (item["address"], item["uuid"]))

        item["mitem"]["sensitive"] = False
        self.parent.Plugins.Menu.on_menu_changed()

        def reply(*args):
            Notification(_("Connected"), _("Connected to %s") % item["mitem"]["text"],
                         icon_name=item["icon"]).show()
            item["mitem"]["sensitive"] = True
            self.parent.Plugins.Menu.on_menu_changed()

        def err(reason):
            Notification(_("Failed to connect"), str(reason).split(": ")[-1],
                         icon_name="dialog-error").show()
            item["mitem"]["sensitive"] = True
            self.parent.Plugins.Menu.on_menu_changed()

        self.parent.Plugins.DBusService.connect_service(item["device"], item["uuid"], reply, err)

    def add_item(self, item):
        if not item["mitem"]:
            mitem = {"icon_name": item["icon"], "callback": lambda itm=item: self.on_item_activated(itm)}
            item["mitem"] = mitem
        else:
            mitem = item["mitem"]
            mitem['sensitive'] = True
            mitem['tooltip'] = None

        item["mitem"]["text"] = _("%(service)s on %(device)s") % {"service": item["name"], "device": item["alias"]}
        item["mitem"]["markup"] = True

        if item["adapter"] not in self.Adapters.values():
            item["device"] = None
        elif not item["device"] and item["adapter"] in self.Adapters.values():
            try:
                item["device"] = self.get_device_path(item)

            except (AdapterNotFound, DeviceNotFound):
                self.items.remove(item)
                self.initialize()

        if not item["device"]:
            mitem["sensitive"] = False
            mitem["tooltip"] = _("Adapter for this connection is not available")

        self.__menuitems.append(mitem)
        self.parent.Plugins.Menu.on_menu_changed()

    def get_menu(self):
        return self.__menuitems

    def get_device_path(self, item):
        try:
            adapter = self.parent.Manager.get_adapter(item["adapter"])
        except DBusNoSuchAdapterError:
            raise AdapterNotFound

        device = self.parent.Manager.find_device(item["address"], adapter.get_object_path())
        if device is None:
            raise DeviceNotFound
        else:
            return device.get_object_path()

    @property
    def items(self):
        if self._items is not None:
            return self._items

        items = self.get_option("recent-connections")

        if not items:
            self._items = []
            return self._items

        for i in reversed(items):
            if "name" not in i or "uuid" not in i:
                items.remove(i)
            try:
                i["device"] = self.get_device_path(i)
            except AdapterNotFound:
                i["device"] = None
            except DeviceNotFound:
                items.remove(i)

            i["time"] = float(i["time"])

        self._items = items

        return self._items

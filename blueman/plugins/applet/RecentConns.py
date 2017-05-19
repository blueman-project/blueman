# coding=utf-8
from operator import itemgetter
import time
import logging
from blueman.Functions import *
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.gui.Notification import Notification
from blueman.Sdp import ServiceUUID
from blueman.plugins.AppletPlugin import AppletPlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


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

    def on_load(self, applet):
        self.Applet = applet
        self.Adapters = {}
        self.items = None
        self.__menuitems = []

        self.item = self.Applet.Plugins.Menu.add(self, 52, text=_("Recent _Connections") + "…",
                                                 icon_name="document-open-recent", submenu_function=self.get_menu)
        self.Applet.Plugins.Menu.add(self, 53)

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
        try:
            power = self.Applet.Plugins.PowerManager.GetBluetoothStatus()
        except:
            power = True

        sensitive = sensitive and \
                    self.Applet.Manager and \
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
        self.Applet.Plugins.Menu.unregister(self)

        RecentConns.items = []

    def initialize(self):
        logging.info("rebuilding menu")
        if self.items is None:
            self.recover_state()

        self.__menuitems = []
        self.Applet.Plugins.Menu.on_menu_changed()

        self.items.sort(key=itemgetter("time"), reverse=True)

        self.items = self.items[0:self.get_option("max-items")]
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
            try:
                if not self.Applet.Plugins.PowerManager.GetBluetoothStatus():
                    self.deferred = True
                    self.item.set_sensitive(False)
                    return
            except:
                pass

            self.item.set_sensitive(True)
            adapters = self.Applet.Manager.get_adapters()
            self.Adapters = {}
            for adapter in adapters:
                self.Adapters[str(adapter.get_object_path())] = str(adapter["Address"])

            if self.items is not None:
                for i in reversed(self.items):

                    try:
                        i["device"] = self.get_device_path(i)
                    except:
                        pass

            else:
                self.recover_state()

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
        a = Adapter(path)

        def on_activated():
            self.Adapters[str(path)] = str(a["Address"])
            self.initialize()

        wait_for_adapter(a, on_activated)

    def on_adapter_removed(self, path):
        try:
            del self.Adapters[str(path)]
        except:
            logging.warning("Adapter not found in list")

        self.initialize()

    def notify(self, object_path, uuid):
        device = Device(object_path)
        logging.info("%s %s" % (device, uuid))
        item = {}
        try:
            adapter = Adapter(device['Adapter'])
        except:
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
        item["mitem"] = None #menu item object

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
        self.Applet.Plugins.Menu.on_menu_changed()

        def reply(*args):
            Notification(_("Connected"), _("Connected to %s") % item["mitem"]["text"],
                         icon_name=item["icon"]).show()
            item["mitem"]["sensitive"] = True
            self.Applet.Plugins.Menu.on_menu_changed()

        def err(reason):
            Notification(_("Failed to connect"), str(reason).split(": ")[-1],
                         icon_name="dialog-error").show()
            item["mitem"]["sensitive"] = True
            self.Applet.Plugins.Menu.on_menu_changed()

        self.Applet.DbusSvc.connect_service(item["device"], item["uuid"], reply, err)

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

            except:
                self.items.remove(item)
                self.initialize()

        if not item["device"]:
            mitem["sensitive"] = False
            mitem["tooltip"] = _("Adapter for this connection is not available")

        self.__menuitems.append(mitem)
        self.Applet.Plugins.Menu.on_menu_changed()

    def get_menu(self):
        return self.__menuitems

    def get_device_path(self, item):
        try:
            adapter = self.Applet.Manager.get_adapter(item["adapter"])
        except ValueError:
            raise AdapterNotFound
        try:
            device = self.Applet.Manager.find_device(item["address"], adapter.get_object_path())
            return device.get_object_path()
        except:
            raise DeviceNotFound

    def recover_state(self):
        items = self.get_option("recent-connections")

        if not items:
            self.items = []
            return

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

        self.items = items

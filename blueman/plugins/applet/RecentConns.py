# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from operator import itemgetter
import time
import weakref
import pickle
import base64
import zlib
import logging
from blueman.Functions import *
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.gui.Notification import Notification
from blueman.Sdp import ServiceUUID

from blueman.plugins.AppletPlugin import AppletPlugin

REGISTRY_VERSION = 0


class AdapterNotFound(Exception):
    pass


class DeviceNotFound(Exception):
    pass


def store_state():
    try:
        RecentConns.inst.store_state()
    except ReferenceError:
        pass


class RecentConns(AppletPlugin, Gtk.Menu):
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
                  #the maximum number of items RecentConns menu will display
                  "name": _("Maximum items"),
                  "desc": _("The maximum number of items recent connections menu will display."),
                  "range": (6, 20)},
    "recent-connections": {"type": str, "default": ""}
    }

    items = None
    inst = None
    atexit_registered = False

    def on_load(self, applet):
        self.Applet = applet
        self.Adapters = {}
        Gtk.Menu.__init__(self)
        if not RecentConns.atexit_registered:
            atexit.register(store_state)
            RecentConns.atexit_registered = True

        self.Item = create_menuitem(_("Recent _Connections") + "...",
                                    get_icon("document-open-recent", 16))

        self.Applet.Plugins.Menu.Register(self, self.Item, 52)
        self.Applet.Plugins.Menu.Register(self, Gtk.SeparatorMenuItem(), 53)

        self.Item.set_submenu(self)

        self.deferred = False
        RecentConns.inst = weakref.proxy(self)

    def store_state(self):
        items = []

        if RecentConns.items:
            for i in RecentConns.items:
                x = i.copy()
                x["device"] = None
                x["mitem"] = None
                items.append(x)

        try:
            dump = base64.b64encode(
                zlib.compress(
                    pickle.dumps((REGISTRY_VERSION, items), 2),
                    9)).decode()

            self.set_option("recent-connections", dump)
        except:
            logging.warning("Failed to store recent connections", exc_info=True)

    def change_sensitivity(self, sensitive):
        try:
            power = self.Applet.Plugins.PowerManager.GetBluetoothStatus()
        except:
            power = True

        sensitive = sensitive and \
                    self.Applet.Manager and \
                    power and \
                    RecentConns.items is not None and \
                    (len(RecentConns.items) > 0)

        self.Item.props.sensitive = sensitive

    def on_power_state_changed(self, manager, state):
        self.change_sensitivity(state)
        if state and self.deferred:
            self.deferred = False
            self.on_manager_state_changed(state)

    def on_unload(self):
        self.destroy()
        self.Applet.Plugins.Menu.Unregister(self)

        RecentConns.items = []
        self.destroy()

    def initialize(self):
        logging.info("rebuilding menu")
        if RecentConns.items is None:
            self.recover_state()

        def each(child, _):
            self.remove(child)

        self.foreach(each, None)

        RecentConns.items.sort(key=itemgetter("time"), reverse=True)

        RecentConns.items = RecentConns.items[0:self.get_option("max-items")]
        RecentConns.items.reverse()

        if len(RecentConns.items) == 0:
            self.change_sensitivity(False)
        else:
            self.change_sensitivity(True)

        count = 0
        for item in RecentConns.items:
            if count < self.get_option("max-items"):
                self.add_item(item)
                count += 1

    def on_manager_state_changed(self, state):

        if state:
            try:
                if not self.Applet.Plugins.PowerManager.GetBluetoothStatus():
                    self.deferred = True
                    self.Item.props.sensitive = False
                    return
            except:
                pass

            self.Item.props.sensitive = True
            adapters = self.Applet.Manager.get_adapters()
            self.Adapters = {}
            for adapter in adapters:
                self.Adapters[str(adapter.get_object_path())] = str(adapter["Address"])

            if RecentConns.items is not None:
                for i in reversed(RecentConns.items):

                    try:
                        i["device"] = self.get_device_path(i)
                    except:
                        pass

            else:
                self.recover_state()

            self.initialize()
        else:
            self.Item.props.sensitive = False
            return

        self.change_sensitivity(state)

    def on_device_removed(self, path):
        for item in reversed(RecentConns.items):
            if item['device'] == path:
                RecentConns.items.remove(item)
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

        for i in RecentConns.items:
            if i["adapter"] == item["adapter"] and \
                            i["address"] == item["address"] and \
                            i["uuid"] == item["uuid"]:
                i["time"] = item["time"]

                i["device"] = item["device"]
                self.initialize()
                return

        RecentConns.items.append(item)
        self.initialize()

        self.store_state()

    def on_item_activated(self, menu_item, item):
        logging.info("Connect %s %s" % (item["address"], item["uuid"]))

        item["mitem"].props.sensitive = False

        def reply(*args):
            label_text = item["mitem"].get_child().get_children()[1].get_text()
            Notification(_("Connected"), _("Connected to %s") % label_text,
                         icon_name=item["icon"], pos_hint=self.Applet.Plugins.StatusIcon.geometry).show()
            item["mitem"].props.sensitive = True

        def err(reason):
            Notification(_("Failed to connect"), str(reason).split(": ")[-1],
                         icon_name="dialog-error", pos_hint=self.Applet.Plugins.StatusIcon.geometry).show()
            item["mitem"].props.sensitive = True

        self.Applet.DbusSvc.connect_service(item["device"], item["uuid"], reply, err)

    def add_item(self, item):
        if not item["mitem"]:
            mitem = create_menuitem("", get_icon(item["icon"], 16))
            item["mitem"] = mitem
            mitem.connect("activate", self.on_item_activated, item)
        else:
            mitem = item["mitem"]
            mitem.props.sensitive = True
            mitem.props.tooltip_text = None

        item_label_markup = _("%(service)s on %(device)s") % {"service": item["name"], "device": item["alias"]}
        item_label = item["mitem"].get_child().get_children()[1]
        item_label.set_markup_with_mnemonic(item_label_markup)

        if item["adapter"] not in self.Adapters.values():
            item["device"] = None
        elif not item["device"] and item["adapter"] in self.Adapters.values():
            try:
                item["device"] = self.get_device_path(item)

            except:
                RecentConns.items.remove(item)
                self.initialize()

        if not item["device"]:
            mitem.props.sensitive = False
            mitem.props.tooltip_text = _("Adapter for this connection is not available")

        self.prepend(mitem)
        mitem.show()

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
        dump = self.get_option("recent-connections")
        try:
            (version, items) = pickle.loads(zlib.decompress(base64.b64decode(dump)))
        except:
            items = None
            version = None

        if version is None or version != REGISTRY_VERSION:
            items = None

        if items is None:
            RecentConns.items = []
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

        RecentConns.items = items

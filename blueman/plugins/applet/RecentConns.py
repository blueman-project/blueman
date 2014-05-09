import os
from gi.repository import Gtk
from gi.repository import Gdk
import dbus
import gettext
import time
import atexit
import weakref
import pickle
import base64
import zlib
from blueman.Functions import *
from blueman.main.Device import Device
from blueman.bluez.Device import Device as BluezDevice
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Serial import Serial
from blueman.bluez.Network import Network
from blueman.main.SignalTracker import SignalTracker
from blueman.gui.Notification import Notification
import blueman.Sdp as sdp

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

    __options__ = {
    "max_items": {"type": int,
                  "default": 6,
                  #the maximum number of items RecentConns menu will display
                  "name": _("Maximum items"),
                  "desc": _("The maximum number of items recent connections menu will display."),
                  "range": (6, 20)
    },
    "recent_connections": {"type": str, "default": ""}
    }

    items = None
    inst = None
    atexit_registered = False

    def on_load(self, applet):
        self.Applet = applet
        self.Adapters = {}
        GObject.GObject.__init__(self)
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
                x["gsignal"] = 0
                items.append(x)

        try:
            dump = base64.b64encode(
                zlib.compress(
                    pickle.dumps((REGISTRY_VERSION, items),
                                 pickle.HIGHEST_PROTOCOL),
                    9))

            self.set_option("recent_connections", dump)
        except:
            dprint(YELLOW("Failed to store recent connections"))

    def change_sensitivity(self, sensitive):
        try:
            power = self.Applet.Plugins.PowerManager.GetBluetoothStatus()
        except:
            power = True

        sensitive = sensitive and \
                    self.Applet.Manager and \
                    power and \
                    RecentConns.items != None and \
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
        if RecentConns.items:
            for i in reversed(RecentConns.items):
                if i["device"]:
                    if i["gsignal"]:
                        i["device"].disconnect(i["gsignal"])
                        i["gsignal"] = None

        RecentConns.items = []
        self.destroy()

    def initialize(self):
        dprint("rebuilding menu")
        if not RecentConns.items:
            self.recover_state()

        def compare_by(fieldname):
            def compare_two_dicts(a, b):
                return cmp(a[fieldname], b[fieldname])

            return compare_two_dicts

        def each(child, _):
            self.remove(child)

        self.foreach(each, None)

        RecentConns.items.sort(compare_by("time"), reverse=True)
        for i in RecentConns.items[self.get_option("max_items"):]:
            if i["gsignal"]:
                i["device"].disconnect(i["gsignal"])

        RecentConns.items = RecentConns.items[0:self.get_option("max_items")]
        RecentConns.items.reverse()

        if len(RecentConns.items) == 0:
            self.change_sensitivity(False)
        else:
            self.change_sensitivity(True)

        count = 0
        for item in RecentConns.items:
            if count < self.get_option("max_items"):
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
            adapters = self.Applet.Manager.list_adapters()
            self.Adapters = {}
            for adapter in adapters:
                p = adapter.get_properties()
                self.Adapters[str(adapter.get_object_path())] = str(p["Address"])

            if RecentConns.items != None:
                for i in reversed(RecentConns.items):

                    if i["device"]:
                        if i["gsignal"]:
                            i["device"].disconnect(i["gsignal"])
                            i["gsignal"] = 0
                        #i["device"].Destroy()

                    try:
                        i["device"] = self.get_device(i)
                        i["gsignal"] = i["device"].connect("invalidated", self.on_device_removed, i)
                    except:
                        pass

            else:
                self.recover_state()

            self.initialize()
        else:
            self.Item.props.sensitive = False
            return

        self.change_sensitivity(state)

    def on_device_removed(self, device, item):
        device.disconnect(item["gsignal"])
        RecentConns.items.remove(item)
        self.initialize()

    def on_adapter_added(self, path):
        a = Adapter(path)

        def on_activated():
            props = a.get_properties()
            self.Adapters[str(path)] = str(props["Address"])
            self.initialize()

        wait_for_adapter(a, on_activated)

    def on_adapter_removed(self, path):
        try:
            del self.Adapters[str(path)]
        except:
            dprint("Adapter not found in list")

        self.initialize()

    def notify(self, device, service_interface, conn_args):
        dprint(device, service_interface, conn_args)
        item = {}
        object_path = device.get_object_path()
        try:
            adapter = Adapter(device.Adapter)
        except:
            dprint("adapter not found")
            return

        props = adapter.get_properties()

        item["adapter"] = props["Address"]
        item["address"] = device.Address
        item["alias"] = device.Alias
        item["icon"] = device.Icon
        item["service"] = service_interface
        item["conn_args"] = conn_args
        item["time"] = time.time()
        item["device"] = device #device object
        item["mitem"] = None #menu item object

        for i in RecentConns.items:
            if i["adapter"] == item["adapter"] and \
                            i["address"] == item["address"] and \
                            i["service"] == item["service"] and \
                            i["conn_args"] == item["conn_args"]:
                i["time"] = item["time"]
                if i["gsignal"]:
                    i["device"].disconnect(i["gsignal"])

                i["device"] = item["device"]
                i["gsignal"] = item["device"].connect("invalidated", self.on_device_removed, i)
                self.initialize()
                return

        item["gsignal"] = item["device"].connect("invalidated", self.on_device_removed, item)
        RecentConns.items.append(item)
        self.initialize()

        self.store_state()

    def on_item_activated(self, menu_item, item):
        dprint("Connect", item["address"], item["service"])

        sv_name = item["service"].split(".")[-1].lower()
        try:
            service = item["device"].Services[sv_name]
        except:
            RecentConns.items.remove(item)
        else:
            sn = startup_notification("Bluetooth Connection",
                                      desc=_("Connecting to %s") % item["mitem"].get_child().props.label,
                                      icon="blueman")

            item["mitem"].props.sensitive = False

            def reply(*args):
                Notification(_("Connected"), _("Connected to %s") % item["mitem"].get_child().props.label,
                             pixbuf=get_icon("gtk-connect", 48),
                             status_icon=self.Applet.Plugins.StatusIcon)
                item["mitem"].props.sensitive = True
                sn.complete()

            def err(reason):
                Notification(_("Failed to connect"), str(reason).split(": ")[-1],
                             pixbuf=get_icon("gtk-dialog-error", 48),
                             status_icon=self.Applet.Plugins.StatusIcon)
                item["mitem"].props.sensitive = True
                sn.complete()

            if item["service"] == Serial().get_interface_name():
                self.Applet.DbusSvc.RfcommConnect(item["device"].get_object_path(), item["conn_args"][0], reply, err)
            else:
                self.Applet.DbusSvc.ServiceProxy(item["service"], item["device"].get_object_path(), "Connect",
                                                 item["conn_args"], reply, err)

    def add_item(self, item):
        device = item["device"]

        if item["service"] == Serial().get_interface_name():
            name = sdp.sdp_get_serial_name(item["address"], item["conn_args"][0])

        elif item["service"] == Network().get_interface_name():
            name = _("Network Access (%s)") % sdp.uuid16_to_name(sdp.uuid128_to_uuid16(item["conn_args"][0]))
        else:
            try:
                name = sdp.bluez_to_friendly_name(item["service"].split(".")[-1].lower())
            except:
                name = item["service"].split(".")[-1] + " " + _("Service")
                name = name.capitalize()

        if not item["mitem"]:
            mitem = create_menuitem("", get_icon(item["icon"], 16))
            item["mitem"] = mitem
            mitem.connect("activate", self.on_item_activated, item)
        else:
            mitem = item["mitem"]
            mitem.props.sensitive = True
            mitem.props.tooltip_text = None

        item["mitem"].props.label = (_("%(service)s on %(device)s") % {"service": name, "device": item["alias"]})

        if item["adapter"] not in self.Adapters.values():
            if item["device"] and item["gsignal"]:
                item["device"].disconnect(item["gsignal"])

            item["device"] = None
        elif not item["device"] and item["adapter"] in self.Adapters.values():
            try:
                dev = self.get_device(item)
                item["device"] = dev
                item["gsignal"] = item["device"].connect("invalidated", self.on_device_removed, item)

            except:
                RecentConns.items.remove(item)
                self.initialize()

        if not item["device"]:
            mitem.props.sensitive = False
            mitem.props.tooltip_text = _("Adapter for this connection is not available")

        self.prepend(mitem)
        mitem.show()

    def get_device(self, item):
        try:
            adapter = self.Applet.Manager.get_adapter(item["adapter"])
        except:
            raise AdapterNotFound
        try:
            return Device(adapter.find_device(item["address"]))
        except:
            raise DeviceNotFound

    def recover_state(self):
        dump = self.get_option("recent_connections")
        try:
            (version, items) = pickle.loads(zlib.decompress(base64.b64decode(dump)))
        except:
            items = None
            version = None

        if version == None or version != REGISTRY_VERSION:
            items = None

        if items == None:
            RecentConns.items = []
            return

        for i in reversed(items):
            try:
                i["device"] = self.get_device(i)
            except AdapterNotFound:
                i["device"] = None
            except DeviceNotFound:
                items.remove(i)
            else:
                i["gsignal"] = i["device"].connect("invalidated", self.on_device_removed, i)

        RecentConns.items = items

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.Constants import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config
from blueman.main.SignalTracker import SignalTracker
from blueman.bluez.Device import Device as BluezDevice
from blueman.bluez.Network import Network
from blueman.main.Device import Device
from _blueman import rfcomm_list
from gi.repository import GObject
import weakref
import os
import cgi

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Pango
import dbus
import time
import datetime
import gettext


class MonitorBase(GObject.GObject):
    __gsignals__ = {
    str('disconnected'): (GObject.SignalFlags.NO_HOOKS, None, ()),
    str('stats'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, device, interface):
        GObject.GObject.__init__(self)

        self.interface = interface
        self.device = device
        self.general_config = Config("org.blueman.general")
        self.config = Config("org.blueman.plugins.netusage", "/org/blueman/plugins/netusages/%s/" % device.Address)

        self.last_tx = 0
        self.last_rx = 0

    #tx and rx must be cumulative absolute values
    def update_stats(self, tx, rx):
        dtx = tx - self.last_tx
        drx = rx - self.last_rx

        if dtx < 0:
            dtx = 0
        if drx < 0:
            drx = 0

        self.last_rx = rx
        self.last_tx = tx
        if dtx > 0:
            self.config["tx"] += dtx
        if drx > 0:
            self.config["rx"] += drx

        self.emit("stats", self.config["tx"], self.config["rx"])

        if not self.device.Address in self.general_config["netusage-dev-list"]:
            self.general_config["netusage-dev-list"] += [self.device.Address]

    def Disconnect(self):
        self.emit("disconnected")


class NMMonitor(MonitorBase):
    def __init__(self, device, nm_dev_path):
        MonitorBase.__init__(self, device, "NM")
        dprint("created nm monitor for path", nm_dev_path)
        self.signals = SignalTracker()
        self.signals.Handle("dbus",
                            dbus.SystemBus(),
                            self.on_ppp_stats,
                            "PppStats",
                            "org.freedesktop.NetworkManager.Device.Serial",
                            path=nm_dev_path)

        self.signals.Handle(device, "property-changed", self.on_device_property_changed)

    def on_ppp_stats(self, rx, tx):
        self.update_stats(tx, rx)

    def on_device_property_changed(self, device, key, value):
        if key == "Connected" and not value:
            self.signals.DisconnectAll()
            self.Disconnect()


class Monitor(MonitorBase):
    def __init__(self, device, interface):
        MonitorBase.__init__(self, device, interface)
        self.poller = None

        self.poller = GObject.timeout_add(5000, self.poll_stats)

    def __del__(self):
        print("deleting monitor")

    def poll_stats(self):
        try:
            f = open("/sys/class/net/%s/statistics/tx_bytes" % self.interface, "r")
            tx = int(f.readline())
            f.close()

            f = open("/sys/class/net/%s/statistics/rx_bytes" % self.interface, "r")
            rx = int(f.readline())
            f.close()
        except IOError:
            self.poller = None
            self.ppp_port = None
            self.interface = None
            self.config = None
            self.Disconnect()
            return False

        self.update_stats(tx, rx)

        return True


class Dialog:
    running = False

    def __init__(self, parent):
        if not Dialog.running:
            Dialog.running = True
        else:
            return
        self.config = None
        self.parent = parent
        builder = Gtk.Builder()
        builder.add_from_file(UI_PATH + "/net-usage.ui")
        builder.set_translation_domain("blueman")

        self.dialog = builder.get_object("dialog")
        self.dialog.connect("response", self.on_response)
        cr1 = Gtk.CellRendererText()
        cr1.props.ellipsize = Pango.EllipsizeMode.END

        self.devices = {}
        self.signals = SignalTracker()

        self.signals.Handle(parent, "monitor-added", self.monitor_added)
        self.signals.Handle(parent, "monitor-removed", self.monitor_removed)
        self.signals.Handle(parent, "stats", self.on_stats)

        cr2 = Gtk.CellRendererText()
        cr2.props.sensitive = False
        cr2.props.style = Pango.Style.ITALIC

        self.liststore = Gtk.ListStore(str, str, str, object)

        self.e_ul = builder.get_object("e_ul")
        self.e_dl = builder.get_object("e_dl")
        self.e_total = builder.get_object("e_total")

        self.l_started = builder.get_object("l_started")
        self.l_duration = builder.get_object("l_duration")

        self.b_reset = builder.get_object("b_reset")
        self.b_reset.connect("clicked", self.on_reset)

        self.cb_device = builder.get_object("cb_device")
        self.cb_device.props.model = self.liststore
        self.cb_device.connect("changed", self.on_selection_changed)

        self.cb_device.pack_start(cr1, True)
        self.cb_device.add_attribute(cr1, 'markup', 1)

        self.cb_device.pack_start(cr2, False)
        self.cb_device.add_attribute(cr2, 'markup', 2)

        general_config = Config("org.blueman.general")

        added = False
        for d in general_config["netusage-dev-list"]:
            for m in parent.monitors:
                if d == m.device.Address:
                    iter = self.liststore.append(
                        [d, self.get_caption(m.device.Alias, m.device.Address), _("Connected:") + " " + m.interface, m])
                    if self.cb_device.get_active() == -1:
                        self.cb_device.set_active_iter(iter)
                    added = True
                    break
            if not added:
                name = d
                if self.parent.Applet.Manager:
                    for a in self.parent.Applet.Manager.list_adapters():
                        try:
                            device = a.find_device(d)
                            device = Device(device)
                            name = self.get_caption(device.Alias, device.Address)
                        except:
                            pass

                self.liststore.append([d, name, _("Not Connected"), None])
            added = False
        if len(self.liststore) > 0:
            if self.cb_device.get_active() == -1:
                self.cb_device.set_active(0)
        else:
            d = Gtk.MessageDialog(parent=self.dialog, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO,
                                  buttons=Gtk.ButtonsType.CLOSE, message_format=_(
                    "No usage statistics are available yet. Try establishing a connection first and then check this page."))
            d.props.icon_name = "blueman"
            d.run()
            d.destroy()
            self.on_response(None, None)
            return

        self.dialog.show()

    def on_response(self, dialog, response):
        self.signals.DisconnectAll()
        Dialog.running = False
        self.dialog.destroy()

    def update_time(self):
        time = self.config["time"]
        if time:
            self.datetime = datetime.datetime.fromtimestamp(time)

            self.l_started.props.label = str(self.datetime)

            delta = datetime.datetime.now() - self.datetime

            d = gettext.ngettext("day", "days", delta.days)
            h = gettext.ngettext("hour", "hours", delta.seconds / 3600)
            m = gettext.ngettext("minute", "minutes", delta.seconds % 3600 / 60)

            self.l_duration.props.label = _("%d %s %d %s and %d %s") % (
            delta.days, d, delta.seconds / 3600, h, delta.seconds % 3600 / 60, m)
        else:
            self.l_started.props.label = _("Unknown")
            self.l_duration.props.label = _("Unknown")

    def on_selection_changed(self, cb):
        iter = cb.get_active_iter()
        (addr,) = self.liststore.get(iter, 0)
        self.config = Config("org.blueman.plugins.netusage", "/org/blueman/plugins/netusages/%s/" % addr)
        self.update_counts(self.config["tx"], self.config["rx"])
        self.update_time()

    def get_caption(self, name, address):
        return "%s\n<small>%s</small>" % (cgi.escape(name), address)

    def update_counts(self, tx, rx):
        tx = int(tx)
        rx = int(rx)

        (num, suffix) = format_bytes(tx)
        self.e_ul.props.text = "%.2f %s" % (num, suffix)

        (num, suffix) = format_bytes(rx)
        self.e_dl.props.text = "%.2f %s" % (num, suffix)

        (num, suffix) = format_bytes(int(tx) + int(rx))
        self.e_total.props.text = "%.2f %s" % (num, suffix)

        self.update_time()

    def on_reset(self, button):
        d = Gtk.MessageDialog(parent=self.dialog, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.QUESTION,
                              buttons=Gtk.ButtonsType.YES_NO,
                              message_format=_("Are you sure you want to reset the counter?"))
        res = d.run()
        d.destroy()
        if res == Gtk.ResponseType.YES:
            self.config["rx"] = 0
            self.config["tx"] = 0
            self.config["time"] = int(time.time())

            self.update_counts(0, 0)

    def on_stats(self, parent, monitor, tx, rx):
        iter = self.cb_device.get_active_iter()
        (mon,) = self.liststore.get(iter, 3)
        if mon == monitor:
            self.update_counts(tx, rx)

    def monitor_added(self, parent, monitor):
        for row in self.liststore:
            iter = row.iter
            (val,) = self.liststore.get(iter, 0)

            if val == monitor.device.Address:
                self.liststore.set(iter, 1, self.get_caption(monitor.device.Alias, monitor.device.Address), 2,
                                   _("Connected:") + " " + monitor.interface, 3, monitor)
                return

        self.liststore.append([monitor.device.Address, self.get_caption(monitor.device.Alias, monitor.device.Address),
                               _("Connected:") + " " + monitor.interface, monitor])

    def monitor_removed(self, parent, monitor):
        for row in self.liststore:
            iter = row.iter
            (val,) = self.liststore.get(iter, 0)

            if val == monitor.device.Address:
                self.liststore.set(iter, 1, self.get_caption(monitor.device.Alias, monitor.device.Address), 2,
                                   _("Not Connected"), 3, None)
                return


class NetUsage(AppletPlugin, GObject.GObject):
    __depends__ = ["Menu"]
    __icon__ = "network-wireless"
    __description__ = _(
        "Allows you to monitor your (mobile broadband) network traffic usage. Useful for limited data access plans. This plugin tracks every device seperately.")
    __author__ = "Walmis"
    __autoload__ = False
    __gsignals__ = {
    str('monitor-added'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    str('monitor-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    #monitor, tx, rx
    str('stats'): (
    GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    def on_load(self, applet):
        GObject.GObject.__init__(self)
        self.monitors = []
        self.devices = weakref.WeakValueDictionary()
        self.signals = SignalTracker()

        bus = self.bus = dbus.SystemBus()
        self.signals.Handle('bluez', Network(), self.on_network_property_changed, 'PropertyChanged',
                            path_keyword="path")

        item = create_menuitem(_("Network _Usage"), get_icon("network-wireless", 16))
        item.props.tooltip_text = _("Shows network traffic usage")
        self.signals.Handle(item, "activate", self.activate_ui)
        self.Applet.Plugins.Menu.Register(self, item, 84, True)

        self.signals.Handle("dbus", bus, self.on_nm_ppp_stats, "PppStats",
                            "org.freedesktop.NetworkManager.Device.Serial", path_keyword="path")
        self.nm_paths = {}

    def on_nm_ppp_stats(self, down, up, path):
        if not path in self.nm_paths:
            props = self.bus.call_blocking("org.freedesktop.NetworkManager",
                                           path,
                                           "org.freedesktop.DBus.Properties",
                                           "GetAll",
                                           "s",
                                           ["org.freedesktop.NetworkManager.Device"])

            if props["Driver"] == "bluetooth" and "rfcomm" in props["Interface"]:
                self.nm_paths[path] = True

                portid = int(props["Interface"].strip("rfcomm"))

                ls = rfcomm_list()
                for dev in ls:
                    if dev["id"] == portid:
                        adapter = self.Applet.Manager.get_adapter(dev["src"])
                        device = adapter.find_device(dev["dst"])
                        device = Device(device)

                        self.monitor_interface(NMMonitor, device, path)

                        return
            else:
                self.nm_paths[path] = False


    def on_network_property_changed(self, key, value, path):
        dprint(key, value, path)
        if key == "Interface" and value != "":
            d = BluezDevice(path)
            d = Device(d)
            self.monitor_interface(Monitor, d, value)

    def activate_ui(self, item):
        Dialog(self)

    def on_unload(self):
        self.signals.DisconnectAll()
        self.Applet.Plugins.Menu.Unregister(self)

    def monitor_interface(self, montype, *args):
        m = montype(*args)
        self.monitors.append(m)
        self.signals.Handle(m, "stats", self.on_stats, sigid=m)
        self.signals.Handle(m, "disconnected", self.on_monitor_disconnected, sigid=m)
        self.emit("monitor-added", m)

    def on_ppp_connected(self, device, rfcomm, ppp_port):
        self.monitor_interface(Monitor, device, ppp_port)

    def on_monitor_disconnected(self, monitor):
        self.monitors.remove(monitor)
        self.signals.Disconnect(monitor)
        self.emit("monitor-removed", monitor)

    def on_stats(self, monitor, tx, rx):
        self.emit("stats", monitor, tx, rx)

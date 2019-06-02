# coding=utf-8

from html import escape
import time
import datetime
import gettext
import logging
from locale import bind_textdomain_codeset

from blueman.Functions import *
from blueman.Constants import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config
from blueman.bluez.Device import Device
from blueman.bluez.Network import AnyNetwork
from gi.repository import GObject
from gi.repository import GLib

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Pango


class MonitorBase(GObject.GObject):
    __gsignals__ = {
        'disconnected': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'stats': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, device, interface):
        super().__init__()

        self.interface = interface
        self.device = device
        self.general_config = Config("org.blueman.general")
        self.config = Config("org.blueman.plugins.netusage", "/org/blueman/plugins/netusages/%s/" % device["Address"])

        self.last_tx = 0
        self.last_rx = 0

    # tx and rx must be cumulative absolute values
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

        if not self.device["Address"] in self.general_config["netusage-dev-list"]:
            self.general_config["netusage-dev-list"] += [self.device["Address"]]

    def disconnect_monitor(self):
        self.emit("disconnected")


class Monitor(MonitorBase):
    def __init__(self, device, interface):
        super().__init__(device, interface)
        self.poller = None
        self.ppp_port = None

        self.poller = GLib.timeout_add(5000, self.poll_stats)

    def __del__(self):
        logging.debug("deleting monitor")

    def poll_stats(self):
        try:
            with open("/sys/class/net/%s/statistics/tx_bytes" % self.interface, "r") as f:
                tx = int(f.readline())

            with open("/sys/class/net/%s/statistics/rx_bytes" % self.interface, "r") as f:
                rx = int(f.readline())
        except IOError:
            self.poller = None
            self.ppp_port = None
            self.interface = None
            self.config = None
            self.disconnect_monitor()
            return False

        self.update_stats(tx, rx)

        return True


class Dialog:
    running = False

    def __init__(self, plugin):
        if not Dialog.running:
            Dialog.running = True
        else:
            return
        self.config = None
        self.plugin = plugin
        builder = Gtk.Builder()
        builder.add_from_file(UI_PATH + "/net-usage.ui")
        builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")

        self.dialog = builder.get_object("dialog")
        self.dialog.connect("response", self.on_response)
        cr1 = Gtk.CellRendererText()
        cr1.props.ellipsize = Pango.EllipsizeMode.END

        self._signals = [
            plugin.connect("monitor-added", self.monitor_added),
            plugin.connect("monitor-removed", self.monitor_removed),
            plugin.connect("stats", self.on_stats)
        ]

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
            for m in plugin.monitors:
                if d == m.device["Address"]:
                    titer = self.liststore.append(
                        [d, self.get_caption(m.device["Alias"], m.device["Address"]),
                         _("Connected:") + " " + m.interface, m])
                    if self.cb_device.get_active() == -1:
                        self.cb_device.set_active_iter(titer)
                    added = True
                    break
            if not added:
                name = d
                if self.plugin.parent.Manager:
                    device = self.plugin.parent.Manager.find_device(d)
                    if device is None:
                        pass
                    else:
                        name = self.get_caption(device["Alias"], device["Address"])

                self.liststore.append([d, name, _("Not Connected"), None])
            added = False
        if len(self.liststore) > 0:
            if self.cb_device.get_active() == -1:
                self.cb_device.set_active(0)
        else:
            msg = _("No usage statistics are available yet. Try establishing a connection first and "
                    "then check this page.")
            d = Gtk.MessageDialog(parent=self.dialog, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO,
                                  buttons=Gtk.ButtonsType.CLOSE, message_format=msg)
            d.props.icon_name = "blueman"
            d.run()
            d.destroy()
            self.on_response(None, None)
            return

        self.dialog.show()

    def on_response(self, dialog, response):
        for sig in self._signals:
            self.plugin.disconnect(sig)
        self._signals = []
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
        titer = cb.get_active_iter()
        (addr,) = self.liststore.get(titer, 0)
        self.config = Config("org.blueman.plugins.netusage", "/org/blueman/plugins/netusages/%s/" % addr)
        self.update_counts(self.config["tx"], self.config["rx"])
        self.update_time()

    def get_caption(self, name, address):
        return "%s\n<small>%s</small>" % (escape(name), address)

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
        titer = self.cb_device.get_active_iter()
        (mon,) = self.liststore.get(titer, 3)
        if mon == monitor:
            self.update_counts(tx, rx)

    def monitor_added(self, parent, monitor):
        for row in self.liststore:
            titer = row.iter
            (val,) = self.liststore.get(titer, 0)

            if val == monitor.device["Address"]:
                self.liststore.set(titer, 1, self.get_caption(monitor.device["Alias"], monitor.device["Address"]), 2,
                                   _("Connected:") + " " + monitor.interface, 3, monitor)
                return

        self.liststore.append(
            [monitor.device["Address"], self.get_caption(monitor.device["Alias"], monitor.device["Address"]),
             _("Connected:") + " " + monitor.interface, monitor]
        )

    def monitor_removed(self, parent, monitor):
        for row in self.liststore:
            titer = row.iter
            (val,) = self.liststore.get(titer, 0)

            if val == monitor.device["Address"]:
                self.liststore.set(titer, 1, self.get_caption(monitor.device["Alias"], monitor.device["Address"]), 2,
                                   _("Not Connected"), 3, None)
                return


class NetUsage(AppletPlugin, GObject.GObject):
    __depends__ = ["Menu"]
    __icon__ = "network-wireless"
    __description__ = _("Allows you to monitor your (mobile broadband) network traffic usage. Useful for limited "
                        "data access plans. This plugin tracks every device seperately.")
    __author__ = "Walmis"
    __autoload__ = False
    __gsignals__ = {
        'monitor-added': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'monitor-removed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        # monitor, tx, rx
        'stats': (GObject.SignalFlags.NO_HOOKS, None,
                  (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    _any_network = None

    def on_load(self):
        GObject.GObject.__init__(self)
        self.monitors = []

        self._any_network = AnyNetwork()
        self._any_network.connect_signal('property-changed', self._on_network_property_changed)

        self.parent.Plugins.Menu.add(self, 84, text=_("Network _Usage"), icon_name="network-wireless",
                                     tooltip=_("Shows network traffic usage"), callback=self.activate_ui)

    def _on_network_property_changed(self, _network, key, value, path):
        if key == "Interface" and value != "":
            d = Device(path)
            self.monitor_interface(Monitor, d, value)

    def activate_ui(self):
        Dialog(self)

    def on_unload(self):
        del self._any_network
        self.parent.Plugins.Menu.unregister(self)

    def monitor_interface(self, montype, *args):
        m = montype(*args)
        self.monitors.append(m)
        m.connect("stats", self.on_stats)
        m.connect("disconnected", self.on_monitor_disconnected)
        self.emit("monitor-added", m)

    def on_ppp_connected(self, device, rfcomm, ppp_port):
        self.monitor_interface(Monitor, device, ppp_port)

    def on_monitor_disconnected(self, monitor):
        self.monitors.remove(monitor)
        self.emit("monitor-removed", monitor)

    def on_stats(self, monitor, tx, rx):
        self.emit("stats", monitor, tx, rx)

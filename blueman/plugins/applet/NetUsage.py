from html import escape
import time
import datetime
from gettext import gettext as _, ngettext
import logging
from typing import List, Any, Optional

from blueman.Functions import *
from blueman.main.Builder import Builder
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config
from blueman.bluez.Device import Device
from blueman.bluez.Network import AnyNetwork
from gi.repository import GObject
from gi.repository import GLib

import gi

from blueman.plugins.applet.PPPSupport import PPPConnectedListener
from blueman.bluemantyping import GSignals

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Pango


class MonitorBase(GObject.GObject):
    __gsignals__: GSignals = {
        'disconnected': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'stats': (GObject.SignalFlags.NO_HOOKS, None, (int, int)),
    }

    def __init__(self, device: Device, interface: str):
        super().__init__()

        self.interface = interface
        self.device = device
        self.general_config = Config("org.blueman.general")
        self.config = Config("org.blueman.plugins.netusage", f"/org/blueman/plugins/netusages/{device['Address']}/")

        self.last_tx = 0
        self.last_rx = 0

    # tx and rx must be cumulative absolute values
    def update_stats(self, tx: int, rx: int) -> None:
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

    def disconnect_monitor(self) -> None:
        self.emit("disconnected")


class Monitor(MonitorBase):
    def __init__(self, device: Device, interface: str):
        super().__init__(device, interface)
        self.poller = None
        self.ppp_port = None

        self.poller = GLib.timeout_add(5000, self.poll_stats)

    def __del__(self) -> None:
        logging.debug("deleting monitor")

    def poll_stats(self) -> bool:
        try:
            with open(f"/sys/class/net/{self.interface}/statistics/tx_bytes") as f:
                tx = int(f.readline())

            with open(f"/sys/class/net/{self.interface}/statistics/rx_bytes") as f:
                rx = int(f.readline())
        except OSError:
            self.poller = None
            self.ppp_port = None
            self.disconnect_monitor()
            return False

        self.update_stats(tx, rx)

        return True


class Dialog:
    running = False

    def __init__(self, plugin: "NetUsage"):
        if not Dialog.running:
            Dialog.running = True
        else:
            return
        self.plugin = plugin
        builder = Builder("net-usage.ui")

        self.dialog = builder.get_widget("dialog", Gtk.Dialog)
        self.dialog.connect("response", self.on_response)
        cr1 = Gtk.CellRendererText()
        cr1.props.ellipsize = Pango.EllipsizeMode.END

        self._handlerids: List[int] = []
        self._handlerids.append(plugin.connect("monitor-added", self.monitor_added))
        self._handlerids.append(plugin.connect("monitor-removed", self.monitor_removed))
        self._handlerids.append(plugin.connect("stats", self.on_stats))

        cr2 = Gtk.CellRendererText()
        cr2.props.sensitive = False
        cr2.props.style = Pango.Style.ITALIC

        self.liststore = Gtk.ListStore(str, str, str, object)

        self.e_ul = builder.get_widget("e_ul", Gtk.Entry)
        self.e_dl = builder.get_widget("e_dl", Gtk.Entry)
        self.e_total = builder.get_widget("e_total", Gtk.Entry)

        self.l_started = builder.get_widget("l_started", Gtk.Label)
        self.l_duration = builder.get_widget("l_duration", Gtk.Label)

        self.b_reset = builder.get_widget("b_reset", Gtk.Button)
        self.b_reset.connect("clicked", self.on_reset)

        self.cb_device = builder.get_widget("cb_device", Gtk.ComboBox)
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
            d = Gtk.MessageDialog(parent=self.dialog, modal=True, type=Gtk.MessageType.INFO,
                                  buttons=Gtk.ButtonsType.CLOSE, text=msg)
            d.props.icon_name = "blueman"
            d.run()
            d.destroy()
            self.on_response(None, None)
            return

        self.dialog.show()

    def on_response(self, _dialog: Optional[Gtk.Dialog], _response: Optional[int]) -> None:
        for sigid in self._handlerids:
            self.plugin.disconnect(sigid)
        self._handlerids = []
        Dialog.running = False
        self.dialog.destroy()

    def update_time(self) -> None:
        time = self.config["time"]
        if time:
            self.datetime = datetime.datetime.fromtimestamp(time)

            self.l_started.props.label = str(self.datetime)

            delta = datetime.datetime.now() - self.datetime

            d = ngettext("day", "days", delta.days)
            h = ngettext("hour", "hours", delta.seconds // 3600)
            m = ngettext("minute", "minutes", delta.seconds % 3600 // 60)

            self.l_duration.props.label = _("%d %s %d %s and %d %s") % (
                delta.days, d, delta.seconds // 3600, h, delta.seconds % 3600 // 60, m)
        else:
            self.l_started.props.label = _("Unknown")
            self.l_duration.props.label = _("Unknown")

    def on_selection_changed(self, cb: Gtk.ComboBox) -> None:
        titer = cb.get_active_iter()
        assert titer is not None
        (addr,) = self.liststore.get(titer, 0)
        self.config = Config("org.blueman.plugins.netusage", f"/org/blueman/plugins/netusages/{addr}/")
        self.update_counts(self.config["tx"], self.config["rx"])
        self.update_time()

    def get_caption(self, name: str, address: str) -> str:
        return f"{escape(name)}\n<small>{address}</small>"

    def update_counts(self, tx: int, rx: int) -> None:
        tx = int(tx)
        rx = int(rx)

        (num, suffix) = format_bytes(tx)
        self.e_ul.props.text = f"{num:.2f} {suffix}"

        (num, suffix) = format_bytes(rx)
        self.e_dl.props.text = f"{num:.2f} {suffix}"

        (num, suffix) = format_bytes(int(tx) + int(rx))
        self.e_total.props.text = f"{num:.2f} {suffix}"

        self.update_time()

    def on_reset(self, _button: Gtk.Button) -> None:
        d = Gtk.MessageDialog(parent=self.dialog, modal=True, type=Gtk.MessageType.QUESTION,
                              buttons=Gtk.ButtonsType.YES_NO,
                              text=_("Are you sure you want to reset the counter?"))
        res = d.run()
        d.destroy()
        if res == Gtk.ResponseType.YES:
            self.config["rx"] = 0
            self.config["tx"] = 0
            self.config["time"] = int(time.time())

            self.update_counts(0, 0)

    def on_stats(self, _parent: "NetUsage", monitor: Monitor, tx: int, rx: int) -> None:
        titer = self.cb_device.get_active_iter()
        assert titer is not None
        (mon,) = self.liststore.get(titer, 3)
        if mon == monitor:
            self.update_counts(tx, rx)

    def monitor_added(self, _parent: "NetUsage", monitor: Monitor) -> None:
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

    def monitor_removed(self, _parent: "NetUsage", monitor: Monitor) -> None:
        for row in self.liststore:
            titer = row.iter
            (val,) = self.liststore.get(titer, 0)

            if val == monitor.device["Address"]:
                self.liststore.set(titer, 1, self.get_caption(monitor.device["Alias"], monitor.device["Address"]), 2,
                                   _("Not Connected"), 3, None)
                return


class NetUsage(AppletPlugin, GObject.GObject, PPPConnectedListener):
    __depends__ = ["Menu"]
    __icon__ = "network-wireless-symbolic"
    __description__ = _("Allows you to monitor your (mobile broadband) network traffic usage. Useful for limited "
                        "data access plans. This plugin tracks every device seperately.")
    __author__ = "Walmis"
    __autoload__ = False
    __gsignals__: GSignals = {
        'monitor-added': (GObject.SignalFlags.NO_HOOKS, None, (Monitor,)),
        'monitor-removed': (GObject.SignalFlags.NO_HOOKS, None, (Monitor,)),
        # monitor, tx, rx
        'stats': (GObject.SignalFlags.NO_HOOKS, None, (Monitor, int, int)),
    }

    _any_network = None

    def on_load(self) -> None:
        GObject.GObject.__init__(self)
        self.monitors: List[Monitor] = []

        self._any_network = AnyNetwork()
        self._any_network.connect_signal('property-changed', self._on_network_property_changed)

        self.parent.Plugins.Menu.add(self, 84, text=_("Network _Usage"), icon_name="network-wireless-symbolic",
                                     tooltip=_("Shows network traffic usage"), callback=self.activate_ui)

    def _on_network_property_changed(self, _network: AnyNetwork, key: str, value: Any, path: str) -> None:
        if key == "Interface" and value != "":
            d = Device(obj_path=path)
            self.monitor_interface(d, value)

    def activate_ui(self) -> None:
        Dialog(self)

    def on_unload(self) -> None:
        del self._any_network
        self.parent.Plugins.Menu.unregister(self)

    def monitor_interface(self, device: Device, interface: str) -> None:
        m = Monitor(device, interface)
        self.monitors.append(m)
        m.connect("stats", self.on_stats)
        m.connect("disconnected", self.on_monitor_disconnected)
        self.emit("monitor-added", m)

    def on_ppp_connected(self, device: Device, _rfcomm: str, ppp_port: str) -> None:
        self.monitor_interface(device, ppp_port)

    def on_monitor_disconnected(self, monitor: Monitor) -> None:
        self.monitors.remove(monitor)
        self.emit("monitor-removed", monitor)

    def on_stats(self, monitor: Monitor, tx: int, rx: int) -> None:
        self.emit("stats", monitor, tx, rx)

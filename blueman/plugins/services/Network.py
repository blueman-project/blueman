from gettext import gettext as _
from random import randint
import logging
import ipaddress
from typing import List, Tuple, cast, Union, TYPE_CHECKING

from blueman.Functions import have, get_local_interfaces
from blueman.main.Builder import Builder
from blueman.plugins.ServicePlugin import ServicePlugin
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler, UdhcpdHandler
from blueman.main.Config import Config
from blueman.main.DBusProxies import Mechanism
from blueman.main.DBusProxies import AppletService
from blueman.gui.CommonUi import ErrorDialog

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, GObject

if TYPE_CHECKING:
    from typing_extensions import Literal


class Network(ServicePlugin):
    __plugin_info__ = (_("Network"), "network-workgroup")

    def on_load(self, container: Gtk.Box) -> None:

        self._builder = Builder("services-network.ui")
        self.widget = self._builder.get_widget("network_frame", Gtk.Widget)

        container.pack_start(self.widget, True, True, 0)

        self.interfaces: List[Tuple[str, ipaddress.IPv4Interface]] = []
        netifs = get_local_interfaces()
        for iface in netifs:
            if iface != "lo" and iface != "pan1":
                logging.info(iface)
                ipiface = ipaddress.ip_interface('/'.join(cast(Tuple[str, str], netifs[iface])))
                self.interfaces.append((iface, ipiface))

        self.setup_network()
        try:
            self.ip_check()
        except (ValueError, ipaddress.AddressValueError) as e:
            logging.exception(e)

    def on_enter(self) -> None:
        self.widget.props.visible = True

    def on_leave(self) -> None:
        self.widget.props.visible = False

    def on_apply(self) -> None:

        if self.on_query_apply_state():
            logging.info("network apply")

            m = Mechanism()
            nap_enable = self._builder.get_widget("nap-enable", Gtk.CheckButton)
            if nap_enable.props.active:

                if self._builder.get_widget("r_dhcpd", Gtk.RadioButton).props.active:
                    stype = "DhcpdHandler"
                elif self._builder.get_widget("r_dnsmasq", Gtk.RadioButton).props.active:
                    stype = "DnsMasqHandler"
                elif self._builder.get_widget("r_udhcpd", Gtk.RadioButton).props.active:
                    stype = "UdhcpdHandler"

                net_ip = self._builder.get_widget("net_ip", Gtk.Entry)

                try:
                    m.EnableNetwork('(sss)', net_ip.props.text, "255.255.255.0", stype)

                    if not self.Config["nap-enable"]:
                        self.Config["nap-enable"] = True
                except Exception as e:
                    parent = self.widget.get_toplevel()
                    assert isinstance(parent, Gtk.Container)
                    d = ErrorDialog("<b>Failed to apply network settings</b>", excp=e, parent=parent)

                    d.run()
                    d.destroy()
                    return
            else:
                self.Config["nap-enable"] = False
                m.DisableNetwork()

            self.clear_options()

    def ip_check(self) -> None:
        entry = self._builder.get_widget("net_ip", Gtk.Entry)
        try:
            nap_ipiface = ipaddress.ip_interface('/'.join((entry.props.text, '255.255.255.0')))
        except (ValueError, ipaddress.AddressValueError):
            entry.props.secondary_icon_name = "dialog-error"
            entry.props.secondary_icon_tooltip_text = _("Invalid IP address")
            raise

        for iface, ipiface in self.interfaces:
            if nap_ipiface.ip == ipiface.ip:
                error_message = _("IP address conflicts with interface %s which has the same address" % iface)
                tooltip_text = error_message
                entry.props.secondary_icon_name = "dialog-error"
                entry.props.secondary_icon_tooltip_text = tooltip_text
                raise ValueError(error_message)

            elif nap_ipiface.network == ipiface.network:
                tooltip_text = _(
                    "IP address overlaps with subnet of interface %s, which has the following configuration  %s/%s\n"
                    "This may cause incorrect network behavior" % (iface, ipiface.ip, ipiface.netmask))
                entry.props.secondary_icon_name = "dialog-warning"
                entry.props.secondary_icon_tooltip_text = tooltip_text
                return

        entry.props.secondary_icon_name = None

    def on_query_apply_state(self) -> Union[bool, "Literal[-1]"]:
        opts = self.get_options()
        if not opts:
            return False

        if "ip" in opts:
            try:
                self.ip_check()
            except (ValueError, ipaddress.AddressValueError) as e:
                logging.exception(e)
                return -1

        return True

    def setup_network(self) -> None:
        self.Config = Config("org.blueman.network")

        nap_enable = self._builder.get_widget("nap-enable", Gtk.CheckButton)
        r_dnsmasq = self._builder.get_widget("r_dnsmasq", Gtk.RadioButton)
        r_dhcpd = self._builder.get_widget("r_dhcpd", Gtk.RadioButton)
        r_udhcpd = self._builder.get_widget("r_udhcpd", Gtk.RadioButton)
        net_ip = self._builder.get_widget("net_ip", Gtk.Entry)
        rb_nm = self._builder.get_widget("rb_nm", Gtk.RadioButton)
        rb_blueman = self._builder.get_widget("rb_blueman", Gtk.RadioButton)
        rb_dun_nm = self._builder.get_widget("rb_dun_nm", Gtk.RadioButton)
        rb_dun_blueman = self._builder.get_widget("rb_dun_blueman", Gtk.RadioButton)

        nap_frame = self._builder.get_widget("nap_frame", Gtk.Frame)
        warning = self._builder.get_widget("warning", Gtk.Box)

        if not self.Config["nap-enable"]:
            nap_frame.props.sensitive = False

        nc = NetConf.get_default()
        if nc.ip4_address is not None:
            # previously we stored a bytearray, ipaddress module reads both
            net_ip.props.text = str(ipaddress.ip_address(nc.ip4_address))
            nap_enable.props.active = True
        else:
            net_ip.props.text = "10.%d.%d.1" % (randint(0, 255), randint(0, 255))

        if nc.get_dhcp_handler() is None:
            nap_frame.props.sensitive = False
            nap_enable.props.active = False
            r_dnsmasq.props.active = True
            self.Config["nap-enable"] = False

        have_dhcpd = have("dhcpd3") or have("dhcpd")
        have_dnsmasq = have("dnsmasq")
        have_udhcpd = have("udhcpd")

        if nc.get_dhcp_handler() == DnsMasqHandler and have_dnsmasq:
            r_dnsmasq.props.active = True
        elif nc.get_dhcp_handler() == DhcpdHandler and have_dhcpd:
            r_dhcpd.props.active = True
        elif nc.get_dhcp_handler() == UdhcpdHandler and have_udhcpd:
            r_udhcpd.props.active = True
        else:
            r_dnsmasq.props.active = True

        if not have_dnsmasq and not have_dhcpd and not have_udhcpd:
            nap_frame.props.sensitive = False
            warning.props.visible = True
            warning.props.sensitive = True
            nap_enable.props.sensitive = False
            self.Config["nap-enable"] = False

        if not have_dnsmasq:
            r_dnsmasq.props.sensitive = False
            r_dnsmasq.props.active = False

        if not have_dhcpd:
            r_dhcpd.props.sensitive = False
            r_dhcpd.props.active = False

        if not have_udhcpd:
            r_udhcpd.props.sensitive = False
            r_udhcpd.props.active = False

        r_dnsmasq.connect("toggled", lambda x: self.option_changed_notify("dnsmasq"))
        r_dhcpd.connect("toggled", lambda x: self.option_changed_notify("dhcpd"))
        r_udhcpd.connect("toggled", lambda x: self.option_changed_notify("udhcpd"))

        net_ip.connect("changed", lambda x: self.option_changed_notify("ip", False))
        nap_enable.connect("toggled", lambda x: self.option_changed_notify("nap_enable"))

        self.Config.bind_to_widget("nap-enable", nap_enable, "active", Gio.SettingsBindFlags.GET)

        nap_enable.bind_property("active", nap_frame, "sensitive", GObject.BindingFlags.DEFAULT)

        applet = AppletService()

        avail_plugins = applet.QueryAvailablePlugins()
        active_plugins = applet.QueryPlugins()

        def dun_support_toggled(rb: Gtk.RadioButton, x: str) -> None:
            if rb.props.active and x == "nm":
                applet.SetPluginConfig('(sb)', "PPPSupport", False)
                applet.SetPluginConfig('(sb)', "NMDUNSupport", True)
            elif rb.props.active and x == "blueman":
                applet.SetPluginConfig('(sb)', "NMDUNSupport", False)
                applet.SetPluginConfig('(sb)', "PPPSupport", True)

        def pan_support_toggled(rb: Gtk.RadioButton, x: str) -> None:
            if rb.props.active and x == "nm":
                applet.SetPluginConfig('(sb)', "DhcpClient", False)
                applet.SetPluginConfig('(sb)', "NMPANSupport", True)

            elif rb.props.active and x == "blueman":
                applet.SetPluginConfig('(sb)', "NMPANSupport", False)
                applet.SetPluginConfig('(sb)', "DhcpClient", True)

        if "PPPSupport" in active_plugins:
            rb_dun_blueman.props.active = True

        if "NMDUNSupport" in avail_plugins:
            rb_dun_nm.props.sensitive = True
        else:
            rb_dun_nm.props.sensitive = False
            rb_dun_nm.props.tooltip_text = _("Not currently supported with this setup")

        if "DhcpClient" in active_plugins:
            rb_blueman.props.active = True

        if "NMPANSupport" in avail_plugins:
            rb_nm.props.sensitive = True
        else:
            rb_nm.props.sensitive = False
            rb_nm.props.tooltip_text = _("Not currently supported with this setup")

        if "NMPANSupport" in active_plugins:
            rb_nm.props.active = True

        if "NMDUNSupport" in active_plugins:
            rb_dun_nm.props.active = True

        rb_nm.connect("toggled", pan_support_toggled, "nm")
        rb_blueman.connect("toggled", pan_support_toggled, "blueman")

        rb_dun_nm.connect("toggled", dun_support_toggled, "nm")
        rb_dun_blueman.connect("toggled", dun_support_toggled, "blueman")

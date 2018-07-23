# coding=utf-8
from random import randint
from locale import bind_textdomain_codeset
import logging
import ipaddress

from blueman.Constants import *
from blueman.Functions import have
from _blueman import get_net_interfaces, get_net_address, get_net_netmask
from blueman.plugins.ServicePlugin import ServicePlugin
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler, UdhcpdHandler
from blueman.main.Config import Config
from blueman.main.DBusProxies import Mechanism
from blueman.main.DBusProxies import AppletService
from blueman.gui.CommonUi import ErrorDialog

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk


class Network(ServicePlugin):
    __plugin_info__ = (_("Network"), "network-workgroup")

    def on_load(self, container):

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")
        self.Builder.add_from_file(UI_PATH + "/services-network.ui")
        self.widget = self.Builder.get_object("network_frame")

        container.pack_start(self.widget, True, True, 0)

        self.interfaces = []
        for iface in get_net_interfaces():
            if iface != "lo" and iface != "pan1":
                logging.info(iface)
                ipiface = ipaddress.ip_interface('/'.join((get_net_address(iface), get_net_netmask(iface))))
                self.interfaces.append((iface, ipiface))

        self.setup_network()
        try:
            self.ip_check()
        except (ValueError, ipaddress.AddressValueError) as e:
            logging.exception(e)
        return _("Network"), "network-workgroup"

    def on_enter(self):
        self.widget.props.visible = True

    def on_leave(self):
        self.widget.props.visible = False

    def on_apply(self):

        if self.on_query_apply_state():
            logging.info("network apply")

            m = Mechanism()
            nap_enable = self.Builder.get_object("nap-enable")
            if nap_enable.props.active:

                if self.Builder.get_object("r_dhcpd").props.active:
                    stype = "DhcpdHandler"
                elif self.Builder.get_object("r_dnsmasq").props.active:
                    stype = "DnsMasqHandler"
                elif self.Builder.get_object("r_udhcpd").props.active:
                    stype = "UdhcpdHandler"

                net_ip = self.Builder.get_object("net_ip")

                try:
                    m.EnableNetwork('(sss)', net_ip.props.text, "255.255.255.0", stype)

                    if not self.Config["nap-enable"]:
                        self.Config["nap-enable"] = True
                except Exception as e:
                    d = ErrorDialog("<b>Failed to apply network settings</b>",
                                    excp=e, parent=self.widget.get_toplevel())

                    d.run()
                    d.destroy()
                    return
            else:
                self.Config["nap-enable"] = False
                m.DisableNetwork()

            self.clear_options()

    def ip_check(self):
        entry = self.Builder.get_object("net_ip")
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

    def on_query_apply_state(self):
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

    def setup_network(self):
        self.Config = Config("org.blueman.network")

        nap_enable = self.Builder.get_object("nap-enable")
        r_dnsmasq = self.Builder.get_object("r_dnsmasq")
        r_dhcpd = self.Builder.get_object("r_dhcpd")
        r_udhcpd = self.Builder.get_object("r_udhcpd")
        net_ip = self.Builder.get_object("net_ip")
        rb_nm = self.Builder.get_object("rb_nm")
        rb_blueman = self.Builder.get_object("rb_blueman")
        rb_dun_nm = self.Builder.get_object("rb_dun_nm")
        rb_dun_blueman = self.Builder.get_object("rb_dun_blueman")

        nap_frame = self.Builder.get_object("nap_frame")
        warning = self.Builder.get_object("warning")

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

        nap_enable.bind_property("active", nap_frame, "sensitive", 0)

        applet = AppletService()

        avail_plugins = applet.QueryAvailablePlugins()
        active_plugins = applet.QueryPlugins()

        def dun_support_toggled(rb, x):
            if rb.props.active and x == "nm":
                applet.SetPluginConfig('(sb)', "PPPSupport", False)
                applet.SetPluginConfig('(sb)', "NMDUNSupport", True)
            elif rb.props.active and x == "blueman":
                applet.SetPluginConfig('(sb)', "NMDUNSupport", False)
                applet.SetPluginConfig('(sb)', "PPPSupport", True)

        def pan_support_toggled(rb, x):
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

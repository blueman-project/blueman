from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk
from blueman.Constants import *
from blueman.Functions import have, dprint, mask_ip4_address
from _blueman import get_net_interfaces, get_net_address, get_net_netmask
from socket import inet_aton, inet_ntoa
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler
from blueman.main.Config import Config
from blueman.main.Mechanism import Mechanism
from blueman.main.AppletService import AppletService
from blueman.gui.Dialogs import NetworkErrorDialog
from random import randint


class Network(ServicePlugin):
    __plugin_info__ = (_("Network"), "network-workgroup")

    def on_load(self, container):

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        self.Builder.add_from_file(UI_PATH + "/services-network.ui")
        self.widget = self.Builder.get_object("network")

        container.pack_start(self.widget, True, True, 0)

        self.interfaces = []
        for iface in get_net_interfaces():
            if iface != "lo" and iface != "pan1":
                print(iface)
                ip = inet_aton(get_net_address(iface))
                mask = inet_aton(get_net_netmask(iface))
                self.interfaces.append((iface, ip, mask, mask_ip4_address(ip, mask)))

        self.setup_network()
        try:
            self.ip_check()
        except:
            pass
        return (_("Network"), "network-workgroup")

    def on_enter(self):
        self.widget.props.visible = True

    def on_leave(self):
        self.widget.props.visible = False

    def on_apply(self):

        if self.on_query_apply_state() == True:
            dprint("network apply")

            m = Mechanism()
            nap_enable = self.Builder.get_object("nap-enable")
            if nap_enable.props.active:

                r_dnsmasq = self.Builder.get_object("r_dnsmasq")
                if r_dnsmasq.props.active:
                    stype = "DnsMasqHandler"
                else:
                    stype = "DhcpdHandler"

                net_ip = self.Builder.get_object("net_ip")
                net_nat = self.Builder.get_object("net_nat")

                try:
                    m.EnableNetwork(inet_aton(net_ip.props.text), inet_aton("255.255.255.0"), stype)
                    if not self.Config["nap-enable"]:
                        self.Config["nap-enable"] = True
                except Exception as e:
                    d = NetworkErrorDialog(e)

                    d.run()
                    d.destroy()
                    return
            else:
                self.Config["nap-enable"] = False
                m.DisableNetwork()

            self.clear_options()


    def ip_check(self):
        e = self.Builder.get_object("net_ip")
        address = e.props.text
        try:
            if address.count(".") != 3:
                raise Exception
            a = inet_aton(address)
        except:
            e.props.secondary_icon_name = "dialog-error"
            e.props.secondary_icon_tooltip_text = _("Invalid IP address")
            raise

        a_netmask = inet_aton("255.255.255.0")

        a_masked = mask_ip4_address(a, a_netmask)

        for iface, ip, netmask, masked in self.interfaces:
            # print mask_ip4_address(a, netmask).encode("hex_codec"), masked.encode("hex_codec")

            if a == ip:
                e.props.secondary_icon_name = "dialog-error"
                e.props.secondary_icon_tooltip_text = _("IP address conflicts with interface %s which has the same address" % iface)
                raise Exception

            elif mask_ip4_address(a, netmask) == masked:
                e.props.secondary_icon_name = "dialog-warning"
                e.props.secondary_icon_tooltip_text = _("IP address overlaps with subnet of interface"
                                                        " %s, which has the following configuration %s/%s\nThis may cause incorrect network behavior" % (iface, inet_ntoa(ip), inet_ntoa(netmask)))
                return

        e.props.secondary_icon_name = None

    def on_query_apply_state(self):
        changed = False
        opts = self.get_options()
        if opts == []:
            return False
        else:
            if "ip" in opts:
                try:
                    self.ip_check()
                except Exception as e:
                    print(e)
                    return -1

            return True


    def setup_network(self):
        self.Config = Config("org.blueman.network")

        gn_enable = self.Builder.get_object("gn-enable")
        # latest bluez does not support GN, apparently
        gn_enable.props.visible = False

        nap_enable = self.Builder.get_object("nap-enable")
        r_dnsmasq = self.Builder.get_object("r_dnsmasq")
        r_dhcpd = self.Builder.get_object("r_dhcpd")
        net_ip = self.Builder.get_object("net_ip")
        net_nat = self.Builder.get_object("net_nat")
        rb_nm = self.Builder.get_object("rb_nm")
        rb_blueman = self.Builder.get_object("rb_blueman")
        rb_dun_nm = self.Builder.get_object("rb_dun_nm")
        rb_dun_blueman = self.Builder.get_object("rb_dun_blueman")

        nap_frame = self.Builder.get_object("nap_frame")
        warning = self.Builder.get_object("warning")

        rb_blueman.props.active = self.Config["dhcp-client"]

        if not self.Config["nap-enable"]:
            nap_frame.props.sensitive = False

        nc = NetConf.get_default()
        if nc.ip4_address != None:
            net_ip.props.text = inet_ntoa(nc.ip4_address)
            nap_enable.props.active = True
        else:
            net_ip.props.text = "10.%d.%d.1" % (randint(0, 255), randint(0, 255))

        #if ns["masq"] != 0:
        #	net_nat.props.active = ns["masq"]

        if nc.get_dhcp_handler() == None:
            nap_frame.props.sensitive = False
            nap_enable.props.active = False
            r_dnsmasq.props.active = True
            self.Config["nap-enable"] = False
        else:
            if nc.get_dhcp_handler() == DnsMasqHandler:
                r_dnsmasq.props.active = True
            else:
                r_dhcpd.props.active = True

        if not have("dnsmasq") and not have("dhcpd3") and not have("dhcpd"):
            nap_frame.props.sensitive = False
            warning.props.visible = True
            warning.props.sensitive = True
            nap_enable.props.sensitive = False
            self.Config["nap-enable"] = False

        if not have("dnsmasq"):
            r_dnsmasq.props.sensitive = False
            r_dnsmasq.props.active = False
            r_dhcpd.props.active = True

        if not have("dhcpd3") and not have("dhcpd"):
            r_dhcpd.props.sensitive = False
            r_dhcpd.props.active = False
            r_dnsmasq.props.active = True

        r_dnsmasq.connect("toggled", lambda x: self.option_changed_notify("dnsmasq"))
        r_dhcpd.connect("toggled", lambda x: self.option_changed_notify("dhcpd"))
        net_nat.connect("toggled", lambda x: self.option_changed_notify("nat"))
        net_ip.connect("changed", lambda x: self.option_changed_notify("ip", False))
        gn_enable.connect("toggled", lambda x: self.option_changed_notify("gn_enable"))
        nap_enable.connect("toggled", lambda x: self.option_changed_notify("nap_enable"))

        self.Config.bind_to_widget("nat", net_nat, "active", Gio.SettingsBindFlags.GET)
        self.Config.bind_to_widget("gn-enable", gn_enable, "active", Gio.SettingsBindFlags.GET)
        self.Config.bind_to_widget("nap-enable", nap_enable, "active", Gio.SettingsBindFlags.GET)

        nap_enable.bind_property("active", nap_frame, "sensitive", 0)

        applet = AppletService()

        avail_plugins = applet.QueryAvailablePlugins()
        active_plugins = applet.QueryPlugins()

        def dun_support_toggled(rb, x):
            if rb.props.active and x == "nm":
                applet.SetPluginConfig("PPPSupport", False)
                applet.SetPluginConfig("NMDUNSupport", True)
            elif rb.props.active and x == "blueman":
                applet.SetPluginConfig("NMDUNSupport", False)
                applet.SetPluginConfig("PPPSupport", True)

        def pan_support_toggled(rb, x):
            if rb.props.active and x == "nm":
                applet.SetPluginConfig("DhcpClient", False)
                applet.SetPluginConfig("NMPANSupport", True)

            elif rb.props.active and x == "blueman":
                applet.SetPluginConfig("NMPANSupport", False)
                applet.SetPluginConfig("DhcpClient", True)


        if "PPPSupport" in active_plugins:
            rb_dun_blueman.props.active = True

        if "NMDUNSupport" in avail_plugins:
            rb_dun_nm.props.sensitive = True
        else:
            rb_dun_nm.props.sensitive = False
            rb_dun_nm.props.tooltip_text = _("Not currently supported with this setup")

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

from gi.repository import Gtk
from blueman.Constants import *
from blueman.Functions import have, dprint, mask_ip4_address
from blueman.Lib import get_net_interfaces, get_net_address, get_net_netmask
from socket import inet_ntoa, inet_aton
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler
from blueman.main.Config import Config
from blueman.main.Mechanism import Mechanism
from blueman.main.AppletService import AppletService
from random import randint


class Network(ServicePlugin):
    __plugin_info__ = (_("Network"), "network-workgroup")

    def on_load(self, container):

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        self.Builder.add_from_file(UI_PATH + "/services-network.ui")
        self.widget = self.Builder.get_object("network")

        self.ignored_keys = []

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

    def on_property_changed(self, netconf, key, value):
        dprint(self.ignored_keys)
        if key in self.ignored_keys:
            self.ignored_keys.remove(key)
            return
        if key == "rb_blueman" or key == "dhcp_client":
            if value:
                self.Builder.get_object("rb_blueman").props.active = True
            else:
                self.Builder.get_object("rb_nm").props.active = True
            return
        if key == "rb_nm":
            return

        if key == "gn_enable":
            self.Builder.get_object(key).props.active = value
            return

        if key == "nap_enable":
            dprint("nap_enable", value)
            self.Builder.get_object(key).props.active = value
            nap_frame = self.Builder.get_object("nap_frame")
            if value:
                nap_frame.props.sensitive = True
            else:
                nap_frame.props.sensitive = False

        if key == "ip":
            self.option_changed_notify(key, False)
        else:
            self.option_changed_notify(key)

    def on_apply(self):

        if self.on_query_apply_state() == True:
            dprint("network apply")

            m = Mechanism()
            nap_enable = self.Builder.get_object("nap_enable")
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

                    if not self.Config.props.nap_enable:  # race condition workaround
                        self.ignored_keys.append("nap_enable")
                    self.Config.props.nap_enable = True
                except Exception as e:
                    lines = str(e).splitlines()

                    d = Gtk.MessageDialog(None, buttons=Gtk.ButtonsType.OK, type=Gtk.MessageType.ERROR)
                    d.props.icon_name = "dialog-error"
                    d.props.text = _("Failed to apply network settings")
                    d.props.secondary_text = lines[-1]
                    d.run()
                    d.destroy()
                    return
            else:
                if self.Config.props.nap_enable:  # race condition workaround
                    self.ignored_keys.append("nap_enable")
                self.Config.props.nap_enable = False
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

        a_netmask = "\xff\xff\xff\0"

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
        self.Config = Config("network")
        self.Config.connect("property-changed", self.on_property_changed)

        gn_enable = self.Builder.get_object("gn_enable")
        # latest bluez does not support GN, apparently
        gn_enable.props.visible = False

        nap_enable = self.Builder.get_object("nap_enable")
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

        rb_blueman.props.active = self.Config.props.dhcp_client
        nap_enable.props.active = self.Config.props.nap_enable
        gn_enable.props.active = self.Config.props.gn_enable

        net_ip.props.text = "10.%d.%d.1" % (randint(0, 255), randint(0, 255))

        if not self.Config.props.nap_enable:
            nap_frame.props.sensitive = False

        nc = NetConf.get_default()
        if nc.ip4_address != None:
            net_ip.props.text = inet_ntoa(nc.ip4_address)
            #if not self.Config.props.nap_enable:
            #	self.ignored_keys.append("nap_enable")
            self.Config.props.nap_enable = True


        #if ns["masq"] != 0:
        #	net_nat.props.active = ns["masq"]

        if nc.get_dhcp_handler() == None:
            nap_frame.props.sensitive = False
            nap_enable.props.active = False
            if self.Config.props.nap_enable or self.Config.props.nap_enable == None:
                self.ignored_keys.append("nap_enable")
            self.Config.props.nap_enable = False


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
            if self.Config.props.nap_enable or self.Config.props.nap_enable == None:
                self.ignored_keys.append("nap_enable")
            self.Config.props.nap_enable = False

        if not have("dnsmasq"):
            r_dnsmasq.props.sensitive = False
            r_dnsmasq.props.active = False
            r_dhcpd.props.active = True

        if not have("dhcpd3") and not have("dhcpd"):
            r_dhcpd.props.sensitive = False
            r_dhcpd.props.active = False
            r_dnsmasq.props.active = True

        r_dnsmasq.connect("toggled", lambda x: self.option_changed_notify("dnsmasq"))

        net_nat.connect("toggled", lambda x: self.on_property_changed(self.Config, "nat", x.props.active))
        net_ip.connect("changed", lambda x: self.on_property_changed(self.Config, "ip", x.props.text))
        gn_enable.connect("toggled", lambda x: setattr(self.Config.props, "gn_enable", x.props.active))
        nap_enable.connect("toggled", lambda x: self.on_property_changed(self.Config, "nap_enable", x.props.active))

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

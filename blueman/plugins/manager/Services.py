from blueman.bluez.BlueZInterface import BlueZInterface
from blueman.plugins.ManagerPlugin import ManagerPlugin
from gi.repository import Gtk

from blueman.Sdp import *
from blueman.Functions import *
from blueman.main.SignalTracker import SignalTracker
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.main.Config import Config
from blueman.main.AppletService import AppletService
from blueman.gui.MessageArea import MessageArea

from blueman.Lib import rfcomm_list


def get_x_icon(icon_name, size):
    ic = get_icon(icon_name, size)
    x = get_icon("blueman-x", size)
    pixbuf = composite_icon(ic, [(x, 0, 0, 255)])

    return pixbuf


class Services(ManagerPlugin):
    connectable_uuids = [HID_SVCLASS_ID, AUDIO_SOURCE_SVCLASS_ID, AUDIO_SINK_SVCLASS_ID, HEADSET_SVCLASS_ID, HANDSFREE_SVCLASS_ID]

    def on_request_menu_items(self, manager_menu, device):
        if BlueZInterface.get_interface_version()[0] < 5:
            return self.on_request_menu_items_bluez4(manager_menu, device)

        items = []
        uuids = device.UUIDs
        appl = AppletService()

        uuids16 = [uuid128_to_uuid16(uuid) for uuid in uuids]

        if set(uuids16) & set(self.connectable_uuids):
            # FIXME: This should only be done once!
            manager_menu.Signals.Handle("bluez", device, manager_menu.service_property_changed, "PropertyChanged")

            if device.get_properties()['Connected']:
                # FIXME: More generic icon
                item = create_menuitem(_("Disconnect"), get_x_icon("mouse", 16))
                manager_menu.Signals.Handle("gobject", item, "activate", manager_menu.on_disconnect, device)
                items.append((item, 100))
            else:
                # FIXME: More generic icon
                item = create_menuitem(_("Connect"), get_icon("mouse", 16))
                manager_menu.Signals.Handle("gobject", item, "activate", manager_menu.on_connect, device)
                items.append((item, 1))

            item.show()

        for name, service in device.Services.items():
            if name == "network":
                manager_menu.Signals.Handle("bluez", service, manager_menu.service_property_changed, "PropertyChanged")
                sprops = service.get_properties()

                if not sprops["Connected"]:
                    for uuid in uuids:
                        uuid16 = uuid128_to_uuid16(uuid)
                        if uuid16 == NAP_SVCLASS_ID or uuid16 == GN_SVCLASS_ID:
                            label = _("Group Network") if uuid16 == GN_SVCLASS_ID else _("Network Access Point")
                            item = create_menuitem(label, get_icon("network-wireless", 16))
                            manager_menu.Signals.Handle("gobject", item, "activate", manager_menu.on_connect,
                                                        device, name, uuid)
                            item.show()
                            items.append((item, 80))
                else:
                    item = create_menuitem(_("Network"), get_x_icon("network-wireless", 16))
                    manager_menu.Signals.Handle("gobject", item, "activate", manager_menu.on_disconnect, device, name)
                    item.show()
                    items.append((item, 101))

                    if "DhcpClient" in appl.QueryPlugins():
                        def renew(x):
                            appl.DhcpClient(sprops["Interface"])

                        item = create_menuitem(_("Renew IP Address"), get_icon("gtk-refresh", 16))
                        manager_menu.Signals.Handle("gobject", item, "activate", renew)
                        item.show()
                        items.append((item, 201))

        return items

    def on_request_menu_items_bluez4(self, manager_menu, device):
        # BlueZ 4 only

        items = []
        uuids = device.UUIDs
        appl = AppletService()

        for name, service in device.Services.items():
            if name == "serial":
                ports_list = rfcomm_list()

                def flt(dev):
                    if dev["dst"] == device.Address and dev["state"] == "connected":
                        return dev["channel"]

                active_ports = map(flt, ports_list)


                def get_port_id(channel):
                    for dev in ports_list:
                        if dev["dst"] == device.Address and dev["state"] == "connected" and dev["channel"] == channel:
                            return dev["id"]

                serial_items = []

                num_ports = 0
                has_dun = False
                try:
                    for port_name, channel, uuid in sdp_get_cached_rfcomm(device.Address):

                        if SERIAL_PORT_SVCLASS_ID in uuid:
                            if name is not None:
                                if channel in active_ports:
                                    item = create_menuitem(port_name, get_x_icon("blueman-serial", 16))
                                    manager_menu.Signals.Handle("gobject",
                                                                item,
                                                                "activate",
                                                                manager_menu.on_disconnect,
                                                                device, name,
                                                                "/dev/rfcomm%d" % get_port_id(channel))
                                    item.show()
                                    items.append((item, 150))
                                else:
                                    item = create_menuitem(port_name, get_icon("blueman-serial", 16))
                                    manager_menu.Signals.Handle("gobject",
                                                                item,
                                                                "activate",
                                                                manager_menu.on_connect,
                                                                device, name,
                                                                channel)
                                    item.show()
                                    serial_items.append(item)


                        elif DIALUP_NET_SVCLASS_ID in uuid:
                            if name is not None:
                                if channel in active_ports:
                                    item = create_menuitem(port_name, get_x_icon("modem", 16))
                                    manager_menu.Signals.Handle("gobject",
                                                                item,
                                                                "activate",
                                                                manager_menu.on_disconnect,
                                                                device,
                                                                name,
                                                                "/dev/rfcomm%d" % get_port_id(channel))
                                    item.show()
                                    items.append((item, 150))
                                else:
                                    item = create_menuitem(port_name, get_icon("modem", 16))
                                    manager_menu.Signals.Handle("gobject",
                                                                item,
                                                                "activate",
                                                                manager_menu.on_connect,
                                                                device,
                                                                name,
                                                                channel)
                                    item.show()
                                    serial_items.append(item)
                                    has_dun = True

                except KeyError:
                    for uuid in uuids:
                        uuid16 = uuid128_to_uuid16(uuid)
                        if uuid16 == DIALUP_NET_SVCLASS_ID:
                            item = create_menuitem(_("Dialup Service"), get_icon("modem", 16))
                            manager_menu.Signals.Handle("gobject",
                                                        item,
                                                        "activate",
                                                        manager_menu.on_connect,
                                                        device,
                                                        name,
                                                        uuid)
                            item.show()
                            serial_items.append(item)
                            has_dun = True

                        if uuid16 == SERIAL_PORT_SVCLASS_ID:
                            item = create_menuitem(_("Serial Service"),
                                                   get_icon("blueman-serial",
                                                            16))
                            manager_menu.Signals.Handle("gobject",
                                                        item,
                                                        "activate",
                                                        manager_menu.on_connect,
                                                        device, name, uuid)
                            item.show()
                            serial_items.append(item)

                    for dev in ports_list:
                        if dev["dst"] == device.Address:
                            if dev["state"] == "connected":
                                devname = _("Serial Port %s") % "rfcomm%d" % dev["id"]

                                item = create_menuitem(devname, get_x_icon("modem", 16))
                                manager_menu.Signals.Handle("gobject",
                                                            item,
                                                            "activate",
                                                            manager_menu.on_disconnect,
                                                            device, name,
                                                            "/dev/rfcomm%d" % dev["id"])
                                items.append((item, 120))
                                item.show()

                def open_settings(i, device):
                    from blueman.gui.GsmSettings import GsmSettings

                    d = GsmSettings(device.Address)
                    d.run()
                    d.destroy()

                if has_dun and "PPPSupport" in appl.QueryPlugins():
                    item = Gtk.SeparatorMenuItem()
                    item.show()
                    serial_items.append(item)

                    item = create_menuitem(_("Dialup Settings"),
                                           get_icon("gtk-preferences", 16))
                    serial_items.append(item)
                    item.show()
                    manager_menu.Signals.Handle("gobject", item,
                                                "activate", open_settings,
                                                device)

                if len(serial_items) > 1:
                    sub = Gtk.Menu()
                    sub.show()

                    item = create_menuitem(_("Serial Ports"), get_icon("modem", 16))
                    item.set_submenu(sub)
                    item.show()
                    items.append((item, 90))

                    for item in serial_items:
                        sub.append(item)

                else:
                    for item in serial_items:
                        items.append((item, 80))


            elif name == "network":
                manager_menu.Signals.Handle("bluez",
                                            service,
                                            manager_menu.service_property_changed,
                                            "PropertyChanged")

                sprops = service.get_properties()

                if not sprops["Connected"]:

                    for uuid in uuids:
                        uuid16 = uuid128_to_uuid16(uuid)
                        if uuid16 == GN_SVCLASS_ID:
                            item = create_menuitem(_("Group Network"),
                                                   get_icon("network-wireless", 16))
                            manager_menu.Signals.Handle("gobject",
                                                        item,
                                                        "activate",
                                                        manager_menu.on_connect,
                                                        device, name, uuid)
                            item.show()
                            items.append((item, 80))

                        if uuid16 == NAP_SVCLASS_ID:
                            item = create_menuitem(_("Network Access Point"),
                                                   get_icon("network-wireless", 16))
                            manager_menu.Signals.Handle("gobject",
                                                        item,
                                                        "activate",
                                                        manager_menu.on_connect,
                                                        device, name, uuid)
                            item.show()
                            items.append((item, 81))


                else:
                    item = create_menuitem(_("Network"), get_x_icon("network-wireless", 16))
                    manager_menu.Signals.Handle("gobject", item,
                                                "activate",
                                                manager_menu.on_disconnect,
                                                device, name)
                    item.show()
                    items.append((item, 101))

                    if "DhcpClient" in appl.QueryPlugins():
                        def renew(x):
                            appl.DhcpClient(sprops["Interface"])

                        item = create_menuitem(_("Renew IP Address"), get_icon("gtk-refresh", 16))
                        manager_menu.Signals.Handle("gobject", item, "activate", renew)
                        item.show()
                        items.append((item, 201))

            elif name == "input":
                manager_menu.Signals.Handle("bluez",
                                            service,
                                            manager_menu.service_property_changed,
                                            "PropertyChanged")
                sprops = service.get_properties()
                if sprops["Connected"]:
                    item = create_menuitem(_("Input Service"), get_x_icon("mouse", 16))
                    manager_menu.Signals.Handle("gobject",
                                                item,
                                                "activate",
                                                manager_menu.on_disconnect,
                                                device, name)
                    items.append((item, 100))

                else:
                    item = create_menuitem(_("Input Service"), get_icon("mouse", 16))
                    manager_menu.Signals.Handle("gobject",
                                                item,
                                                "activate",
                                                manager_menu.on_connect,
                                                device, name)
                    items.append((item, 1))

                item.show()


            elif name == "headset":
                sprops = service.get_properties()

                if sprops["Connected"]:
                    item = create_menuitem(_("Headset Service"),
                                           get_icon("blueman-handsfree", 16))
                    manager_menu.Signals.Handle("gobject",
                                                item, "activate",
                                                manager_menu.on_disconnect,
                                                device, name)
                    items.append((item, 110))
                else:
                    item = create_menuitem(_("Headset Service"),
                                           get_icon("blueman-handsfree", 16))
                    manager_menu.Signals.Handle("gobject", item,
                                                "activate",
                                                manager_menu.on_connect,
                                                device, name)
                    items.append((item, 10))

                item.show()



            elif name == "audiosink":
                sprops = service.get_properties()

                if sprops["Connected"]:
                    item = create_menuitem(_("Audio Sink"), get_icon("blueman-headset", 16))
                    manager_menu.Signals.Handle("gobject",
                                                item,
                                                "activate",
                                                manager_menu.on_disconnect,
                                                device, name)
                    items.append((item, 120))
                else:
                    item = create_menuitem(_("Audio Sink"),
                                           get_icon("blueman-headset", 16))
                    item.props.tooltip_text = _("Allows to send audio to remote device")
                    manager_menu.Signals.Handle("gobject",
                                                item,
                                                "activate",
                                                manager_menu.on_connect,
                                                device, name)
                    items.append((item, 20))

                item.show()


            elif name == "audiosource":
                sprops = service.get_properties()

                if not sprops["State"] == "disconnected":
                    item = create_menuitem(_("Audio Source"),
                                           get_icon("blueman-headset", 16))
                    manager_menu.Signals.Handle("gobject",
                                                item, "activate",
                                                manager_menu.on_disconnect,
                                                device, name)
                    items.append((item, 121))
                else:
                    item = create_menuitem(_("Audio Source"),
                                           get_icon("blueman-headset", 16))
                    item.props.tooltip_text = _("Allows to receive audio from remote device")
                    manager_menu.Signals.Handle("gobject",
                                                item, "activate",
                                                manager_menu.on_connect,
                                                device, name)
                    items.append((item, 21))
                item.show()

        return items


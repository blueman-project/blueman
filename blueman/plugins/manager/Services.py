from gettext import gettext as _
from typing import List, Tuple

import cairo

from blueman.Service import Service
from blueman.bluez.Device import Device
from blueman.bluez.Network import Network
from blueman.gui.manager.ManagerDeviceMenu import MenuItemsProvider, ManagerDeviceMenu
from blueman.plugins.ManagerPlugin import ManagerPlugin
from blueman.Functions import create_menuitem
from blueman.main.DBusProxies import AppletService
from blueman.services import *
from _blueman import rfcomm_list

import gi

from blueman.services.meta import NetworkService, SerialService

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Services(ManagerPlugin, MenuItemsProvider):
    def on_load(self) -> None:
        self.icon_theme = Gtk.IconTheme.get_default()

    def _make_x_icon(self, icon_name: str, size: int) -> cairo.ImageSurface:
        assert self.parent.window is not None

        scale = self.parent.window.get_scale_factor()
        window = self.parent.window.get_window()

        target = self.icon_theme.load_surface(icon_name, size, scale, window, Gtk.IconLookupFlags.FORCE_SIZE)
        bmx = self.icon_theme.load_surface("blueman-x", size, scale, window, Gtk.IconLookupFlags.FORCE_SIZE)

        x = target.get_width() - bmx.get_width()
        y = target.get_height() - bmx.get_height()
        context = cairo.Context(target)
        context.set_source_surface(bmx, x, y)
        context.paint()

        return target

    def on_request_menu_items(self, manager_menu: ManagerDeviceMenu, device: Device) -> List[Tuple[Gtk.MenuItem, int]]:
        items = []
        appl = AppletService()

        self.has_dun = False
        serial_items = []

        def add_menu_item(manager_menu: ManagerDeviceMenu, service: Service) -> None:
            if service.connected:
                surface = self._make_x_icon(service.icon, 16)
                item = create_menuitem(service.name, surface=surface)
                item.connect("activate", manager_menu.on_disconnect, service)
                items.append((item, service.priority + 100))
            else:
                item = create_menuitem(service.name, service.icon)
                if service.description:
                    item.props.tooltip_text = service.description
                item.connect("activate", manager_menu.on_connect, service)
                if isinstance(service, SerialService):
                    serial_items.append(item)
                    if isinstance(service, DialupNetwork):
                        self.has_dun = True
                else:
                    items.append((item, service.priority))
            item.props.sensitive = service.available
            item.show()

        for service in get_services(device):
            add_menu_item(manager_menu, service)

            if isinstance(service, SerialService):
                for dev in rfcomm_list():
                    if dev["dst"] == device['Address'] and dev["state"] == "connected":
                        devname = _("Serial Port %s") % "rfcomm%d" % dev["id"]

                        surface = self._make_x_icon("modem", 16)
                        item = create_menuitem(devname, surface=surface)
                        item.connect("activate", manager_menu.on_disconnect, service, dev["id"])
                        items.append((item, 120))
                        item.show()

            if isinstance(service, NetworkService) and service.connected:
                if "DhcpClient" in appl.QueryPlugins():
                    def renew(_item: Gtk.MenuItem) -> None:
                        appl.DhcpClient('(s)', Network(device.get_object_path())["Interface"])

                    item = create_menuitem(_("Renew IP Address"), "view-refresh")
                    item.connect("activate", renew)
                    item.show()
                    items.append((item, 201))

        if self.has_dun and ('PPPSupport' in appl.QueryPlugins() or 'NMDUNSupport' in appl.QueryPlugins()):
            def open_settings(_item: Gtk.MenuItem, device: Device) -> None:
                from blueman.gui.GsmSettings import GsmSettings

                d = GsmSettings(device['Address'])
                d.run()
                d.destroy()

            item = Gtk.SeparatorMenuItem()
            item.show()
            serial_items.append(item)

            item = create_menuitem(_("Dialup Settings"), "preferences-other")
            serial_items.append(item)
            item.show()
            item.connect("activate", open_settings, device)

        if len(serial_items) > 1:
            sub = Gtk.Menu()
            sub.show()

            item = create_menuitem(_("Serial Ports"), "modem")
            item.set_submenu(sub)
            item.show()
            items.append((item, 90))

            for item in serial_items:
                sub.append(item)
        else:
            for item in serial_items:
                items.append((item, 80))

        return items

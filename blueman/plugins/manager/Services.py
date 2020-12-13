from typing import List, Tuple

import cairo

from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceMenu import MenuItemsProvider, ManagerDeviceMenu
from blueman.plugins.ManagerPlugin import ManagerPlugin
from blueman.Functions import create_menuitem
from blueman.main.DBusProxies import AppletService
from blueman.services import get_services

import gi

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
        assert isinstance(target, cairo.ImageSurface)
        bmx = self.icon_theme.load_surface("blueman-x", size, scale, window, Gtk.IconLookupFlags.FORCE_SIZE)
        assert isinstance(bmx, cairo.ImageSurface)

        x = target.get_width() - bmx.get_width()
        y = target.get_height() - bmx.get_height()
        context = cairo.Context(target)
        context.set_source_surface(bmx, x, y)
        context.paint()

        return target

    def on_request_menu_items(self, manager_menu: ManagerDeviceMenu, device: Device) -> List[Tuple[Gtk.MenuItem, int]]:
        items: List[Tuple[Gtk.MenuItem, int]] = []
        appl = AppletService()

        services = get_services(device)

        connectable_services = [service for service in services if service.connectable]
        for service in connectable_services:
            item: Gtk.MenuItem = create_menuitem(service.name, service.icon)
            if service.description:
                item.props.tooltip_text = service.description
            item.connect("activate", manager_menu.on_connect, service)
            items.append((item, service.priority))
            item.props.sensitive = service.available
            item.show()

        for service in services:
            for instance in service.connected_instances:
                surface = self._make_x_icon(service.icon, 16)
                item = create_menuitem(instance.name, surface=surface)
                item.connect("activate", manager_menu.on_disconnect, service, instance.port)
                items.append((item, service.priority + 100))
                item.show()

        for action, priority in set((action, service.priority)
                                    for service in services for action in service.common_actions
                                    if any(plugin in appl.QueryPlugins() for plugin in action.plugins)):
            item = create_menuitem(action.title, action.icon)
            items.append((item, priority + 200))
            item.show()
            item.connect("activate", lambda _: action.callback())

        return items

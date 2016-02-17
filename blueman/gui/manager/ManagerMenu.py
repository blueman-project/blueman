# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import blueman.bluez as bluez
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.gui.CommonUi import *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib


class ManagerMenu:
    def __init__(self, blueman):
        self.blueman = blueman

        self.adapter_items = []
        self.Search = None

        self.item_adapter = self.blueman.Builder.get_object("item_adapter")
        self.item_device = self.blueman.Builder.get_object("item_device")

        self.item_view = self.blueman.Builder.get_object("item_view")
        self.item_help = self.blueman.Builder.get_object("item_help")

        help_menu = Gtk.Menu()

        self.item_help.set_submenu(help_menu)
        help_menu.show()

        report_item = create_menuitem(_("_Report a Problem"), get_icon("dialog-warning", 16))
        report_item.show()
        help_menu.append(report_item)
        report_item.connect("activate", lambda x: launch("xdg-open %s/issues" % WEBSITE, None, True))

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        help_menu.append(sep)

        help_item = create_menuitem("_Help", get_icon("help-about"))
        help_item.show()
        help_menu.append(help_item)
        help_item.connect("activate", lambda x: show_about_dialog('Blueman ' + _('Device Manager')))

        view_menu = Gtk.Menu()
        self.item_view.set_submenu(view_menu)
        view_menu.show()

        item_toolbar = Gtk.CheckMenuItem.new_with_mnemonic(_("Show _Toolbar"))
        item_toolbar.show()
        view_menu.append(item_toolbar)
        self.blueman.Config.bind_to_widget("show-toolbar", item_toolbar, "active")

        item_statusbar = Gtk.CheckMenuItem.new_with_mnemonic(_("Show _Statusbar"))
        item_statusbar.show()
        view_menu.append(item_statusbar)
        self.blueman.Config.bind_to_widget("show-statusbar", item_statusbar, "active")

        item_services = Gtk.SeparatorMenuItem()
        view_menu.append(item_services)
        item_services.show()

        group = []

        itemf = Gtk.RadioMenuItem.new_with_mnemonic(group, _("Latest Device _First"))
        itemf.show()
        group = itemf.get_group()
        view_menu.append(itemf)

        iteml = Gtk.RadioMenuItem.new_with_mnemonic(group, _("Latest Device _Last"))
        iteml.show()
        group = iteml.get_group()
        view_menu.append(iteml)

        itemf.connect("activate", lambda x: self.blueman.Config.set_boolean("latest-last", not x.props.active))
        iteml.connect("activate", lambda x: self.blueman.Config.set_boolean("latest-last", x.props.active))

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        view_menu.append(sep)

        item_plugins = create_menuitem(_("Plugins"), get_icon('blueman-plugin', 16))
        item_plugins.show()
        view_menu.append(item_plugins)
        item_plugins.connect('activate', lambda *args: self.blueman.Applet.open_plugin_dialog(ignore_reply=True))

        item_services = create_menuitem(_("_Local Services") + "...", get_icon("preferences-desktop", 16))
        item_services.connect('activate',
                              lambda *args: launch("blueman-services", None, False, "blueman", _("Service Preferences")))
        view_menu.append(item_services)
        item_services.show()

        adapter_menu = Gtk.Menu()
        self.item_adapter.set_submenu(adapter_menu)

        search_item = create_menuitem(_("_Search"), get_icon("edit-find", 16))
        search_item.connect("activate", lambda x: self.blueman.inquiry())
        search_item.show()
        adapter_menu.prepend(search_item)
        self.Search = search_item

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        adapter_menu.append(sep)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        adapter_menu.append(sep)

        adapter_settings = create_menuitem("_Preferences", get_icon("preferences-system", 16))
        adapter_settings.connect("activate", lambda x: self.blueman.adapter_properties())
        adapter_settings.show()
        adapter_menu.append(adapter_settings)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        adapter_menu.append(sep)

        exit_item = create_menuitem("_Exit", get_icon("application-exit", 16))
        exit_item.connect("activate", lambda x: Gtk.main_quit())
        exit_item.show()
        adapter_menu.append(exit_item)

        self.item_adapter.show()
        self.item_view.show()
        self.item_help.show()
        self.item_device.show()
        self.item_device.props.sensitive = False

        blueman.List.connect("adapter-added", self.on_adapter_added)
        blueman.List.connect("adapter-removed", self.on_adapter_removed)
        blueman.List.connect("adapter-property-changed", self.on_adapter_property_changed)
        blueman.List.connect("device-selected", self.on_device_selected)
        blueman.List.connect("adapter-changed", self.on_adapter_changed)

        self.adapters = blueman.List.manager.list_adapters()

        self.on_adapter_changed(blueman.List, blueman.List.GetAdapterPath())

        self.device_menu = None

    def on_device_selected(self, List, device, tree_iter):
        if tree_iter and device:
            self.item_device.props.sensitive = True

            if self.device_menu is None:
                self.device_menu = ManagerDeviceMenu(self.blueman)
                self.item_device.set_submenu(self.device_menu)
            else:
                GLib.idle_add(self.device_menu.Generate, priority=GLib.PRIORITY_LOW)

        else:
            self.item_device.props.sensitive = False

    def on_adapter_property_changed(self, lst, adapter, kv):
        (key, value) = kv
        if key == "Name" or key == "Alias":
            self.generate_adapter_menu()
        elif key == "Discovering":
            if self.Search:
                if value:
                    self.Search.props.sensitive = False
                else:
                    self.Search.props.sensitive = True

    def generate_adapter_menu(self):
        menu = self.item_adapter.get_submenu()
        insert_after = 2
        group = []

        # Remove and disconnect the existing adapter menu items
        for item, sig in self.adapter_items:
            item.disconnect(sig)
            menu.remove(item)

        self.adapter_items = []

        for adapter in self.adapters:
            item = Gtk.RadioMenuItem.new_with_label(group, adapter.get_name())
            item.show()
            group = item.get_group()

            sig = item.connect("activate", self.on_adapter_selected, adapter.get_object_path())
            if adapter.get_object_path() == self.blueman.List.Adapter.get_object_path():
                item.props.active = True

            menu.insert(item, insert_after)
            self.adapter_items.append((item, sig))

            insert_after += 1

    def on_adapter_selected(self, menuitem, adapter_path):
        if menuitem.props.active:
            if adapter_path != self.blueman.List.Adapter.get_object_path():
                dprint("selected", adapter_path)
                self.blueman.Config["last-adapter"] = adapter_path_to_name(adapter_path)
                self.blueman.List.SetAdapter(adapter_path)

    def on_adapter_added(self, device_list, adapter_path):
        self.adapters.append(bluez.Adapter(adapter_path))
        self.generate_adapter_menu()

    def on_adapter_removed(self, device_list, adapter_path):
        for adapter in self.adapters:
            if adapter.get_object_path() == adapter_path:
                self.adapters.remove(adapter)
        self.generate_adapter_menu()

    def on_adapter_changed(self, List, path):
        if path is None:
            self.item_adapter.props.sensitive = False
        else:
            self.item_adapter.props.sensitive = True
            self.generate_adapter_menu()

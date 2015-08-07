from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gtk, Gio
import blueman.bluez as Bluez
from blueman.Functions import *
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.Functions import adapter_path_to_name
from blueman.gui.CommonUi import *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ManagerMenu:
    def __init__(self, blueman):
        self.blueman = blueman

        self.Menubar = blueman.Builder.get_object("menu")

        self.adapter_items = []
        self.Search = None

        self.item_adapter = Gtk.MenuItem.new_with_mnemonic(_("_Adapter"))
        self.item_device = Gtk.MenuItem.new_with_mnemonic(_("_Device"))

        self.item_view = Gtk.MenuItem.new_with_mnemonic(_("_View"))
        self.item_help = Gtk.MenuItem.new_with_mnemonic(_("_Help"))

        self.Menubar.append(self.item_adapter)
        self.Menubar.append(self.item_device)
        self.Menubar.append(self.item_view)
        self.Menubar.append(self.item_help)

        help_menu = Gtk.Menu()

        self.item_help.set_submenu(help_menu)
        help_menu.show()

        item = create_menuitem(_("_Report a Problem"), get_icon("dialog-warning", 16))
        item.connect("activate", lambda x: launch("xdg-open %s/issues" % WEBSITE, None, True))
        help_menu.append(item)
        item.show()

        item = Gtk.SeparatorMenuItem()
        help_menu.append(item)
        item.show()

        item = create_menuitem("_Help", get_icon("help-about"))
        item.connect("activate", lambda x: show_about_dialog('Blueman ' + _('Device Manager')))
        help_menu.append(item)
        item.show()

        view_menu = Gtk.Menu()
        self.item_view.set_submenu(view_menu)
        view_menu.show()

        item = Gtk.CheckMenuItem.new_with_mnemonic(_("Show _Toolbar"))
        self.blueman.Config.bind_to_widget("show-toolbar", item, "active")
        view_menu.append(item)
        item.show()

        item = Gtk.CheckMenuItem.new_with_mnemonic(_("Show _Statusbar"))
        self.blueman.Config.bind_to_widget("show-statusbar", item, "active")
        view_menu.append(item)
        item.show()

        item = Gtk.SeparatorMenuItem()
        view_menu.append(item)
        item.show()

        group = []

        itemf = Gtk.RadioMenuItem.new_with_mnemonic(group, _("Latest Device _First"))
        group = itemf.get_group()
        view_menu.append(itemf)
        itemf.show()

        iteml = Gtk.RadioMenuItem.new_with_mnemonic(group, _("Latest Device _Last"))
        group = iteml.get_group()
        view_menu.append(iteml)
        iteml.show()

        itemf.connect("activate", lambda x: self.blueman.Config.set_boolean("latest-last", not x.props.active))
        iteml.connect("activate", lambda x: self.blueman.Config.set_boolean("latest-last", x.props.active))

        item = Gtk.SeparatorMenuItem()
        view_menu.append(item)
        item.show()

        item = create_menuitem(_("Plugins"), get_icon('blueman-plugin', 16))
        item.connect('activate', lambda *args: self.blueman.Applet.open_plugin_dialog(ignore_reply=True))
        view_menu.append(item)
        item.show()

        item = create_menuitem(_("_Local Services") + "...", get_icon("preferences-desktop", 16))
        item.connect('activate',
                     lambda *args: launch("blueman-services", None, False, "blueman", _("Service Preferences")))
        view_menu.append(item)
        item.show()

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

    def on_device_selected(self, List, device, iter):
        if iter and device:
            self.item_device.props.sensitive = True

            if self.device_menu == None:
                self.device_menu = ManagerDeviceMenu(self.blueman)
                self.item_device.set_submenu(self.device_menu)
            else:
                GObject.idle_add(self.device_menu.Generate, priority=GObject.PRIORITY_LOW)

        else:
            self.item_device.props.sensitive = False


    def on_adapter_property_changed(self, list, adapter, kv):
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
        menu = Gtk.Menu()

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        settings = create_menuitem("_Preferences", get_icon("preferences-system", 16))
        settings.connect("activate", lambda x: self.blueman.adapter_properties())
        settings.show()
        menu.append(settings)

        group = []
        for adapter in self.adapters:
            item = Gtk.RadioMenuItem.new_with_label(group, adapter.get_name())
            group = item.get_group()

            item.connect("activate", self.on_adapter_selected, adapter.get_object_path())
            if adapter.get_object_path() == self.blueman.List.Adapter.get_object_path():
                item.props.active = True

            item.show()
            menu.prepend(item)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.prepend(sep)

        item = create_menuitem(_("_Search"), get_icon("edit-find", 16))
        item.connect("activate", lambda x: self.blueman.inquiry())
        item.show()
        menu.prepend(item)
        self.Search = item

        m = self.item_adapter.get_submenu()
        if m != None:
            m.deactivate()
        self.item_adapter.set_submenu(menu)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        item = create_menuitem("_Exit", get_icon("application-exit", 16))
        item.connect("activate", lambda x: Gtk.main_quit())
        item.show()
        menu.append(item)

    def on_adapter_selected(self, menuitem, adapter_path):
        if menuitem.props.active:
            if adapter_path != self.blueman.List.Adapter.get_object_path():
                dprint("selected", adapter_path)
                self.blueman.Config["last-adapter"] = adapter_path_to_name(adapter_path)
                self.blueman.List.SetAdapter(adapter_path)


    def on_adapter_added(self, device_list, adapter_path):
        self.adapters.append(Bluez.Adapter(adapter_path))
        self.generate_adapter_menu()

    def on_adapter_removed(self, device_list, adapter_path):
        for adapter in self.adapters:
            if adapter.get_object_path() == adapter_path:
                self.adapters.remove(adapter)
        self.generate_adapter_menu()

    def on_adapter_changed(self, List, path):
        if path == None:
            self.item_adapter.props.sensitive = False
        else:
            self.item_adapter.props.sensitive = True
            self.generate_adapter_menu()

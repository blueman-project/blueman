from gi.repository import Gtk
import blueman.bluez as Bluez
from blueman.Functions import *
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.Functions import adapter_path_to_name
from blueman.gui.CommonUi import *


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

        item = create_menuitem(_("_Report a Problem"), get_icon("gtk-dialog-warning", 16))
        item.connect("activate", lambda x: spawn(["xdg-open", WEBSITE + '/issues'], True))
        help_menu.append(item)
        item.show()

        item = Gtk.SeparatorMenuItem()
        help_menu.append(item)
        item.show()

        item = Gtk.ImageMenuItem.new_from_stock("gtk-about", None)
        item.connect("activate", lambda x: show_about_dialog('Blueman ' + _('Device Manager')))
        help_menu.append(item)
        item.show()

        view_menu = Gtk.Menu()
        self.item_view.set_submenu(view_menu)
        view_menu.show()

        item = Gtk.CheckMenuItem.new_with_mnemonic(_("Show Toolbar"))
        if self.blueman.Config.props.show_toolbar == None:
            item.props.active = True
        else:
            if not self.blueman.Config.props.show_toolbar:
                item.props.active = False
            else:
                item.props.active = True
        item.connect("activate", lambda x: setattr(self.blueman.Config.props, "show_toolbar", x.props.active))
        view_menu.append(item)
        item.show()

        item = Gtk.CheckMenuItem.new_with_mnemonic(_("Show Statusbar"))
        if self.blueman.Config.props.show_statusbar == None:
            item.props.active = True
        else:
            if not self.blueman.Config.props.show_statusbar:
                item.props.active = False
            else:
                item.props.active = True
        item.connect("activate", lambda x: setattr(self.blueman.Config.props, "show_statusbar", x.props.active))
        view_menu.append(item)
        item.show()

        item = Gtk.SeparatorMenuItem()
        view_menu.append(item)
        item.show()

        group = []

        itemf = Gtk.RadioMenuItem.new_with_label(group, _("Latest Device First"))
        group = itemf.get_group()
        view_menu.append(itemf)
        itemf.show()

        iteml = Gtk.RadioMenuItem.new_with_label(group, _("Latest Device Last"))
        group = iteml.get_group()
        view_menu.append(iteml)
        iteml.show()

        if self.blueman.Config.props.latest_last:
            iteml.props.active = True
        else:
            itemf.props.active = True
        itemf.connect("activate", lambda x: setattr(self.blueman.Config.props, "latest_last", not x.props.active))
        iteml.connect("activate", lambda x: setattr(self.blueman.Config.props, "latest_last", x.props.active))

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
        if key == "Name":
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

        settings = Gtk.ImageMenuItem.new_from_stock("gtk-preferences", None)
        settings.connect("activate", lambda x: self.blueman.adapter_properties())
        settings.show()
        menu.append(settings)

        group = []
        for adapter in self.adapters:
            props = adapter.get_properties()
            item = Gtk.RadioMenuItem.new_with_label(group, props["Name"])
            group = item.get_group()

            item.connect("activate", self.on_adapter_selected, adapter.get_object_path())
            if adapter.get_object_path() == self.blueman.List.Adapter.get_object_path():
                item.props.active = True

            item.show()
            menu.prepend(item)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.prepend(sep)

        item = create_menuitem(_("_Search"), get_icon("gtk-find", 16))
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

        item = Gtk.ImageMenuItem.new_from_stock("gtk-quit", None)
        item.connect("activate", lambda x: Gtk.main_quit())
        item.show()
        menu.append(item)

    def on_adapter_selected(self, menuitem, adapter_path):
        if menuitem.props.active:
            if adapter_path != self.blueman.List.Adapter.get_object_path():
                dprint("selected", adapter_path)
                self.blueman.Config.props.last_adapter = adapter_path_to_name(adapter_path)
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
		


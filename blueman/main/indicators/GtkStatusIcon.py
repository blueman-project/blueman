# coding=utf-8
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from blueman.Functions import create_menuitem


def build_menu(items, activate):
    menu = Gtk.Menu()
    for index, item in enumerate(items):
        if 'text' in item and 'icon_name' in item:
            gtk_item = create_menuitem(item['text'], item['icon_name'])
            label = gtk_item.get_child()
            if item['markup']:
                label.set_markup_with_mnemonic(item['text'])
            else:
                label.set_text_with_mnemonic(item['text'])
            gtk_item.connect('activate', lambda _, idx=index: activate(idx))
            if 'submenu' in item:
                gtk_item.set_submenu(build_menu(item['submenu'], lambda subid, idx=index: activate(idx, subid)))
            if 'tooltip' in item:
                gtk_item.props.tooltip_text = item['tooltip']
            gtk_item.props.sensitive = item['sensitive']
        else:
            gtk_item = Gtk.SeparatorMenuItem()
        gtk_item.show()
        menu.append(gtk_item)
    return menu


class GtkStatusIcon(object):
    def __init__(self, icon_name, on_activate_menu_item, on_activate_status_icon):
        self._on_activate = on_activate_menu_item
        self.indicator = Gtk.StatusIcon(icon_name=icon_name)
        self.indicator.set_title('blueman')
        self.indicator.connect('popup-menu', self.on_popup_menu)
        self.indicator.connect('activate', lambda _status_icon: on_activate_status_icon())
        self._menu = None

    def on_popup_menu(self, status_icon, button, activate_time):
        if self._menu:
            self._menu.popup(None, None, Gtk.StatusIcon.position_menu, status_icon, button, activate_time)

    def set_icon(self, icon_name):
        self.indicator.props.icon_name = icon_name

    def set_text(self, text):
        self.indicator.props.tooltip_markup = text

    def set_visibility(self, visible):
        self.indicator.props.visible = visible

    def set_menu(self, menu):
        self._menu = build_menu(menu, self._on_activate)

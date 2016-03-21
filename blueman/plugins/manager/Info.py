import dbus
from gi.repository import Gtk

from blueman.Functions import create_menuitem, get_icon
from blueman.Sdp import uuid128_to_uuid16, uuid16_to_name

from blueman.plugins.ManagerPlugin import ManagerPlugin


def show_info(device, parent):
    dialog = Gtk.Dialog()
    dialog.set_transient_for(parent)
    dialog.set_icon_name('blueman')
    dialog.set_title('blueman')
    store = Gtk.ListStore(str, str)
    view = Gtk.TreeView()
    view.set_headers_visible(False)
    view.set_model(store)
    for i in range(2):
        column = Gtk.TreeViewColumn()
        cell = Gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', i)
        view.append_column(column)
    dialog.get_content_area().pack_start(view, True, False, 0)
    view.show_all()

    def format_boolean(x):
        return _('yes') if x else _('no')

    def format_rssi(rssi):
        if rssi in [0x99, 0x7f]:
            'invalid (0x{:02x})'.format(rssi)
        else:
            '{} dBm (0x{:02x})'.format(rssi, rssi)

    def format_uuids(uuids):
        return "\n".join([uuid + ' ' + uuid16_to_name(uuid128_to_uuid16(uuid)) for uuid in uuids])
    properties = [
        'Address',
        'Name',
        'Alias',
        ('Class', lambda x: x and "0x{:06x}".format(x)),
        ('Appearance', lambda x: "0x{:04x}".format(x)),
        'Icon',
        ('Paired', format_boolean),
        ('Trusted', format_boolean),
        ('Blocked', format_boolean),
        ('LegacyPairing', format_boolean),
        ('RSSI', format_rssi),
        ('Connected', format_boolean),
        ('UUIDs', format_uuids),
        'Modalias',
        'Adapter'
    ]
    for prop in properties:
        try:
            if isinstance(prop, tuple):
                store.append((prop[0], prop[1](device.get(prop[0]))))
            else:
                store.append((prop, device.get(prop)))
        except dbus.exceptions.DBusException:
            pass
    dialog.run()
    dialog.destroy()


class Info(ManagerPlugin):
    def on_unload(self):
        pass

    def on_request_menu_items(self, manager_menu, device):
        item = create_menuitem(_("Info"), get_icon("info", 16))
        item.props.tooltip_text = _("Show device information")
        item.connect('activate', lambda x: show_info(device, manager_menu.get_toplevel()))
        return [(item, 400)]

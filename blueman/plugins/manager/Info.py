from gi.repository import Gtk, Gdk

import logging
from blueman.Functions import create_menuitem
from blueman.Sdp import ServiceUUID
from blueman.bluez.errors import BluezDBusException

from blueman.plugins.ManagerPlugin import ManagerPlugin


def show_info(device, parent):
    def format_boolean(x):
        return _('yes') if x else _('no')

    def format_rssi(rssi):
        if rssi in [0x99, 0x7f]:
            'invalid (0x{:02x})'.format(rssi)
        else:
            '{} dBm (0x{:02x})'.format(rssi, rssi)

    def format_uuids(uuids):
        return "\n".join([uuid + ' ' + ServiceUUID(uuid).name for uuid in uuids])

    def on_accel_activated(group, dialog, key, flags):
        if key != 99:
            logging.warning("Ignoring key %s" % key)
            return

        store, paths = view_selection.get_selected_rows()

        text = []
        for path in paths:
            row = store[path]
            text.append(row[-1])

        logging.info("\n".join(text))
        clipboard.set_text("\n".join(text), -1)

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    dialog = Gtk.Dialog(icon_name="blueman", title="blueman")
    dialog.set_transient_for(parent)
    dialog_content_area = dialog.get_content_area()

    label = Gtk.Label()
    label.set_markup("<big>Select row(s) and use <i>Control + C</i> to copy</big>")
    label.show()
    dialog_content_area.pack_start(label, True, False, 0)

    accelgroup = Gtk.AccelGroup()
    dialog.add_accel_group(accelgroup)

    key, mod = Gtk.accelerator_parse("<Control>C")
    accelgroup.connect(key, mod, Gtk.AccelFlags.MASK, on_accel_activated)

    store = Gtk.ListStore(str, str)
    view = Gtk.TreeView(model=store, headers_visible=False)
    view_selection = view.get_selection()
    view_selection.set_mode(Gtk.SelectionMode.MULTIPLE)

    for i in range(2):
        column = Gtk.TreeViewColumn()
        cell = Gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', i)
        view.append_column(column)
    dialog_content_area.pack_start(view, True, False, 0)
    view.show_all()

    properties = (
        ('Address', None),
        ('AddressType', None),
        ('Name', None),
        ('Alias', None),
        ('Class', lambda x: "0x{:06x}".format(x)),
        ('Appearance', lambda x: "0x{:04x}".format(x)),
        ('Icon', None),
        ('Paired', format_boolean),
        ('Trusted', format_boolean),
        ('Blocked', format_boolean),
        ('LegacyPairing', format_boolean),
        ('RSSI', format_rssi),
        ('Connected', format_boolean),
        ('UUIDs', format_uuids),
        ('Modalias', None),
        ('Adapter', None),
        # FIXME below 3 we need some sample data to decode and display properly
        ('ManufacturerData', str),
        ('ServiceData', str),
        ('AdvertisingData', str)
    )
    for name, func in properties:
        try:
            if func is None:
                store.append((name, device.get(name)))
            else:
                store.append((name, func(device.get(name))))
        except BluezDBusException:
            logging.info("Could not get property %s" % name)
            pass
        except ValueError:
            logging.info("Could not add property %s" % name)
            pass

    dialog.run()
    dialog.destroy()


class Info(ManagerPlugin):
    def on_unload(self):
        pass

    def on_request_menu_items(self, manager_menu, device):
        item = create_menuitem(_("_Info"), "dialog-information")
        item.props.tooltip_text = _("Show device information")
        item.connect('activate', lambda x: show_info(device, manager_menu.get_toplevel()))
        return [(item, 400)]

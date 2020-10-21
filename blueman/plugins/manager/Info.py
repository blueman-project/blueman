from gettext import gettext as _
from typing import List, Tuple, Iterable, Callable, Any, Optional

from gi.repository import Gtk, Gdk

import logging

from gi.repository.GObject import GObject

from blueman.Functions import create_menuitem
from blueman.Sdp import ServiceUUID
from blueman.bluez.Device import Device
from blueman.bluez.errors import BluezDBusException
from blueman.gui.manager.ManagerDeviceMenu import MenuItemsProvider, ManagerDeviceMenu, DeviceMenuItem

from blueman.plugins.ManagerPlugin import ManagerPlugin


def show_info(device: Device, parent: Gtk.Window) -> None:
    def format_boolean(x: bool) -> str:
        return _('yes') if x else _('no')

    def format_rssi(rssi: int) -> str:
        if rssi in [0x99, 0x7f]:
            return f'invalid (0x{rssi:02x})'
        else:
            return f'{rssi} dBm (0x{rssi:02x})'

    def format_uuids(uuids: Iterable[str]) -> str:
        return "\n".join([uuid + ' ' + ServiceUUID(uuid).name for uuid in uuids])

    store = Gtk.ListStore(str, str)
    view = Gtk.TreeView(model=store, headers_visible=False)
    view_selection = view.get_selection()
    view_selection.set_mode(Gtk.SelectionMode.MULTIPLE)

    def on_accel_activated(_group: Gtk.AccelGroup, _dialog: GObject, key: int, _modifier: Gdk.ModifierType) -> bool:
        if key != 99:
            logging.warning(f"Ignoring key {key}")
            return False

        store, paths = view_selection.get_selected_rows()

        text = []
        for path in paths:
            row = store[path]
            text.append(row[-1])

        logging.info("\n".join(text))
        clipboard.set_text("\n".join(text), -1)

        return False

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    dialog = Gtk.Dialog(icon_name="blueman", title="blueman")
    dialog.set_transient_for(parent)
    dialog_content_area = dialog.get_content_area()

    label = Gtk.Label()
    label.set_markup(_("<big>Select row(s) and use <i>Control + C</i> to copy</big>"))
    label.show()
    dialog_content_area.pack_start(label, True, False, 0)

    accelgroup = Gtk.AccelGroup()
    dialog.add_accel_group(accelgroup)

    key, mod = Gtk.accelerator_parse("<Control>C")
    accelgroup.connect(key, mod, Gtk.AccelFlags.MASK, on_accel_activated)

    for i in range(2):
        column = Gtk.TreeViewColumn()
        cell = Gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', i)
        view.append_column(column)
    dialog_content_area.pack_start(view, True, False, 0)
    view.show_all()

    properties: Iterable[Tuple[str, Optional[Callable[[Any], str]]]] = (
        ('Address', None),
        ('AddressType', None),
        ('Name', None),
        ('Alias', None),
        ('Class', lambda x: f"0x{x:06x}"),
        ('Appearance', lambda x: f"0x{x:04x}"),
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
            logging.info(f"Could not get property {name}")
            pass
        except ValueError:
            logging.info(f"Could not add property {name}")
            pass

    dialog.run()
    dialog.destroy()


class Info(ManagerPlugin, MenuItemsProvider):
    def on_request_menu_items(self, manager_menu: ManagerDeviceMenu, device: Device) -> List[DeviceMenuItem]:
        item = create_menuitem(_("_Info"), "dialog-information")
        item.props.tooltip_text = _("Show device information")
        _window = manager_menu.get_toplevel()
        assert isinstance(_window, Gtk.Window)
        window = _window  # https://github.com/python/mypy/issues/2608
        item.connect('activate', lambda x: show_info(device, window))
        return [DeviceMenuItem(item, DeviceMenuItem.Group.ACTIONS, 400)]

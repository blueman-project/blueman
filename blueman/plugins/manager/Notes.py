import datetime
from gettext import gettext as _
from tempfile import NamedTemporaryFile
from typing import List

from blueman.Functions import create_menuitem, launch
from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceMenu import MenuItemsProvider, ManagerDeviceMenu, DeviceMenuItem
from blueman.main.Builder import Builder
from blueman.plugins.ManagerPlugin import ManagerPlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def send_note_cb(dialog: Gtk.Dialog, response_id: int, device_address: str, text_view: Gtk.Entry) -> None:
    text = text_view.get_buffer().props.text
    dialog.destroy()
    if response_id == Gtk.ResponseType.REJECT:
        return

    date = datetime.datetime.now().strftime('%Y%m%dT%H%M00')
    data = ('BEGIN:VNOTE \n'
            'VERSION:1.1 \n'
            'BODY;CHARSET=UTF-8: %s \n'
            'DCREATED:%s \n'
            'LAST-MODIFIED:%s \n'
            'CLASS:PUBLIC \n'
            'X-IRMC-LUID:000001000000 \n'
            'END:VNOTE \n' % (' '.join(text.splitlines()), date, date))

    tempfile = NamedTemporaryFile(suffix='.vnt', prefix='note', delete=False)
    tempfile.write(data.encode('utf-8'))
    tempfile.close()
    launch(f"blueman-sendto --delete --device={device_address}", paths=[tempfile.name])


def send_note(device: Device, parent: Gtk.Window) -> None:
    builder = Builder("note.ui")
    dialog = builder.get_widget("dialog", Gtk.Dialog)
    dialog.set_transient_for(parent)
    dialog.props.icon_name = 'blueman'
    note = builder.get_widget("note", Gtk.Entry)
    dialog.connect('response', send_note_cb, device['Address'], note)
    dialog.present()


class Notes(ManagerPlugin, MenuItemsProvider):
    def on_request_menu_items(self, manager_menu: ManagerDeviceMenu, device: Device) -> List[DeviceMenuItem]:
        item = create_menuitem(_("Send _note"), "dialog-information-symbolic")
        item.props.tooltip_text = _("Send a text note")
        _window = manager_menu.get_toplevel()
        assert isinstance(_window, Gtk.Window)
        window = _window  # https://github.com/python/mypy/issues/2608
        item.connect('activate', lambda x: send_note(device, window))
        return [DeviceMenuItem(item, DeviceMenuItem.Group.ACTIONS, 500)]

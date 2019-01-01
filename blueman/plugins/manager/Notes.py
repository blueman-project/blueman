import datetime
from gettext import bind_textdomain_codeset
from tempfile import NamedTemporaryFile

from blueman.Functions import create_menuitem, launch, UI_PATH
from blueman.plugins.ManagerPlugin import ManagerPlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def send_note_cb(dialog, response_id, device_address, text_view):
    text = text_view.get_buffer().props.text
    dialog.destroy()
    if response_id == Gtk.ResponseType.CANCEL:
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
    launch('blueman-sendto --delete --device=%s' % device_address, [tempfile.name], False, 'blueman')


def send_note(device, parent):
    builder = Gtk.Builder()
    builder.set_translation_domain('blueman')
    bind_textdomain_codeset('blueman', 'UTF-8')
    builder.add_from_file(UI_PATH + '/note.ui')
    dialog = builder.get_object('dialog')
    dialog.set_transient_for(parent)
    dialog.props.icon_name = 'blueman'
    dialog.connect('response', send_note_cb, device['Address'], builder.get_object('note'))
    dialog.present()


class Notes(ManagerPlugin):
    def on_unload(self):
        pass

    def on_request_menu_items(self, manager_menu, device):
        item = create_menuitem(_("Send _note"), "dialog-information")
        item.props.tooltip_text = _("Send a text note")
        item.connect('activate', lambda x: send_note(device, manager_menu.get_toplevel()))
        return [(item, 500)]

# coding=utf-8
import time
import logging
from locale import bind_textdomain_codeset
from gettext import ngettext

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from blueman.bluez.Adapter import Adapter
from blueman.bluez.obex.ObjectPush import ObjectPush
from blueman.bluez.obex.Manager import Manager
from blueman.Functions import format_bytes
from blueman.Constants import UI_PATH
from blueman.main.SpeedCalc import SpeedCalc
from blueman.gui.CommonUi import ErrorDialog
from blueman.bluez import obex

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk, GObject, GLib, Gio


class Sender(Gtk.Dialog):
    __gsignals__ = {
        'result': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_BOOLEAN,)),
    }

    def __init__(self, device, adapter_path, files):
        super().__init__(
            title=_("Bluetooth File Transfer"),
            name="BluemanSendTo",
            icon_name="blueman",
            border_width=5,
            default_width=400,
            window_position=Gtk.WindowPosition.CENTER,
            type_hint=Gdk.WindowTypeHint.DIALOG
        )

        self.b_cancel = self.add_button("_Stop", Gtk.ResponseType.CLOSE)
        self.b_cancel.props.receives_default = True
        self.b_cancel.props.use_underline = True
        self.b_cancel.connect("clicked", self.on_cancel)

        self.Builder = Gtk.Builder(translation_domain="blueman")
        bind_textdomain_codeset("blueman", "UTF-8")
        self.Builder.add_from_file(UI_PATH + "/send-dialog.ui")

        grid = self.Builder.get_object("sendto")
        content_area = self.get_content_area()
        content_area.add(grid)

        self.l_dest = self.Builder.get_object("l_dest")
        self.l_file = self.Builder.get_object("l_file")

        self.pb = self.Builder.get_object("pb")
        self.pb.props.text = _("Connecting")

        self.device = device
        self.adapter = Adapter(adapter_path)
        self.manager = Manager()
        self.files = []
        self.num_files = 0
        self.object_push = None
        self.transfer = None

        self.total_bytes = 0
        self.total_transferred = 0

        self._last_bytes = 0
        self._last_update = 0

        self.error_dialog = None
        self.cancelling = False

        # bytes transferred on a current transfer
        self.transferred = 0

        self.speed = SpeedCalc(6)

        for file_name in files:
            parsed_file = Gio.File.parse_name(file_name)

            if not parsed_file.query_exists():
                logging.info("Skipping non existing file %s" % parsed_file.get_path())
                continue

            file_info = parsed_file.query_info("standard::*", Gio.FileQueryInfoFlags.NONE)

            if file_info.get_file_type() == Gio.FileType.DIRECTORY:
                logging.info("Skipping directory %s" % parsed_file.get_path())
                continue

            self.files.append(parsed_file)
            self.num_files += 1
            self.total_bytes += file_info.get_size()

        if len(self.files) == 0:
            self.emit("result", False)

        try:
            self.client = obex.Client()
            self.manager.connect_signal('session-added', self.on_session_added)
            self.manager.connect_signal('session-removed', self.on_session_removed)
        except GLib.Error as e:
            if 'StartServiceByName' in e.message:
                logging.debug(e.message)
                d = ErrorDialog(_("obexd not available"), _("Failed to autostart obex service. Make sure the obex "
                                                            "daemon is running"), parent=self.get_toplevel())
                d.run()
                d.destroy()
                self.emit("result", False)
            else:
                # Fail on anything else
                raise

        self.l_file.props.label = self.files[-1].get_basename()

        self.client.connect('session-failed', self.on_session_failed)

        logging.info("Sending to %s" % device['Address'])
        self.l_dest.props.label = device['Alias']

        # Stop discovery if discovering and let adapter settle for a second
        if self.adapter["Discovering"]:
            self.adapter.stop_discovery()
            time.sleep(1)

        self.create_session()

        self.show()

    def create_session(self):
        self.client.create_session(self.device['Address'], self.adapter["Address"])

    def on_cancel(self, button):
        self.pb.props.text = _("Cancelling")
        if button:
            button.props.sensitive = False

        if self.object_push:
            self.client.remove_session(self.object_push.get_session_path())

        self.emit("result", False)

    def on_transfer_started(self, _object_push, transfer_path, filename):
        if self.total_transferred == 0:
            self.pb.props.text = _("Sending File") + (" %(0)s/%(1)s (%(2).2f %(3)s/s) " + _("ETA:") + " %(4)s") % {
                "1": self.num_files,
                "0": (self.num_files - len(self.files) + 1),
                "2": 0.0,
                "3": "B/s",
                "4": "∞"}

        self.l_file.props.label = filename
        self._last_bytes = 0
        self.transferred = 0

        self.transfer = obex.Transfer(transfer_path)
        self.transfer.connect("error", self.on_transfer_error)
        self.transfer.connect("progress", self.on_transfer_progress)
        self.transfer.connect("completed", self.on_transfer_completed)

    def on_transfer_failed(self, _object_push, error):
        self.on_transfer_error(None, str(error))

    def on_transfer_progress(self, _transfer, progress):
        self.transferred = progress
        if self._last_bytes == 0:
            self.total_transferred += progress
        else:
            self.total_transferred += (progress - self._last_bytes)

        self._last_bytes = progress

        tm = time.time()
        if tm - self._last_update > 0.5:
            spd = self.speed.calc(self.total_transferred)
            (size, units) = format_bytes(spd)
            try:
                x = ((self.total_bytes - self.total_transferred) / spd) + 1
                if x > 60:
                    x /= 60
                    eta = ngettext("%.0f Minute", "%.0f Minutes", round(x)) % x
                else:
                    eta = ngettext("%.0f Second", "%.0f Seconds", round(x)) % x
            except ZeroDivisionError:
                eta = "∞"

            self.pb.props.text = _("Sending File") + (" %(0)s/%(1)s (%(2).2f %(3)s/s) " + _("ETA:") + " %(4)s") % {
                "1": self.num_files,
                "0": (self.num_files - len(self.files) + 1),
                "2": size,
                "3": units,
                "4": eta}
            self._last_update = tm

        self.pb.props.fraction = float(self.total_transferred) / self.total_bytes

    def on_transfer_completed(self, _transfer):
        del self.files[-1]
        self.transfer = None

        self.process_queue()

    def process_queue(self):
        if len(self.files) > 0:
            self.send_file(self.files[-1].get_path())
        else:
            self.emit("result", True)

    def send_file(self, file_path):
        logging.info(file_path)
        if self.object_push:
            self.object_push.send_file(file_path)

    def on_transfer_error(self, _transfer, msg=""):
        if not self.error_dialog:
            self.speed.reset()
            d = ErrorDialog(msg, _("Error occurred while sending file %s") % self.files[-1].get_basename(),
                            modal=True, icon_name="blueman", parent=self.get_toplevel(), buttons=[])

            if len(self.files) > 1:
                d.add_button(_("Skip"), Gtk.ResponseType.NO)
            d.add_button(_("Retry"), Gtk.ResponseType.YES)
            d.add_button("_Cancel", Gtk.ResponseType.CANCEL)

            self.client.remove_session(self.object_push.get_object_path())

            def on_response(dialog, resp):
                dialog.destroy()
                self.error_dialog = None

                if resp == Gtk.ResponseType.CANCEL:
                    self.on_cancel(None)
                elif resp == Gtk.ResponseType.NO:
                    finfo = self.files[-1].query_info('standard::*', Gio.FileQueryInfoFlags.NONE)
                    self.total_bytes -= finfo.get_size()
                    self.total_transferred -= self.transferred
                    self.transferred = 0
                    del self.files[-1]
                    if not self.object_push:
                        self.create_session()
                    self.process_queue()
                elif resp == Gtk.ResponseType.YES:
                    self.total_transferred -= self.transferred
                    self.transferred = 0
                    if not self.object_push:
                        self.create_session()

                    self.process_queue()
                else:
                    self.on_cancel(None)

            d.connect("response", on_response)
            d.show()
            self.error_dialog = d

    def on_session_added(self, _manager, session_path):
        self.object_push = ObjectPush(session_path)
        self.object_push.connect("transfer-started", self.on_transfer_started)
        self.object_push.connect("transfer-failed", self.on_transfer_failed)
        self.process_queue()

    def on_session_removed(self, _manager, session_path):
        logging.debug('Session removed: %s' % session_path)
        self.object_push.disconnect_by_func(self.on_transfer_started)
        self.object_push.disconnect_by_func(self.on_transfer_failed)
        self.object_push = None

    def on_session_failed(self, _client, msg):
        d = ErrorDialog(_("Error occurred"), msg.reason.split(None, 1)[1], icon_name="blueman",
                        parent=self.get_toplevel())

        d.run()
        d.destroy()
        self.emit("result", False)

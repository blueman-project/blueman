from gettext import gettext as _
import time
import logging
from gettext import ngettext
from typing import List, Iterable, Optional

from blueman.bluez.Device import Device
from blueman.bluez.errors import BluezDBusException
from blueman.main.Builder import Builder
from blueman.bluemantyping import GSignals
from blueman.bluez.Adapter import Adapter
from blueman.bluez.obex.ObjectPush import ObjectPush
from blueman.bluez.obex.Manager import Manager
from blueman.bluez.obex.Client import Client
from blueman.bluez.obex.Transfer import Transfer
from blueman.Functions import format_bytes
from blueman.main.SpeedCalc import SpeedCalc
from blueman.gui.CommonUi import ErrorDialog

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk, GObject, GLib, Gio


class Sender(Gtk.Dialog):
    __gsignals__: GSignals = {
        'result': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_BOOLEAN,)),
    }

    def __init__(self, device: Device, adapter_path: str, files: Iterable[str]) -> None:
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

        builder = Builder("send-dialog.ui")

        grid = builder.get_widget("sendto", Gtk.Grid)
        content_area = self.get_content_area()
        content_area.add(grid)

        self.l_dest = builder.get_widget("l_dest", Gtk.Label)
        self.l_file = builder.get_widget("l_file", Gtk.Label)

        self.pb = builder.get_widget("pb", Gtk.ProgressBar)
        self.pb.props.text = _("Connecting")

        self.device = device
        self.adapter = Adapter(obj_path=adapter_path)
        self.manager = Manager()
        self.files: List[Gio.File] = []
        self.num_files = 0
        self.object_push: Optional[ObjectPush] = None
        self.object_push_handlers: List[int] = []
        self.transfer: Optional[Transfer] = None

        self.total_bytes = 0
        self.total_transferred = 0

        self._last_bytes = 0
        self._last_update = 0.0

        self.error_dialog: Optional[ErrorDialog] = None
        self.cancelling = False

        # bytes transferred on a current transfer
        self.transferred = 0

        self.speed = SpeedCalc(6)

        for file_name in files:
            parsed_file = Gio.File.parse_name(file_name)

            if not parsed_file.query_exists():
                logging.info(f"Skipping non existing file {parsed_file.get_path()}")
                continue

            file_info = parsed_file.query_info("standard::*", Gio.FileQueryInfoFlags.NONE)

            if file_info.get_file_type() == Gio.FileType.DIRECTORY:
                logging.info(f"Skipping directory {parsed_file.get_path()}")
                continue

            self.files.append(parsed_file)
            self.num_files += 1
            self.total_bytes += file_info.get_size()

        if len(self.files) == 0:
            self.emit("result", False)

        try:
            self.client = Client()
            self.manager.connect_signal('session-added', self.on_session_added)
            self.manager.connect_signal('session-removed', self.on_session_removed)
        except GLib.Error as e:
            if 'StartServiceByName' in e.message:
                logging.debug(e.message)
                parent = self.get_toplevel()
                assert isinstance(parent, Gtk.Container)
                d = ErrorDialog(_("obexd not available"), _("Failed to autostart obex service. Make sure the obex "
                                                            "daemon is running"), parent=parent)
                d.run()
                d.destroy()
                self.emit("result", False)
            else:
                # Fail on anything else
                raise

        basename = self.files[-1].get_basename()
        assert basename is not None
        self.l_file.props.label = basename

        self.client.connect('session-failed', self.on_session_failed)

        logging.info(f"Sending to {device['Address']}")
        self.l_dest.props.label = device['Alias']

        # Stop discovery if discovering and let adapter settle for a second
        if self.adapter["Discovering"]:
            self.adapter.stop_discovery()
            time.sleep(1)

        self.create_session()

        self.show()

    def create_session(self) -> None:
        self.client.create_session(self.device['Address'], self.adapter["Address"])

    def on_cancel(self, button: Optional[Gtk.Button]) -> None:
        self.pb.props.text = _("Cancelling")
        if button:
            button.props.sensitive = False

        if self.object_push:
            self.client.remove_session(self.object_push.get_session_path())

        self.emit("result", False)

    def on_transfer_started(self, _object_push: ObjectPush, transfer_path: str, filename: str) -> None:
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

        self.transfer = Transfer(obj_path=transfer_path)
        self.transfer.connect("error", self.on_transfer_error)
        self.transfer.connect("progress", self.on_transfer_progress)
        self.transfer.connect("completed", self.on_transfer_completed)

    def on_transfer_failed(self, _object_push: ObjectPush, error: str) -> None:
        self.on_transfer_error(None, str(error))

    def on_transfer_progress(self, _transfer: Transfer, progress: int) -> None:
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
                    eta = ngettext("%(minutes)d Minute", "%(minutes)d Minutes", round(x)) % {"minutes": round(x)}
                else:
                    eta = ngettext("%(seconds)d Second", "%(seconds)d Seconds", round(x)) % {"seconds": round(x)}
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

    def on_transfer_completed(self, _transfer: Transfer) -> None:
        del self.files[-1]
        self.transfer = None

        self.process_queue()

    def process_queue(self) -> None:
        if len(self.files) > 0:
            path = self.files[-1].get_path()
            assert path is not None
            self.send_file(path)
        else:
            self.emit("result", True)

    def send_file(self, file_path: str) -> None:
        logging.info(file_path)
        if self.object_push:
            self.object_push.send_file(file_path)

    def on_transfer_error(self, _transfer: Optional[Transfer], msg: str = "") -> None:
        if not self.error_dialog:
            self.speed.reset()
            parent = self.get_toplevel()
            assert isinstance(parent, Gtk.Container)
            d = ErrorDialog(msg, _("Error occurred while sending file %s") % self.files[-1].get_basename(),
                            modal=True, icon_name="blueman", parent=parent, buttons=Gtk.ButtonsType.NONE)

            if len(self.files) > 1:
                d.add_button(_("Skip"), Gtk.ResponseType.NO)
            d.add_button(_("Retry"), Gtk.ResponseType.YES)
            d.add_button("_Cancel", Gtk.ResponseType.CANCEL)

            if self.object_push:
                self.client.remove_session(self.object_push.get_object_path())

            def on_response(dialog: Gtk.Dialog, resp: int) -> None:
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

    def on_session_added(self, _manager: Manager, session_path: str) -> None:
        self.object_push = ObjectPush(obj_path=session_path)
        self.object_push_handlers.append(self.object_push.connect("transfer-started", self.on_transfer_started))
        self.object_push_handlers.append(self.object_push.connect("transfer-failed", self.on_transfer_failed))
        self.process_queue()

    def on_session_removed(self, _manager: Manager, session_path: str) -> None:
        logging.debug(f"Session removed: {session_path}")
        if self.object_push:
            for handlerid in self.object_push_handlers:
                self.object_push.disconnect(handlerid)
            self.object_push = None

    def on_session_failed(self, _client: Client, msg: BluezDBusException) -> None:
        parent = self.get_toplevel()
        assert isinstance(parent, Gtk.Container)
        d = ErrorDialog(_("Error occurred"), msg.reason.split(None, 1)[1], icon_name="blueman", parent=parent)

        d.run()
        d.destroy()
        self.emit("result", False)

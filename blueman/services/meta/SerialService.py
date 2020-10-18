from gettext import gettext as _
import logging
import os
import subprocess
from typing import Callable, Dict, Optional, List

from gi.repository import Gio, GLib

from blueman.bluez.Adapter import Adapter
from _blueman import create_rfcomm_device, get_rfcomm_channel, RFCOMMError, rfcomm_list
from blueman.Service import Service, Instance
from blueman.bluez.Device import Device
from blueman.main.DBusProxies import Mechanism
from blueman.Constants import RFCOMM_WATCHER_PATH


class SerialService(Service):
    def __init__(self, device: Device, uuid: str) -> None:
        super().__init__(device, uuid)
        self._handlerids: Dict[int, int] = {}

    @property
    def available(self) -> bool:
        # It will ask to pair anyway so not make it available
        paired: bool = self.device["Paired"]
        return paired

    @property
    def connectable(self) -> bool:
        return True

    @property
    def connected_instances(self) -> List[Instance]:
        return [Instance(_("Serial Port %s") % "rfcomm%d" % dev["id"], dev["id"]) for dev in rfcomm_list()
                if dev["dst"] == self.device['Address'] and dev["state"] == "connected"]

    def on_file_changed(
        self,
        monitor: Gio.FileMonitor,
        file: Gio.File,
        _other_file: Gio.File,
        event_type: Gio.FileMonitorEvent,
        port: int
    ) -> None:
        if event_type == Gio.FileMonitorEvent.DELETED:
            logging.info(f'{file.get_path()} got deleted')
            if port in self._handlerids:
                handler_id = self._handlerids.pop(port)
                monitor.disconnect(handler_id)
            else:
                logging.warning(f"No handler id for {port}")
        elif event_type == Gio.FileMonitorEvent.ATTRIBUTE_CHANGED:
            path = file.get_path()
            assert path is not None
            self.try_replace_root_watcher(monitor, path, port)

    def try_replace_root_watcher(self, monitor: Gio.FileMonitor, path: str, port: int) -> None:
        if not os.access(path, os.R_OK | os.W_OK):
            return

        logging.info(f'User was granted access to {path}')
        logging.info('Replacing root watcher')
        Mechanism().CloseRFCOMM('(d)', port)
        subprocess.Popen([RFCOMM_WATCHER_PATH, path])
        if port in self._handlerids:
            handler_id = self._handlerids.pop(port)
            monitor.disconnect(handler_id)
        else:
            logging.warning(f"No handler id for {port}")

    def connect(
        self,
        reply_handler: Optional[Callable[[str], None]] = None,
        error_handler: Optional[Callable[[RFCOMMError], None]] = None
    ) -> bool:
        # We expect this service to have a reserved UUID
        uuid = self.short_uuid
        assert uuid
        channel = get_rfcomm_channel(uuid, self.device['Address'])
        if channel is None or channel == 0:
            error = RFCOMMError("Failed to get rfcomm channel")
            if error_handler:
                error_handler(error)
                return True
            else:
                raise error

        try:
            port_id = create_rfcomm_device(Adapter(obj_path=self.device["Adapter"])['Address'], self.device["Address"],
                                           channel)
            filename = '/dev/rfcomm%d' % port_id
            logging.info('Starting rfcomm watcher as root')
            Mechanism().OpenRFCOMM('(d)', port_id)
            mon = Gio.File.new_for_path(filename).monitor_file(Gio.FileMonitorFlags.NONE)
            self._handlerids[port_id] = mon.connect('changed', self.on_file_changed, port_id)
            self.try_replace_root_watcher(mon, filename, port_id)

            if reply_handler:
                reply_handler(filename)
        except RFCOMMError as e:
            if error_handler:
                error_handler(e)
            else:
                raise e
        return True

    def disconnect(
        self,
        port_id: int,
        reply_handler: Optional[Callable[[], None]] = None,
        error_handler: Optional[Callable[[str], None]] = None
    ) -> None:
        try:
            Mechanism().CloseRFCOMM('(d)', port_id)
        except GLib.Error as e:
            if error_handler:
                error_handler(e.message)
            else:
                raise

        if reply_handler:
            reply_handler()

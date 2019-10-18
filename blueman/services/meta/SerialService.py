# coding=utf-8
import logging
import os
import subprocess
from typing import Callable, Optional

from gi.repository import Gio, GLib

from blueman.bluez.Adapter import Adapter
from _blueman import create_rfcomm_device, get_rfcomm_channel, RFCOMMError
from blueman.Service import Service
from blueman.main.DBusProxies import Mechanism
from blueman.Constants import RFCOMM_WATCHER_PATH


class SerialService(Service):
    @property
    def available(self) -> bool:
        # It will ask to pair anyway so not make it available
        paired: bool = self.device["Paired"]
        return paired

    @property
    def connected(self) -> bool:
        return False

    def on_file_changed(
        self,
        monitor: Gio.FileMonitor,
        file: Gio.File,
        _other_file: Gio.File,
        event_type: Gio.FileMonitorEvent,
        port: int
    ) -> None:
        if event_type == Gio.FileMonitorEvent.DELETED:
            logging.info('%s got deleted' % file.get_path())
            monitor.disconnect_by_func(self.on_file_changed, port)
        elif event_type == Gio.FileMonitorEvent.ATTRIBUTE_CHANGED:
            self.try_replace_root_watcher(monitor, file.get_path(), port)

    def try_replace_root_watcher(self, monitor: Gio.FileMonitor, path: str, port: int) -> None:
        if not os.access(path, os.R_OK | os.W_OK):
            return

        logging.info('User was granted access to %s' % path)
        logging.info('Replacing root watcher')
        Mechanism().CloseRFCOMM('(d)', port)
        subprocess.Popen([RFCOMM_WATCHER_PATH, path])
        monitor.disconnect_by_func(self.on_file_changed, port)

    def connect(
        self,
        reply_handler: Optional[Callable[[str], None]] = None,
        error_handler: Optional[Callable[[RFCOMMError], None]] = None
    ) -> bool:
        channel = get_rfcomm_channel(self.short_uuid, self.device['Address'])
        if channel == 0:
            error = RFCOMMError("Failed to get rfcomm channel")
            if error_handler:
                error_handler(error)
                return True
            else:
                raise error

        try:
            port_id = create_rfcomm_device(Adapter(self.device["Adapter"])['Address'], self.device["Address"], channel)
            filename = '/dev/rfcomm%d' % port_id
            logging.info('Starting rfcomm watcher as root')
            Mechanism().OpenRFCOMM('(d)', port_id)
            mon = Gio.File.new_for_path(filename).monitor_file(Gio.FileMonitorFlags.NONE)
            mon.connect('changed', self.on_file_changed, port_id)
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

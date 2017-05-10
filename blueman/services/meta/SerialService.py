# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
import signal
import subprocess

from gi.repository import Gio

from blueman.bluez.Adapter import Adapter
from _blueman import rfcomm_list, release_rfcomm_device, create_rfcomm_device
from blueman.Service import Service
from blueman.main.Mechanism import Mechanism
from blueman.Constants import RFCOMM_WATCHER_PATH


class SerialService(Service):
    def __init__(self, device, uuid):
        super(SerialService, self).__init__(device, uuid)
        self.file_changed_handler = None

    def serial_port_id(self, channel):
        for dev in rfcomm_list():
            if dev["dst"] == self.device['Address'] and dev["state"] == "connected" and dev["channel"] == channel:
                return dev["id"]

    @property
    def connected(self):
        return False

    def on_file_changed(self, monitor, file, other_file, event_type, port):
        if event_type == Gio.FileMonitorEvent.DELETED:
            logging.info('%s got deleted' % file.get_path())
            monitor.disconnect(self.file_changed_handler)
        elif event_type == Gio.FileMonitorEvent.ATTRIBUTE_CHANGED:
            self.try_replace_root_watcher(monitor, file.get_path(), port)

    def try_replace_root_watcher(self, monitor, path, port):
        if not os.access(path, os.R_OK | os.W_OK):
            return

        logging.info('User was granted access to %s' % path)
        logging.info('Replacing root watcher')
        Mechanism().close_rfcomm(str('(d)'), port)
        subprocess.Popen([RFCOMM_WATCHER_PATH, path])
        monitor.disconnect(self.file_changed_handler)

    def connect(self, reply_handler=None, error_handler=None):
        try:
            channel = 1
            for dev in rfcomm_list():
                if dev["dst"] == self.device['Address']:
                    channel = dev["channel"]
            port_id = create_rfcomm_device(Adapter(self.device["Adapter"])['Address'], self.device["Address"], channel)
            filename = '/dev/rfcomm%d' % port_id
            logging.info('Starting rfcomm watcher as root')
            Mechanism().open_rfcomm(str('(d)'), port_id)
            mon = Gio.File.new_for_path(filename).monitor_file(Gio.FileMonitorFlags.NONE)
            self.file_changed_handler = mon.connect('changed', self.on_file_changed, port_id)
            self.try_replace_root_watcher(mon, filename, port_id)

            if reply_handler:
                reply_handler(filename)
        except Exception as e:
            if error_handler:
                error_handler(e)
            else:
                raise e
        return True

    def disconnect(self, *args):
        Mechanism().close_rfcomm(str('(d)'), args[0])
        release_rfcomm_device(args[0])

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBlueZInterface import PropertiesBlueZInterface
from blueman.bluez.errors import raise_dbus_error, parse_dbus_error
import dbus
import xml.dom.minidom


class Device(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        if self.__class__.get_interface_version()[0] < 5:
            interface = 'org.bluez.Device'
        else:
            interface = 'org.bluez.Device1'
        super(Device, self).__init__(interface, obj_path)

    @raise_dbus_error
    def pair(self, reply_handler=None, error_handler=None):
        # BlueZ 5 only!
        def ok():
            if callable(reply_handler):
                reply_handler()

        def err(e):
            exception = parse_dbus_error(e)
            if callable(error_handler):
                error_handler(exception)
            else:
                raise exception

        self.get_interface().Pair(reply_handler=ok, error_handler=err)

    @raise_dbus_error
    def connect(self, reply_handler=None, error_handler=None):
        # BlueZ 5 only!
        def ok():
            if callable(reply_handler):
                reply_handler()

        def err(e):
            exception = parse_dbus_error(e)
            if callable(error_handler):
                error_handler(exception)
            else:
                raise exception

        self.get_interface().Connect(reply_handler=ok, error_handler=err)

    @raise_dbus_error
    def disconnect(self, reply_handler=None, error_handler=None):
        def ok():
            if callable(reply_handler):
                reply_handler()

        def err(e):
            exception = parse_dbus_error(e)
            if callable(error_handler):
                error_handler(exception)
            else:
                raise exception

        self.get_interface().Disconnect(reply_handler=ok, error_handler=err)

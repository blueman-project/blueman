from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import raise_dbus_error, parse_dbus_error


class Device(PropertiesBase):
    __gproperties__ = {
        str('Alias'): (GObject.TYPE_STRING,
                       'BlueZ Device Alias',
                       None,
                       None,
                       GObject.PARAM_READWRITE)

    def do_get_property(self, prop):
        return self.get(prop.name)

    def do_set_property(self, prop, value):
        return self.set(prop.name, value)

    @raise_dbus_error
    def __init__(self, obj_path=None):
        super(Device, self).__init__('org.bluez.Device1', obj_path)

    @raise_dbus_error
    def pair(self, reply_handler=None, error_handler=None):
        def ok():
            if callable(reply_handler):
                reply_handler()

        def err(e):
            exception = parse_dbus_error(e)
            if callable(error_handler):
                error_handler(exception)
            else:
                raise exception

        self._interface.Pair(reply_handler=ok, error_handler=err)

    @raise_dbus_error
    def connect(self, reply_handler=None, error_handler=None):
        def ok():
            if callable(reply_handler):
                reply_handler()

        def err(e):
            exception = parse_dbus_error(e)
            if callable(error_handler):
                error_handler(exception)
            else:
                raise exception

        self._interface.Connect(reply_handler=ok, error_handler=err)

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

        self._interface.Disconnect(reply_handler=ok, error_handler=err)

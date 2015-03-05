from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBlueZInterface import PropertiesBlueZInterface
from blueman.bluez.errors import raise_dbus_error


class Headset(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        if self.__class__.get_interface_version()[0] < 5:
            interface = 'org.bluez.Headset'
        else:
            interface = 'org.bluez.Headset1'

        super(Headset, self).__init__(interface, obj_path)

    def unhandle_signal(self, handler, signal, **kwargs):
        if signal == 'AnswerRequested':
            self._unhandle_signal(handler, signal, self.get_interface_name(), self.get_object_path(), **kwargs)
        else:
            super(Headset, self).unhandle_signal(handler, signal, **kwargs)

    def handle_signal(self, handler, signal, **kwargs):
        if signal == 'AnswerRequested':
            self._handle_signal(handler, signal, self.get_interface_name(), self.get_object_path(), **kwargs)
        else:
            super(Headset, self).handle_signal(handler, signal, **kwargs)

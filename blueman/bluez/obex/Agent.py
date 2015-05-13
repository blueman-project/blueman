from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
import dbus.service
from gi.repository import GObject
from gi.types import GObjectMeta
from inspect import isclass
from blueman.Functions import dprint
from blueman.bluez.obex.Error import Error


class _GDbusObjectType(dbus.service.InterfaceType, GObjectMeta):
    pass

_GDBusObject = _GDbusObjectType(str('_GDBusObject'), (dbus.service.Object, GObject.GObject), {})


# noinspection PyPep8Naming
class Agent(_GDBusObject, dbus.service.Object, GObject.GObject):
    __gsignals__ = {
        str('release'): (GObject.SignalFlags.NO_HOOKS, None, ()),
        str('authorize'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,
                                                                GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
        str('cancel'): (GObject.SignalFlags.NO_HOOKS, None, ()),
    }

    def __init__(self, agent_path):
        self._agent_path = agent_path
        dbus.service.Object.__init__(self, dbus.SessionBus(), agent_path)
        GObject.GObject.__init__(self)
        self._reply_handler = None
        self._error_handler = None

    @dbus.service.method('org.bluez.obex.Agent1')
    def Release(self):
        dprint(self._agent_path)
        self.emit('release')

    @dbus.service.method('org.bluez.obex.Agent1', async_callbacks=('reply_handler', 'error_handler'))
    def AuthorizePush(self, transfer_path, reply_handler, error_handler):
        dprint(self._agent_path, transfer_path)
        self._reply_handler = reply_handler
        self._error_handler = error_handler
        self.emit('authorize', transfer_path, None, None, None)

    @dbus.service.method('org.bluez.obex.Agent1')
    def Cancel(self):
        dprint(self._agent_path)
        self.emit('cancel')

    @dbus.service.method('org.bluez.obex.Agent', async_callbacks=('reply_handler', 'error_handler'))
    def Authorize(self, transfer_path, bt_address, name, _type, length, _time, reply_handler, error_handler):
        dprint(self._agent_path, transfer_path, bt_address, name, length)
        self._reply_handler = reply_handler
        self._error_handler = error_handler
        self.emit('authorize', transfer_path, bt_address, name, length)

    @dbus.service.method('org.bluez.obex.Agent')
    def Cancel(self):
        dprint(self._agent_path)
        self.emit('cancel')

    def reply(self, reply):
        dprint(self._agent_path, reply)
        if isclass(reply) and issubclass(reply, Error):
            self._error_handler(dbus.DBusException(name=('org.bluez.obex.Error.%s' % reply.__name__)))
        else:
            self._reply_handler(reply)
        self._reply_handler = None
        self._error_handler = None

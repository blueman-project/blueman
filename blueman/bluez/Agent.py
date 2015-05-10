from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
import inspect
import dbus.service
from blueman.bluez.BlueZInterface import BlueZInterface
import blueman.bluez.errors as errors

__SIGNATURES__ = {
    'Release': ('', ''),
    'RequestPinCode': ('o', 's'),
    'RequestPasskey': ('o', 'u'),
    'DisplayPasskey': ('ouu', ''),
    'DisplayPinCode': ('os', ''),
    'RequestConfirmation': ('ou', ''),
    'RequestAuthorization': ('o', ''),
    'Authorize': ('os', ''),
    'AuthorizeService': ('os', ''),
    'Cancel': ('', '')
}


def AgentMethod(func):
    global __SIGNATURES__
    try:
        signatures = __SIGNATURES__[func.__name__]
    except KeyError:
        raise errors.BluezUnavailableAgentMethodError('method name ' + func.__name__ + ' unavailable for agent')
    args = inspect.getargspec(func)[0]
    if len(args) - len(signatures[0]) == 3:
        async_callbacks = (args[-2], args[-1])
    else:
        async_callbacks = None

    if BlueZInterface.get_interface_version()[0] < 5:
        interface = 'org.bluez.Agent'
    else:
        interface = 'org.bluez.Agent1'

    warp = dbus.service.method(interface, in_signature=signatures[0], out_signature=signatures[1],
                               async_callbacks=async_callbacks)
    return warp(func)


class Agent(dbus.service.Object):
    def __init__(self, obj_path):
        self.__obj_path = obj_path
        dbus.service.Object.__init__(self, dbus.SystemBus(), obj_path)

    def get_object_path(self):
        return self.__obj_path

    @AgentMethod
    def Release(self):
        dprint('Release')

    @AgentMethod
    def RequestPinCode(self, device, _ok, _err):
        dprint('RequestPinCode (%s)' % device)

    @AgentMethod
    def RequestPasskey(self, device, _ok, _err):
        dprint('RequestPasskey (%s)' % device)

    @AgentMethod
    def DisplayPasskey(self, device, passkey, entered):
        dprint('DisplayPasskey (%s, %d)' % (device, passkey))

    @AgentMethod
    def DisplayPinCode(self, device, pin_code):
        dprint('DisplayPinCode (%s, %s)' % (device, pin_code))

    @AgentMethod
    def RequestConfirmation(self, device, passkey):
        dprint('RequestConfirmation (%s, %d)' % (device, passkey))

    @AgentMethod
    def RequestAuthorization(self, device):
        dprint('RequestAuthorization (%s)' % device)

    @AgentMethod
    def Authorize(self, device, uuid):
        dprint('Authorize (%s, %s)' % (device, uuid))

    @AgentMethod
    def AuthorizeService(self, device, uuid):
        dprint('AuthorizeService (%s, %s)' % (device, uuid))

    @AgentMethod
    def Cancel(self):
        dprint('Cancel')

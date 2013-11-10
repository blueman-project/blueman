from blueman.Functions import dprint
import inspect
import dbus.service
import errors

__SIGNATURES__ = {
    'Release': ('', ''),
    'RequestPinCode': ('o', 's'),
    'RequestPasskey': ('o', 'u'),
    'DisplayPasskey': ('ouu', ''),
    'RequestConfirmation': ('ou', ''),
    'Authorize': ('os', ''),
    'ConfirmModeChange': ('s', ''),
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
    warp = dbus.service.method('org.bluez.Agent',
                               in_signature=signatures[0],
                               out_signature=signatures[1],
                               async_callbacks=async_callbacks)
    return warp(func)


class Agent(dbus.service.Object):
    def __init__(self, obj_path):
        self.__obj_path = obj_path
        dbus.service.Object.__init__(self, dbus.SystemBus(), obj_path)

    @AgentMethod
    def Release(self):
        dprint('Release')

    @AgentMethod
    def RequestPinCode(self, device):
        dprint('RequestPinCode (%s)' % (device))

    @AgentMethod
    def RequestPasskey(self, device):
        dprint('RequestPasskey (%s)' % (device))

    @AgentMethod
    def DisplayPasskey(self, device, passkey, entered):
        dprint('DisplayPasskey (%s, %d)' % (device, passkey))

    @AgentMethod
    def RequestConfirmation(self, device, passkey):
        dprint('RequestConfirmation (%s, %d)' % (device, passkey))

    @AgentMethod
    def Authorize(self, device, uuid):
        dprint('Authorize (%s, %s)' % (device, uuid))

    @AgentMethod
    def ConfirmModeChange(self, mode):
        dprint('ConfirmModeChange (%s)' % (mode))

    @AgentMethod
    def Cancel(self):
        dprint('Cancel')

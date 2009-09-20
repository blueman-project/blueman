# Agent.py - class Agent and decorator AgentMethod
#
# Copyright (C) 2008 Vinicius Gomes <vcgomes [at] gmail [dot] com>
# Copyright (C) 2008 Li Dongyang <Jerry87905 [at] gmail [dot] com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import inspect
import dbus
import dbus.service
import errors

__SIGNATURES__ = {'Release':('', ''),
                  'RequestPinCode':('o', 's'),
                  'RequestPasskey':('o', 'u'),
                  'DisplayPasskey':('ouu', ''),
                  'RequestConfirmation':('ou', ''),
                  'Authorize':('os', ''),
                  'ConfirmModeChange':('s', ''),
                  'Cancel':('', '')}

def AgentMethod(func):
    '''
    The decorator for customizing the agent methods.
    To use async callbacks, add two extra parameters for
    success callback and error callback in the def of the agent method.
    '''
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
# AgentMethod

class Agent(dbus.service.Object):

    '''
    Represents the BlueZ dbus API on interface "org.bluez.Agent".
    Inherit from this class and use AgentMethod decorator
    to customize the methods.
    The simple-agent is provided by default.
    '''

    def __init__(self, obj_path):
        self.__obj_path = obj_path
        dbus.service.Object.__init__(self, dbus.SystemBus(), obj_path)
    # __init__

    def GetObjectPath(self):
        '''Returns the dbus object path of the agent.'''
        return self.__obj_path
    # GetObjectPath

    @AgentMethod
    def Release(self):
        '''
        This method gets called when the service daemon
        unregisters the agent. An agent can use it to do
        cleanup tasks. There is no need to unregister the
        agent, because when this method gets called it has
        already been unregistered.
        '''
        dprint("Release")
    # Release

    @AgentMethod
    def RequestPinCode(self, device):
        '''
        This method gets called when the service daemon
        needs to get the passkey for an authentication.
        The return value should be a string of 1-16 characters
        length. The string can be alphanumeric.
        '''
        dprint("RequestPinCode (%s)" % (device))

    # RequestPinCode

    @AgentMethod
    def RequestPasskey(self, device):
        '''
        This method gets called when the service daemon
        needs to get the passkey for an authentication.
        The return value should be a numeric value
        between 0-999999.
        '''
        dprint("RequestPasskey (%s)" % (device))

    # RequestPasskey

    @AgentMethod
    def DisplayPasskey(self, device, passkey, entered):
        '''
        This method gets called when the service daemon
        needs to display a passkey for an authentication.
        The entered parameter indicates the number of already
        typed keys on the remote side.
        An empty reply should be returned. When the passkey
        needs no longer to be displayed, the Cancel method
        of the agent will be called.
        During the pairing process this method might be
        called multiple times to update the entered value.
        '''
        dprint("DisplayPasskey (%s, %d)" % (device, passkey))
    # DisplayPasskey

    @AgentMethod
    def RequestConfirmation(self, device, passkey):
        '''
        This method gets called when the service daemon
        needs to confirm a passkey for an authentication.
        To confirm the value it should return an empty reply
        or an error in case the passkey is invalid.
        '''
        dprint("RequestConfirmation (%s, %d)" % (device, passkey))

    # RequestConfirmation

    @AgentMethod
    def Authorize(self, device, uuid):
        '''
        This method gets called when the service daemon
        needs to authorize a connection/service request.
        '''
        dprint("Authorize (%s, %s)" % (device, uuid))
    # Authorize

    @AgentMethod
    def ConfirmModeChange(self, mode):
        '''
        This method gets called if a mode change is requested
        that needs to be confirmed by the user. An example
        would be leaving flight mode.
        '''
        dprint("ConfirmModeChange (%s)" % (mode))
    # ConfirmModeChange

    @AgentMethod
    def Cancel(self):
        '''
        This method gets called to indicate that the agent
        request failed before a reply was returned.
        '''
        dprint("Cancel")
    # Cancel
# Agent

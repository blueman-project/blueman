# Adapter.py - class Adapter
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

import dbus
import types

import Device
import Agent
import errors
from utils import raise_dbus_error
from utils import raise_type_error
from BaseInterface import BaseInterface

class Adapter(BaseInterface):

    '''Represents the BlueZ dbus API on interface"org.bluez.Adapter".'''

    @raise_dbus_error
    def __init__(self, obj_path):
        super(Adapter, self).__init__('org.bluez.Adapter', obj_path)
    # __init__

    @raise_dbus_error
    def GetProperties(self):
        '''
        Returns all properties for the adapter.
        Properties:
        string Address [readonly]
            The Bluetooth device address.
        string Name [readwrite]
            The Bluetooth friendly name. This value can be
            changed and a PropertyChanged signal will be emitted.
        string Mode [readwrite]
            The Bluetooth operation mode.
            Valid modes: "off", "connectable","discoverable", "limited"
        uint32 DiscoverableTimeout [readwrite]
            The discoverable timeout in seconds. A value of zero
            means that the timeout is disabled and it will stay in
            discoverable/limited mode forever.
            The default value for the discoverable timeout should
            be 180 seconds (3 minutes).
        boolean Discovering [readonly]
            Indicates that a device discovery procedure is active.
        '''
        return self.GetInterface().GetProperties()
    # GetProperties

    @raise_dbus_error
    def SetProperty(self, name, value, **kwargs):
        '''
        Changes the value of the specified property. Only
        properties that are listed a read-write are changeable.
        On success this will emit a PropertyChanged signal.
        '''
        if type(value) == types.IntType:
            value = dbus.UInt32(value)
        self.GetInterface().SetProperty(name, value, **kwargs)
    # SetProperty

    @raise_dbus_error
    def RequestMode(self, mode, reply_handler=None, error_handler=None):
        '''
        This method will request a mode change. The mode
        change must be confirmed by the user via the agent.
        Possible modes for this call are "connectable" and
        "discoverable". Any application that wants to use
        Bluetooth functionality can use this method to
        indicate which mode it needs to operate sucessfully.
        In case the user does not confirm the mode change it
        will return an error to indicate this rejection.
        Use reply_handler and error_handler to make asynchronous call.
        reply_handler will not receive any parameters,
        error_handler will receive an exception as the parameter.
        '''
        def error_handler_wrapper(exception):
            exception = errors.parse_dbus_error(exception)
            if not callable(error_handler):
                raise exception
            error_handler(exception)

        if reply_handler is None and error_handler is None:
            self.GetInterface().RequestMode(mode)
        else:
            self.GetInterface().RequestMode(mode,
                                            reply_handler=reply_handler,
                                            error_handler=error_handler_wrapper)
    # RequestMode

    @raise_dbus_error
    def ReleaseMode(self):
        '''Releases a mode requested via RequestMode.'''
        self.GetInterface().ReleaseMode()
    # ReleaseMode

    @raise_dbus_error
    def StartDiscovery(self):
        '''
        This method starts the device discovery session. This
        includes an inquiry procedure and remote device name
        resolving. Use StopDiscovery to release the sessions
        acquired.
        This process will start emitting DeviceFound and
        PropertyChanged "Discovering" signals.
        '''
        self.GetInterface().StartDiscovery()
    # StartDiscovery

    @raise_dbus_error
    def StopDiscovery(self):
        '''
        This method will cancel any previous StartDiscovery
        transaction.
        Note that a discovery procedure is shared between all
        discovery sessions thus calling StopDiscovery will only
        release a single session.
        '''
        self.GetInterface().StopDiscovery()
    # StopDiscovery

    @raise_dbus_error
    def FindDevice(self, address):
        '''
        Returns the Device instance for given address.
        The device object needs to be first created via
        CreateDevice or CreatePairedDevice.
        '''
        obj_path = self.GetInterface().FindDevice(address)
        return Device.Device(obj_path)
    # FindDevice

    @raise_dbus_error
    def ListDevices(self):
        '''Returns list of Device instances.'''
        obj_paths = self.GetInterface().ListDevices()
        devices = []
        for obj_path in obj_paths:
            devices.append(Device.Device(obj_path))
        return devices
    # ListDevices

    @raise_dbus_error
    def CreateDevice(self, address, reply_handler=None, error_handler=None):
        '''
        Creates a new dbus object path for a remote device,
        then returns Device instance. This method will connect to
        the remote device and retrieve all SDP records.
        If the dbus object path for the remote device already exists
        this method will fail.
        '''
        def reply_handler_wrapper(obj_path):
            if not callable(reply_handler):
                return
            reply_handler(Device.Device(obj_path))

        def error_handler_wrapper(exception):
            exception = errors.parse_dbus_error(exception)
            if not callable(error_handler):
                raise exception
            error_handler(exception)

        if reply_handler is None and error_handler is None:
            obj_path = self.GetInterface().CreateDevice(address)
            return Device.Device(obj_path)
        else:
            self.GetInterface().CreateDevice(address,
                                                   reply_handler=reply_handler_wrapper,
                                                   error_handler=error_handler_wrapper)
            return None


    # CreateDevice

    @raise_dbus_error
    def CreatePairedDevice(self, address, agent, capability='', reply_handler=None, error_handler=None):
        '''
        Creates a new object path for a remote device and then
        returns Device instance. This method will connect to
        the remote device and retrieve all SDP records and then
        initiate the pairing.
        If previously CreateDevice was used successfully,
        this method will only initiate the pairing.
        Compared to CreateDevice this method will fail if
        the pairing already exists, but not if the object
        path already has been created. This allows applications
        to use CreateDevice first and the if needed use
        CreatePairedDevice to initiate pairing.
        The capability parameter is the same as for the
        RegisterAgent method.
        Use reply_handler and error_handler to make asynchronous call,
        and this method will return None.
        reply_handler will receive an instance of Device as the parameter,
        error_handler will receive an exception as the parameter.
        '''
        def reply_handler_wrapper(obj_path):
            if not callable(reply_handler):
                return
            reply_handler(Device.Device(obj_path))

        def error_handler_wrapper(exception):
            exception = errors.parse_dbus_error(exception)
            if not callable(error_handler):
                raise exception
            error_handler(exception)

        if reply_handler is None and error_handler is None:
            obj_path = self.GetInterface().CreatePairedDevice(address, agent, capability)
            return Device.Device(obj_path)
        else:
            self.GetInterface().CreatePairedDevice(address,
                                                   agent,
                                                   capability,
                                                   reply_handler=reply_handler_wrapper,
                                                   error_handler=error_handler_wrapper)
            return None
    # CreatePairedDevice

    @raise_dbus_error
    def RemoveDevice(self, device):
        '''
        This removes the remote device dbus object according to
        given Device instance. It will remove also the pairing information.
        '''
        raise_type_error(device, Device.Device)
        self.GetInterface().RemoveDevice(device.GetObjectPath())
    # RemoveDevice

    @raise_dbus_error
    def RegisterAgent(self, agent, capability=''):
        '''
        This registers the adapter wide agent.
        The agent should be an instance of Agent, the methods of Agent
        will be called when user input is needed.
        If an application disconnects from the dbus bus all
        of its registered agents will be removed.
        The capability parameter can have the values
        "DisplayOnly", "DisplayYesNo", "KeyboardOnly" and
        "NoInputNoOutput" which reflects the input and output
        capabilities of the agent. If an empty string is
        used it will fallback to "DisplayYesNo".
        '''
        raise_type_error(agent, Agent.Agent)
        self.GetInterface().RegisterAgent(agent.GetObjectPath(), capability)
    # RegisterAgent

    @raise_dbus_error
    def UnregisterAgent(self, agent):
        '''
        This unregisters the agent that has been previously
        registered.
        '''
        raise_type_error(agent, Agent.Agent)
        self.GetInterface().UnregisterAgent(agent.GetObjectPath())
    # UnregisterAgent
# Adapter

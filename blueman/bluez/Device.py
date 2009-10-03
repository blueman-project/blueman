# Device.py - class Device
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

from utils import raise_dbus_error
from BaseInterface import BaseInterface

class Device(BaseInterface):

    '''Represents the BlueZ dbus API on interface "org.bluez.Device".'''

    @raise_dbus_error
    def __init__(self, obj_path):
        super(Device, self).__init__('org.bluez.Device', obj_path)
    # __init__

    @raise_dbus_error
    def GetProperties(self):
        '''
        Returns all properties for the device.
        Properties:
            string Address [readonly]
                The Bluetooth device address of the remote device.
            string Name [readonly]
                The Bluetooth remote name. This value can not be
                changed. Use the Alias property instead.
            uint32 Class [readonly]
                The Bluetooth class of device of the remote device.
            array{string} UUIDs [readonly]
                List of 128-bit UUIDs that represents the available
                remote services.
            boolean Paired [readonly]
                Indicates if the remote device is paired.
            boolean Connected [readonly]
                Indicates if the remote device is currently connected.
                A PropertyChanged signal indicate changes to this
                status.
            boolean Trusted [readwrite]
                Indicates if the remote is seen as trusted. This
                setting can be changed by the application.
            string Alias [readwrite]
                The name alias for the remote device. The alias can
                be used to have a different friendly name for the
                remote device.
                In case no alias is set, it will return the remote
                device name. Setting an empty string as alias will
                convert it back to the remote device name.
                When reseting the alias with an empty string, the
                emitted PropertyChanged signal will show the remote
                name again.
            object Adapter [readonly]
                The object path of the adpater the device belongs to.
        '''
        return self.GetInterface().GetProperties()
    # GetProperties

    @raise_dbus_error
    def SetProperty(self, name, value):
        '''
        Changes the value of the specified property. Only
        properties that are listed a read-write are changeable.
        On success this will emit a PropertyChanged signal.
        '''
        self.GetInterface().SetProperty(name, value)
    # SetProperty

    @raise_dbus_error
    def DiscoverServices(self, pattern):
        '''
        This method starts the service discovery to retrieve
        remote service records. The pattern parameter can
        be used to specific specific UUIDs.
        The return value is a dictionary with the record
        handles as keys and the service record in XML format
        as values. The key is uint32 and the value a string
        for this dictionary.
        '''
        return self.GetInterface().DiscoverServices(pattern)
    # DiscoverServices

    @raise_dbus_error
    def CancelDiscovery(self):
        '''
        This method will cancel any previous DiscoverServices
        transaction.
        '''
        self.GetInterface().CancelDiscovery()
    # CancelDiscovery

    @raise_dbus_error
    def Disconnect(self, *args, **kwargs):
        '''
        This method disconnects a specific remote device by
        terminating the low-level ACL connection. The use of
        this method should be restricted to administrator
        use.
        A DisconnectRequested signal will be sent and the
        actual disconnection will only happen 2 seconds later.
        This enables upper-level applications to terminate
        their connections gracefully before the ACL connection
        is terminated.
        '''
        self.GetInterface().Disconnect(*args, **kwargs)
    # Disconnect
# Device

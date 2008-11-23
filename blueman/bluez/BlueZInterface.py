# BlueZInterface.py - the base class of other BlueZ interface classes
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

from utils import raise_type_error

class BlueZInterface(object):

    '''the base class of other BlueZ interface classes.'''

    def __init__(self, interface_name, obj_path):
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        self.__bus = dbus.SystemBus()
        self.__dbus_proxy = self.__bus.get_object('org.bluez', obj_path, follow_name_owner_changes=True)
        self.__interface = dbus.Interface(self.__dbus_proxy, interface_name)
    # __init__

    def GetObjectPath(self):
        return self.__obj_path
    # GetObjectPath

    def GetInterface(self):
        return self.__interface
    # GetInterface

    def GetInterfaceName(self):
        return self.__interface_name
    # GetInterfaceName

    def HandleSignal(self, handler, signal, **kwargs):
        '''
        The handler function will be called when specific signal is emmited.
        For available signals of each interface, check BlueZ4 documents.
        '''
       # raise_type_error(handler, types.FunctionType)
        raise_type_error(signal, types.StringType)
        self.__bus.add_signal_receiver(handler,
                                       signal,
                                       self.__interface_name,
                                       'org.bluez',
                                       self.__obj_path, **kwargs)
    def UnHandleSignal(self, handler, signal, **kwargs):
        '''
        The handler function will be called when specific signal is emmited.
        For available signals of each interface, check BlueZ4 documents.
        '''
       # raise_type_error(handler, types.FunctionType)
        raise_type_error(signal, types.StringType)
        self.__bus.remove_signal_receiver(handler,
                                       signal,
                                       self.__interface_name,
                                       'org.bluez',
                                       self.__obj_path, **kwargs)
    # HandleSignal
# BlueZInterface

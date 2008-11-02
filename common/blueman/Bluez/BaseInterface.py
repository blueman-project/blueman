# BaseInterface.py - abstraction of BlueZ base interfaces
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
import xml.dom.minidom

from BlueZInterface import BlueZInterface
from ServiceInterface import ServiceInterface

class BaseInterface(BlueZInterface):

    def __init__(self, interface_name, obj_path):
        super(BaseInterface, self).__init__(interface_name, obj_path)
    # __init__

    def ListServiceInterfaces(self):
        '''
        Returns a list of available service interfaces under current object path,
        for available methods for each interface, check BlueZ4 documents.
        '''
        interfaces = []
        dbus_object = dbus.SystemBus().get_object('org.bluez', self.GetObjectPath())
        dbus_introspect = dbus.Interface(dbus_object, 'org.freedesktop.DBus.Introspectable')
        introspect_xml = dbus_introspect.Introspect()
        root_node = xml.dom.minidom.parseString(introspect_xml)
        for interface in root_node.getElementsByTagName('interface'):
            interface_name = interface.getAttribute('name')
            if interface_name != self.GetInterfaceName():
                methods = []
                for method in interface.getElementsByTagName('method'):
                    methods.append(method.getAttribute('name'))
                interfaces.append(ServiceInterface(interface_name, self.GetObjectPath(), methods))
        return interfaces
    # ListServiceInterfaces
# BaseInterface

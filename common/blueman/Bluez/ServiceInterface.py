# ServiceInterface.py - interface of BlueZ service plugins
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
from BlueZInterface import BlueZInterface

class ServiceInterface(BlueZInterface):

    @raise_dbus_error
    def __init__(self, interface, obj_path, methods):
        self.methods = methods
        super(ServiceInterface, self).__init__(interface, obj_path)
    # __init__

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, 'methods'):
            func = getattr(self.GetInterface(), name)
            return raise_dbus_error(func)
        else:
            return super(ServiceInterface, self).__getattribute__(name)
    # __getattribute__
# ServiceInterface

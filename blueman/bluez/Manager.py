# Manager.py - class Manager
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

import Adapter
import Agent
import errors
from utils import raise_dbus_error
from BaseInterface import BaseInterface

class Manager(BaseInterface):

    '''
    Represents the BlueZ dbus API on interface "org.bluez.Manager".
    Pass the name of the mainloop as a string to __init__.
    The mainloop support could not be changed after the first init of Manager.
    Supported mainloops are gobject, pyqt4 and ecore, use your perferred one.
    And gobject is supported by dbus-python natively.
    If you wanna use pyqt4 or ecore, make sure you have python bindings for them.
    '''

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Manager, cls).__new__(cls)
        return cls._instance
    # __new__

    @raise_dbus_error
    def __init__(self, mainloop):
        try:
            if self.__mainloop_support:
                pass
        except AttributeError:
            self.__setup_event_loop(mainloop)
        super(Manager, self).__init__('org.bluez.Manager', '/')
    # __init__

    def __setup_event_loop(self, mainloop):
        def parse_gobject_mainloop(mainloop):
            try:
                import dbus.mainloop.glib
            except ImportError:
                raise errors.DBusMainLoopModuleNotFoundError('Can not find module for ' + mainloop)
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            return True

        def parse_pyqt4_mainloop(mainloop):
            try:
                import dbus.mainloop.qt
            except ImportError:
                raise errors.DBusMainLoopModuleNotFoundError('Can not find module for ' + mainloop)
            dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
            return True

        def parse_ecore_mainloop(mainloop):
            try:
                import e_dbus
            except ImportError:
                raise errors.DBusMainLoopModuleNotFoundError('Can not find module for ' + mainloop)
            e_dbus.DBusEcoreMainLoop(set_as_default=True)
            return True

        _supported_mainloops = {'gobject':parse_gobject_mainloop,
                                'pyqt4':parse_pyqt4_mainloop,
                                'ecore':parse_ecore_mainloop}
        if (not isinstance(mainloop, str)) or (not _supported_mainloops.has_key(mainloop)):
            raise errors.DBusMainLoopNotSupportedError('Supported mainloops are gobject, pyqt4 and ecore')
        else:
            parse_mainloop = _supported_mainloops.get(mainloop)
            if parse_mainloop(mainloop):
                self.__mainloop_support = True
    # __setup_event_loop

    @raise_dbus_error
    def GetAdapter(self, pattern=None):
        '''
        Returns an instance of Adaper for specified adapter,
        valid patterns are "hci0" or "00:11:22:33:44:55".
        Or returns default BlueZ if pattern is None.
        '''
        if pattern is not None:
            obj_path = self.GetInterface().FindAdapter(pattern)
        else:
            obj_path = self.GetInterface().DefaultAdapter()
        return Adapter.Adapter(obj_path)
    # GetAdapter

    @raise_dbus_error
    def ListAdapters(self):
        '''Returns a list of Adapter instances.'''
        obj_paths = self.GetInterface().ListAdapters()
        adapters = []
        for obj_path in obj_paths:
            adapters.append(Adapter.Adapter(obj_path))
        return adapters
    # ListAdapters

    def CreateAgent(self, cls=Agent.Agent, obj_path='/org/bluez/Agent'):
        '''
        Paramater cls should be a custom sub-class of Agent.
        Paramater obj_path is the dbus object path for the agent, should start with '/'.
        Returns an instance of specified cls.
        '''
        if not issubclass(cls, Agent.Agent):
            raise TypeError('Expecting a subclass of Agent')
        return cls(obj_path)
    # CreateAgent
# Manager

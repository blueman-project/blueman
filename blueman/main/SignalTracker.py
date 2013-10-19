# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
from blueman.bluez.BlueZInterface import BlueZInterface
import dbus
import gobject
import traceback


class SignalTracker:
    def __init__(self):
        self._signals = []

    def Handle(self, *args, **kwargs):
        auto = not type(args[0]) == str
        if "sigid" in kwargs:
            sigid = kwargs["sigid"]
            del kwargs["sigid"]
        else:
            sigid = None

        if auto:
            obj = args[0]
            args = args[1:]
            if isinstance(obj, BlueZInterface):
                objtype = "bluez"
            elif isinstance(obj, gobject.GObject):
                objtype = "gobject"
            elif isinstance(obj, dbus.proxies.Interface):
                objtype = "dbus"
            else:
                raise Exception, "Unknown object type"
        else:
            objtype = args[0]
            obj = args[1]
            args = args[2:]

        if objtype == "bluez":
            obj.HandleSignal(*args, **kwargs)
        elif objtype == "gobject":
            args = obj.connect(*args)
        elif objtype == "dbus":
            if isinstance(obj, dbus.Bus):
                obj.add_signal_receiver(*args, **kwargs)
            else:
                print "Deprecated use of dbus signaltracker"
                traceback.print_stack()
                obj.bus.add_signal_receiver(*args, **kwargs)

        self._signals.append((sigid, objtype, obj, args, kwargs))

    def Disconnect(self, sigid):
        for sig in self._signals:
            (_sigid, objtype, obj, args, kwargs) = sig
            if sigid != None and _sigid == sigid:
                if objtype == "bluez":
                    obj.UnHandleSignal(*args)
                elif objtype == "gobject":
                    obj.disconnect(args)
                elif objtype == "dbus":
                    if isinstance(obj, dbus.Bus):
                        if "path" in kwargs:
                            obj.remove_signal_receiver(*args, **kwargs)
                        else:
                            obj.remove_signal_receiver(*args)
                    else:
                        obj.bus.remove_signal_receiver(*args)

                self._signals.remove(sig)


    def DisconnectAll(self):
        for sig in self._signals:

            (sigid, objtype, obj, args, kwargs) = sig
            if objtype == "bluez":
                obj.UnHandleSignal(*args)
            elif objtype == "gobject":
                obj.disconnect(args)
            elif objtype == "dbus":
                if isinstance(obj, dbus.Bus):
                    if "path" in kwargs:
                        obj.remove_signal_receiver(*args, **kwargs)
                    else:
                        obj.remove_signal_receiver(*args)
                else:
                    obj.bus.remove_signal_receiver(*args)

        self._signals = []

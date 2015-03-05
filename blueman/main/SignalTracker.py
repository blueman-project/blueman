from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from gi.repository import GObject
import traceback


class SignalTracker:
    def __init__(self):
        self._signals = []

    def Handle(self, *args, **kwargs):
        auto = not (hasattr(args[0], "upper") and hasattr(args[0], "format"))
        if "sigid" in kwargs:
            sigid = kwargs["sigid"]
            del kwargs["sigid"]
        else:
            sigid = None

        if auto:
            obj = args[0]
            args = args[1:]
            from blueman.bluez.BlueZInterface import BlueZInterface
            if isinstance(obj, BlueZInterface):
                objtype = "bluez"
            elif isinstance(obj, GObject.GObject):
                objtype = "gobject"
            elif isinstance(obj, dbus.proxies.Interface):
                objtype = "dbus"
            else:
                raise Exception("Unknown object type")
        else:
            objtype = args[0]
            obj = args[1]
            args = args[2:]

        if objtype == "bluez":
            obj.handle_signal(*args, **kwargs)
        elif objtype == "gobject":
            args = obj.connect(*args)
        elif objtype == "dbus":
            if isinstance(obj, dbus.Bus):
                obj.add_signal_receiver(*args, **kwargs)
            else:
                print("Deprecated use of dbus signaltracker")
                traceback.print_stack()
                obj.bus.add_signal_receiver(*args, **kwargs)

        self._signals.append((sigid, objtype, obj, args, kwargs))

    def Disconnect(self, sigid):
        for sig in self._signals:
            (_sigid, objtype, obj, args, kwargs) = sig
            if sigid != None and _sigid == sigid:
                if objtype == "bluez":
                    obj.unhandle_signal(*args)
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
                obj.unhandle_signal(*args)
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

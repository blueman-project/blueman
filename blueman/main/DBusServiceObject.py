#
# Copyright (C) 2010 Martin Pitt <martin@piware.de>
# Copyright (C) 2016 Patrick Griffis <tingping@tingping.se>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import inspect
import logging
from xml.etree import ElementTree
from gi.repository import (
    GLib,
    GObject,
    Gio
)

__all__ = ['dbus_method', 'dbus_property', 'dbus_signal', 'DBusServiceObject']

class DBusAnnotationInfo:
    def __init__(self):
        key = None
        value = None
        annotations = []

class DBusArgInfo:
    def __init__(self, name="", signature=""):
        self.name = name
        self.signature = signature

class DBusMethodInfo:
    def __init__(self, name="", interface=None, in_args=[], out_args=[], invocation=None, annotations=[]):
        self.name = name
        self.interface = interface
        self.in_args = in_args
        self.out_args = out_args
        self.invocation = invocation
        self.annotations = annotations

    def generate_xml(self):
        method = ElementTree.Element('method', {'name': self.name})
        for arg in self.in_args:
            ElementTree.SubElement(method, 'arg', {'name': arg.name,
                                           'type': arg.signature,
                                           'direction': 'in'})
        for arg in self.out_args:
            ElementTree.SubElement(method, 'arg', {'name': arg.name,
                                           'type': arg.signature,
                                           'direction': 'out'})
        return method

class DBusSignalInfo:
    def __init__(self, name="", args=[], annotations=[], interface=None):
        self.name = name
        self.args = args
        self.annotations = annotations
        self.interface = interface

    def generate_xml(self):
        signal = ElementTree.Element('signal', {'name': self.name})
        for arg in self.args:
            ElementTree.SubElement(signal, 'arg', {'name': arg.name, 'type': arg.signature})
        return signal

class DBusPropertyInfo:
    def __init__(self, name="", interface=None, signature=[], flags=Gio.DBusPropertyInfoFlags.NONE, annotations=[]):
        self.name = name
        self.interface = interface
        self.signature = signature
        self.flags = flags
        self.annotations = annotations

    def generate_xml(self):
        access = ''
        if self.flags & Gio.DBusPropertyInfoFlags.READABLE:
            access += 'read'
        if self.flags & Gio.DBusPropertyInfoFlags.WRITABLE:
            access += 'write'

        prop = ElementTree.Element('property', {'name': self.name,
                                                'type': self.signature,
                                                'access': access})
        return prop

class DBusInterfaceInfo:
    def __init__(self, name=''):
        self.name = name
        self.methods = []
        self.signals = []
        self.properties = []
        self.annotations = []

    def generate_xml(self, indent=0):
        interface = ElementTree.Element('interface', {'name': self.name})
        for member in self.methods + self.properties + self.annotations + self.signals:
            interface.append(member.generate_xml())
        return interface

class DBusNodeInfo:
    def __init__(self, path=""):
        self.path = path
        self.interfaces = {}
        self.nodes = []
        self.annotations = []

    def generate_xml(self, indent=0):
        node = ElementTree.Element('node', {'name': self.path})
        for interface in self.interfaces.values():
            node.append(interface.generate_xml())
        return node

class DBusMethodInvocation(object):
    def __init__(self, invocation, signature):
        self._invocation = invocation
        self._signature = signature

    def return_error(self, error):
        if isinstance(error, GLib.Error):
            message = error.message
        else:
            message = str(error)
        self._invocation.return_error_literal(
            Gio.dbus_error_quark(),
            Gio.DBusError.FAILED,
            message
        )

    def return_value(self, value=None):
        if value is None or self._signature is None:
            self._invocation.return_value(None)
            return

        try:
            param = GLib.Variant('(%s)' % self._signature, (value,))
            self._invocation.return_value(param)
        except Exception as e:
            self.return_error(e)

    @property
    def invocation(self):
        return self._invocation

    @property
    def sender(self):
        return self._invocation.get_sender()

    @property
    def path(self):
        return self._invocation.get_object_path()

def _create_arginfo_list(func, signature, invocation_keyword=None):
    arg_names = inspect.getargspec(func).args
    signature_list = GLib.Variant.split_signature('(%s)' %signature) if signature else []
    arg_names.pop(0) # eat "self" argument

    if invocation_keyword and invocation_keyword in arg_names:
        arg_names.remove(invocation_keyword)

    if len(signature_list) != len(arg_names):
        raise TypeError('Specified signature %s for method %s does not match length of arguments'
                        %(str(signature_list), func.__name__))

    args = []
    for arg_signature, arg_name in zip(signature_list, arg_names):
        args.append(DBusArgInfo(name=arg_name, signature=arg_signature))
    return args

def dbus_method(interface, in_signature=None, out_signature=None, invocation_keyword=None):
    def decorator(func):
        in_args = _create_arginfo_list(func, in_signature, invocation_keyword)
        out_args = [DBusArgInfo(name='return', signature=out_signature),] if out_signature else []
        func._dbus_info = DBusMethodInfo(name=func.__name__,
                                         interface=interface,
                                         in_args=in_args,
                                         out_args=out_args,
                                         invocation=invocation_keyword)
        return func

    return decorator

def dbus_signal(interface, signature=None):
    def decorator(func):
        args = _create_arginfo_list(func, signature)
        info = DBusSignalInfo(name=func.__name__,
                                   interface=interface,
                                   args=args)

        def wrapper(self, *args):
            params = GLib.Variant('(%s)' %signature, args) if signature else None
            try:
                self.connection.emit_signal(None, self.object_path,
                                            interface, func.__name__,
                                            params)
            except GLib.Error as e:
                logging.warning('Failed to emit signal:', e)
            func(self, *args)

        wrapper._dbus_info = info
        return wrapper

    return decorator

class dbus_property(object):
    def __init__(self, interface, signature, fget=None, fset=None):
        # check if fget is a data descriptor => a property
        if hasattr(fget, '__set__') and hasattr(fget, '__get__'):
            self.fget = None
            self.wrapped = fget
            prop = self.wrapped
        else:
            self.fget = fget
            self.wrapped = None
            prop = self
        self.fset = fset

        flags = Gio.DBusPropertyInfoFlags.NONE
        if prop.fget is not None:
            flags |= Gio.DBusPropertyInfoFlags.READABLE
        if prop.fset is not None:
            flags |= Gio.DBusPropertyInfoFlags.WRITABLE
        self._dbus_info = DBusPropertyInfo(interface=interface,
                                          signature=signature,
                                          flags=flags)

    def __call__(self, arg):
        # check if we're decorating a data descriptor => a property
        if hasattr(arg, '__set__') and hasattr(arg, '__get__'):
            self.wrapped = arg
            return self
        return self.getter(arg)

    def __get__(self, obj, type):
        if obj is None:
            return self
        if self.wrapped is not None:
            return self.wrapped.__get__(obj, type)
        if self.fget is None:
            raise AttributeError('unreadable attribute')
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.wrapped is not None:
            return self.wrapped.__set__(obj, value)
        if self.fset is None:
            raise AttributeError('can\'t set attribute')
        return self.fset(obj, value)

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def getter(self, fget):
        if self.wrapped is not None:
            return type(self)(interface=self._dbus_info.interface,
                              signature=self._dbus_info.signature,
                              fget=self.wrapped.getter(fget))
        else:
            return type(self)(interface=self._dbus_info.interface,
                              signature=self._dbus_info.signature,
                              fget=fget,
                              fset=self.fset)

    def setter(self, fset):
        if self.wrapped is not None:
            return type(self)(interface=self._dbus_info.interface,
                              signature=self._dbus_info.signature,
                              fget=self.wrapped.setter(fset))
        else:
            return type(self)(interface=self._dbus_info.interface,
                              signature=self._dbus_info.signature,
                              fget=self.fget,
                              fset=fset)


class DBusServiceObject(GObject.Object):
    object_path = GObject.Property(type=str,
                                   flags=GObject.ParamFlags.READWRITE|GObject.ParamFlags.CONSTRUCT_ONLY)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dbus_info = DBusNodeInfo(path=self.object_path)
        self.__dbus_regids = []

        if self.connection:
            self.__dbus_export()

    def __del__(self):
        if self.connection:
            self.__dbus_unexport()

    @GObject.Property(type=Gio.DBusConnection,
                      flags=GObject.ParamFlags.READWRITE|GObject.ParamFlags.CONSTRUCT)
    def connection(self):
        return self.__connection

    @connection.setter
    def __set_connection(self, conn):
        prev = None if not hasattr(self, '__connection') else self.__connection
        if prev:
            self.__dbus_unexport()
        self.__connection = conn
        if prev and self.__connection:
            # Only export on changes otherwise it is done during init
            self.__dbus_export()

    def __dbus_export(self):
        for id in dir(self):
            # don't use getattr(self, id) as default to avoid calling
            # __get__ of properties (which may not have been initialized)
            attr = getattr(type(self), id, None)
            if attr is None:
                attr = getattr(self, id)
            try:
                info = attr._dbus_info
                interface = self.__dbus_info.interfaces.setdefault(
                    info.interface, DBusInterfaceInfo(name=info.interface))
            except AttributeError:
                continue

            if isinstance(info, DBusMethodInfo):
                interface.methods.append(info)
            elif isinstance(info, DBusPropertyInfo):
                # the name of properties is determined by its attribute name
                info.name = info.name or id
                interface.properties.append(info)
            elif isinstance(info, DBusSignalInfo):
                interface.signals.append(info)

        xml = ElementTree.tostring(self.__dbus_info.generate_xml(), encoding='unicode')
        node_info = Gio.DBusNodeInfo.new_for_xml(xml)
        logging.debug('--- XML: ---\n%s\n-------' %node_info.generate_xml(0).str)

        for interface in self.__dbus_info.interfaces:
            regid = self.connection.register_object(
                self.__dbus_info.path,
                node_info.lookup_interface(interface),
                self.__dbus_method_call,
                self.__dbus_get_property,
                self.__dbus_set_property
            )
            self.__dbus_regids.append(regid)

    def __dbus_unexport(self):
        for reg_id in self.__dbus_regids:
            self.connection.unregister_object(reg_id)
        self.regids = []
        self.__dbus_info = DBusNodeInfo(path=self.object_path)

    def _refresh_dbus_registration(self):
        # Used when plugins are (un)loaded
        self.__dbus_unexport()
        self.__dbus_export()

    def __dbus_method_call(self, conn, sender, object_path, iface_name, method_name,
                           parameters, invocation):

        try:
            method = getattr(self, method_name)
            info = method._dbus_info
        except AttributeError:
            invocation.return_error_literal(Gio.dbus_error_quark(),
                    Gio.DBusError.UNKNOWN_METHOD,
                    'No such interface or method: %s.%s' % (iface_name, method_name))
            return

        kwargs = {}
        if info.invocation:
            if len(info.out_args) > 0:
                signature = info.out_args[0].signature
            else:
                signature = None

            method_invocation = DBusMethodInvocation(invocation, signature)
            kwargs[info.invocation] = method_invocation

        try:
            ret = method(*parameters.unpack(), **kwargs)
            if info.invocation:
                # Consumer responsible to handle reply
                return

            if ret is None and not info.out_args:
                invocation.return_value(None)
            else:
                invocation.return_value(GLib.Variant('(%s)' %info.out_args[0].signature, (ret,)))
        except Exception as e:
            invocation.return_error_literal(Gio.dbus_error_quark(),
                    Gio.DBusError.IO_ERROR,
                    'Method %s.%s failed with: %s' % (iface_name, method_name, str(e)))

    def __dbus_get_property(self, conn, sender, object_path, iface_name, prop_name):
        try:
            info = getattr(type(self), prop_name)._dbus_info
            ret = getattr(self, prop_name)
        except AttributeError:
            return None
        return GLib.Variant(info.signature, ret)

    def __dbus_set_property(self, conn, sender, object_path, iface_name, prop_name, value):
        try:
            info = getattr(type(self), prop_name)._dbus_info
            ret = setattr(self, prop_name, value.unpack())
        except AttributeError:
            return False
        return True

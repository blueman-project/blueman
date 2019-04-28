# coding=utf-8

import logging
import sys
import traceback

from gi.repository import Gio, GLib


class DbusError(Exception):
    _name = "org.blueman.Error"

    def __init__(self, message=None):
        self._message = message

    @property
    def name(self):
        return self._name

    @property
    def message(self):
        return self._message


class DbusService:
    def __init__(self, bus_name, interface_name, path, bus_type):
        self._bus = Gio.bus_get_sync(bus_type)
        if bus_name:
            Gio.bus_own_name(bus_type, bus_name, Gio.BusNameOwnerFlags.NONE, None, None, None)
        self._methods = {}
        self._signals = {}
        self._interface_name = interface_name
        self._path = path
        self._regid = None

    def add_method(self, name, arguments, return_value, method, pass_sender=False, is_async=False):
        if name in self._signals:
            raise Exception("%s already defined" % name)

        options = set()
        if pass_sender:
            options.add("sender")
        if is_async:
            options.add("async")
        self._methods[name] = (arguments, return_value, method, options)
        self._reregister()

    def remove_method(self, name):
        del self._methods[name]
        self._reregister()

    def add_signal(self, name, signature):
        if name in self._signals:
            raise Exception("%s already defined" % name)

        self._signals[name] = signature
        self._reregister()

    def remove_signal(self, name):
        del self._signals[name]
        self._reregister()

    def emit_signal(self, name, *args):
        self._bus.emit_signal(None, self._path, self._interface_name, name,
                              self._prepare_arguments(self._signals[name], args))

    def register(self):
        node_xml = "<node name='/'><interface name='%s'>" % self._interface_name
        for method_name, method_info in self._methods.items():
            node_xml += "<method name='%s'>" % method_name
            for argument in method_info[0]:
                node_xml += "<arg type='%s' direction='in'/>" % argument
            if method_info[1]:
                node_xml += "<arg type='%s' direction='out'/>" % method_info[1]
            node_xml += "</method>"
        for signal_name, signal_signature in self._signals.items():
            node_xml += "<signal name='%s'>" % signal_name
            if signal_signature:
                node_xml += "<arg type='%s'/>" % signal_signature
            node_xml += "</signal>"
        node_xml += "</interface></node>"

        node_info = Gio.DBusNodeInfo.new_for_xml(node_xml)

        regid = self._bus.register_object(
            self._path,
            node_info.interfaces[0],
            self._handle_method_call,
            None,
            None)

        if regid:
            self._regid = regid
        else:
            raise GLib.Error('Failed to register object with path: %s', self._path)

    def unregister(self):
        self._bus.unregister_object(self._regid)
        self._regid = None

    def _reregister(self):
        if self._regid:
            self.unregister()
            self.register()

    def _handle_method_call(self, _connection, sender, _path, interface_name, method_name, parameters, invocation):
        try:
            try:
                _arguments, result_signature, method, options = self._methods[method_name]
            except KeyError:
                logging.warning('Unhandled method: %s' % method_name)
                invocation.return_error_literal(Gio.dbus_error_quark(), Gio.DBusError.UNKNOWN_METHOD,
                                                "No such method on interface: %s.%s" % (interface_name, method_name))

            def ok(*result):
                invocation.return_value(self._prepare_arguments(result_signature, result))

            args = parameters.unpack()
            if "sender" in options:
                args += (sender,)
            if "async" in options:
                method(*(args + (ok, lambda exception: self._return_dbus_error(invocation, exception))))
            else:
                ok(method(*args))
        except Exception as e:
            self._return_dbus_error(invocation, e)

    @staticmethod
    def _return_dbus_error(invocation, data):
        if isinstance(data, DbusError):
            invocation.return_dbus_error(data.name, data.message)
        else:
            if isinstance(data, Exception):
                et, ev, etb = sys.exc_info()
                if ev is data:
                    message = "".join(traceback.format_exception(et, ev, etb))
                else:
                    message = "".join(traceback.format_exception_only(data.__class__, data))
            else:
                message = str(data)
            invocation.return_error_literal(Gio.dbus_error_quark(), Gio.DBusError.FAILED, message)

    @staticmethod
    def _prepare_arguments(signature, args):
        return GLib.Variant("(%s)" % signature, args) if signature else None

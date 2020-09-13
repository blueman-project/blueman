import logging
import sys
import traceback
from typing import Dict, Tuple, Callable, Set, Optional, Any, Collection, Mapping, Union, overload, TYPE_CHECKING

from gi.repository import Gio, GLib

if TYPE_CHECKING:
    from typing_extensions import Literal


class DbusError(Exception):
    _name = "org.blueman.Error"

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def name(self) -> str:
        return self._name

    @property
    def message(self) -> str:
        return self._message


class DbusService:
    def __init__(self, bus_name: Optional[str], interface_name: str, path: str, bus_type: Gio.BusType,
                 properties: Optional[Mapping[str, str]] = None) -> None:
        self._bus = Gio.bus_get_sync(bus_type)
        if bus_name:
            Gio.bus_own_name(bus_type, bus_name, Gio.BusNameOwnerFlags.NONE, None, None, None)
        self._methods: Dict[str, Tuple[Tuple[str, ...], Tuple[str, ...], Callable[..., None], Set[str]]] = {}
        self._signals: Dict[str, Tuple[str, ...]] = {}
        self._properties = {} if properties is None else properties
        self._interface_name = interface_name
        self._path = path
        self._regid: Optional[int] = None

    @overload
    def add_method(self, name: str, arguments: Tuple[str, ...], return_values: Union[str, Tuple[str, ...]],
                   method: Callable[..., None], pass_sender: bool = False, is_async: bool = False) -> None:
        ...

    @overload
    def add_method(self, name: str, arguments: Tuple[str, ...], return_values: Tuple[str, ...],
                   method: Callable[..., Any], pass_sender: bool = False,
                   is_async: "Literal[False]" = False) -> None:
        ...

    def add_method(self, name: str, arguments: Tuple[str, ...], return_values: Union[str, Tuple[str, ...]],
                   method: Callable[..., Any], pass_sender: bool = False, is_async: bool = False) -> None:
        if name in self._signals:
            raise Exception(f"{name} already defined")

        options = set()
        if pass_sender:
            options.add("sender")
        if is_async:
            options.add("async")
        self._methods[name] = (arguments, self._handle_return_type(return_values), method, options)
        self._reregister()

    def remove_method(self, name: str) -> None:
        del self._methods[name]
        self._reregister()

    def add_signal(self, name: str, types: Union[str, Tuple[str, ...]]) -> None:
        if name in self._signals:
            raise Exception(f"{name} already defined")

        self._signals[name] = self._handle_return_type(types)
        self._reregister()

    def _handle_return_type(self, types: Union[str, Tuple[str, ...]]) -> Tuple[str, ...]:
        if isinstance(types, str):
            if types:
                # A non-empty string is a single return type
                return types,
            else:
                # An empty string is no return type
                return ()
        else:
            return types

    def remove_signal(self, name: str) -> None:
        del self._signals[name]
        self._reregister()

    def emit_signal(self, name: str, *args: Any) -> None:
        self._bus.emit_signal(None, self._path, self._interface_name, name,
                              self._prepare_arguments(self._signals[name], args))

    def register(self) -> None:
        node_xml = f"<node name='/'><interface name='{self._interface_name}'>"
        for property_name, signature in self._properties.items():
            node_xml += f"<property name='{property_name}' type='{signature}' access='read'/>"
        for method_name, method_info in self._methods.items():
            node_xml += f"<method name='{method_name}'>"
            for argument in method_info[0]:
                node_xml += f"<arg type='{argument}' direction='in'/>"
            for result in method_info[1]:
                node_xml += f"<arg type='{result}' direction='out'/>"
            node_xml += "</method>"
        for signal_name, signal_signature in self._signals.items():
            node_xml += f"<signal name='{signal_name}'>"
            for signature in signal_signature:
                node_xml += f"<arg type='{signature}'/>"
            node_xml += "</signal>"
        node_xml += "</interface></node>"

        node_info = Gio.DBusNodeInfo.new_for_xml(node_xml)

        regid = self._bus.register_object(
            self._path,
            node_info.interfaces[0],
            self._handle_method_call,
            self._get_property,
            None)

        if regid:
            self._regid = regid
        else:
            raise GLib.Error(f"Failed to register object with path: {self._path}")

    def unregister(self) -> None:
        if self._regid is not None:
            self._bus.unregister_object(self._regid)
            self._regid = None

    def _reregister(self) -> None:
        if self._regid:
            self.unregister()
            self.register()

    def _handle_method_call(self, _connection: Gio.DBusConnection, sender: str, _path: str, interface_name: str,
                            method_name: str, parameters: GLib.Variant, invocation: Gio.DBusMethodInvocation) -> None:
        try:
            try:
                _arguments, result_signatures, method, options = self._methods[method_name]
            except KeyError:
                logging.warning(f"Unhandled method: {method_name}")
                invocation.return_error_literal(Gio.dbus_error_quark(), Gio.DBusError.UNKNOWN_METHOD,
                                                f"No such method on interface: {interface_name}.{method_name}")

            def ok(*result: Any) -> None:
                invocation.return_value(self._prepare_arguments(result_signatures,
                                                                result[0] if len(result_signatures) > 1 else result))

            args = parameters.unpack()
            if "sender" in options:
                args += (sender,)
            if "async" in options:
                method(*(args + (ok, lambda exception: self._return_dbus_error(invocation, exception))))
            else:
                ok(method(*args))
        except Exception as e:
            self._return_dbus_error(invocation, e)

    def _get_property(self, _connection: Gio.DBusConnection, _sender: str, path: str, interface_name: str,
                      property_name: str) -> GLib.Variant:
        assert interface_name == self._interface_name and path == self._path
        return GLib.Variant(self._properties[property_name], getattr(self, property_name))

    @staticmethod
    def _return_dbus_error(invocation: Gio.DBusMethodInvocation, data: object) -> None:
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
    def _prepare_arguments(types: Tuple[str, ...], args: Collection[Any]) -> Optional[GLib.Variant]:
        return GLib.Variant(f"({''.join(types)})", args) if types else None

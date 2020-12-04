from typing import List, Callable, Optional, Any, Union, Dict

from gi.repository import Gio, GLib, GObject
from gi.types import GObjectMeta
from blueman.bluez.errors import parse_dbus_error, BluezDBusException
import logging

from blueman.bluemantyping import GSignals


class BaseMeta(GObjectMeta):
    def __call__(cls, *args: object, **kwargs: str) -> "Base":
        if not hasattr(cls, "__instances__"):
            cls.__instances__: Dict[str, "Base"] = {}

        path = kwargs.get('obj_path')
        if path is None:
            path = getattr(cls, "_obj_path")

        if path in cls.__instances__:
            return cls.__instances__[path]

        instance: "Base" = super().__call__(*args, **kwargs)
        cls.__instances__[path] = instance

        return instance


class Base(Gio.DBusProxy, metaclass=BaseMeta):
    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __name = 'org.bluez'
    __bus_type = Gio.BusType.SYSTEM

    __gsignals__: GSignals = {
        'property-changed': (GObject.SignalFlags.NO_HOOKS, None, (str, object, str))
    }
    __instances__: Dict[str, "Base"]

    _interface_name: str

    def __init__(self, *, obj_path: str):
        super().__init__(
            g_name=self.__name,
            g_interface_name=self._interface_name,
            g_object_path=obj_path,
            g_bus_type=self.__bus_type,
            # FIXME See issue 620
            g_flags=Gio.DBusProxyFlags.GET_INVALIDATED_PROPERTIES)

        self.init()
        self.__fallback = {'Icon': 'blueman', 'Class': 0, 'Appearance': 0}

        self.__variant_map = {str: 's', int: 'u', bool: 'b'}

    def do_g_properties_changed(self, changed_properties: GLib.Variant, _invalidated_properties: List[str]) -> None:
        changed = changed_properties.unpack()
        object_path = self.get_object_path()
        logging.debug(f"{object_path} {changed}")
        for key, value in changed.items():
            self.emit("property-changed", key, value, object_path)

    def _call(
        self,
        method: str,
        param: Optional[GLib.Variant] = None,
        reply_handler: Optional[Callable[..., None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        def callback(
            proxy: Base,
            result: Gio.AsyncResult,
            reply: Optional[Callable[..., None]],
            error: Optional[Callable[[BluezDBusException], None]],
        ) -> None:
            try:
                value = proxy.call_finish(result).unpack()
                if reply:
                    reply(*value)
            except GLib.Error as e:
                if error:
                    error(parse_dbus_error(e))
                else:
                    logging.error(f"Unhandled error for {self.get_interface_name()}.{method}", exc_info=True)

        self.call(method, param, Gio.DBusCallFlags.NONE, GLib.MAXINT, None,
                  callback, reply_handler, error_handler)

    def get(self, name: str) -> Any:
        try:
            prop = self.call_sync(
                'org.freedesktop.DBus.Properties.Get',
                GLib.Variant('(ss)', (self._interface_name, name)),
                Gio.DBusCallFlags.NONE,
                GLib.MAXINT,
                None)
            return prop.unpack()[0]
        except GLib.Error as e:
            property = self.get_cached_property(name)
            if property is not None:
                return property.unpack()
            elif name in self.__fallback:
                return self.__fallback[name]
            else:
                raise parse_dbus_error(e)

    def set(self, name: str, value: Union[str, int, bool]) -> None:
        v = GLib.Variant(self.__variant_map[type(value)], value)
        param = GLib.Variant('(ssv)', (self._interface_name, name, v))
        self.call('org.freedesktop.DBus.Properties.Set',
                  param,
                  Gio.DBusCallFlags.NONE,
                  GLib.MAXINT,
                  None)

    def get_properties(self) -> Dict[str, Any]:
        param = GLib.Variant('(s)', (self._interface_name,))
        res = self.call_sync('org.freedesktop.DBus.Properties.GetAll',
                             param,
                             Gio.DBusCallFlags.NONE,
                             GLib.MAXINT,
                             None)

        props: Dict[str, Any] = res.unpack()[0]
        for k, v in self.__fallback.items():
            if k in props:
                continue
            else:
                props[k] = v

        return props

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Union[str, int, bool]) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self.get_properties()

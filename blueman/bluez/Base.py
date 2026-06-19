from typing import Any
from collections.abc import Callable
from blueman.bluemantyping import GSignals, ObjectPath

from gi.repository import Gio, GLib, GObject
from gi.types import GObjectMeta
from blueman.bluez.errors import parse_dbus_error, BluezDBusException
import logging

DBUS_TIMEOUT = 10 * 1_000


class InstanceRegistry:
    """Caches one :class:`Base` instance per D-Bus object path.

    Object-identity caching used to live inline in :class:`BaseMeta`. Pulling
    it into a small, named collaborator keeps the metaclass focused on
    construction and makes the cache independently testable and replaceable.
    """

    def __init__(self) -> None:
        self._instances: dict[str, "Base"] = {}

    def get(self, path: str) -> "Base | None":
        return self._instances.get(path)

    def add(self, path: str, instance: "Base") -> None:
        self._instances[path] = instance

    def remove(self, path: str) -> None:
        self._instances.pop(path, None)

    def clear(self) -> None:
        self._instances.clear()


class BaseMeta(GObjectMeta):
    def __call__(cls, *args: object, **kwargs: str) -> "Base":
        registry: InstanceRegistry | None = cls.__dict__.get("_registry")
        if registry is None:
            registry = InstanceRegistry()
            cls._registry = registry

        path = kwargs.get('obj_path')
        if path is None:
            path = getattr(cls, "_obj_path")

        existing = registry.get(path)
        if existing is not None:
            return existing

        instance: "Base" = super().__call__(*args, **kwargs)
        registry.add(path, instance)

        return instance


class Base(GObject.Object, metaclass=BaseMeta):
    __name = 'org.bluez'
    __bus_type = Gio.BusType.SYSTEM
    __proxy: Gio.DBusProxy

    __gsignals__: GSignals = {
        'property-changed': (GObject.SignalFlags.NO_HOOKS, None, (str, object, str))
    }
    _registry: InstanceRegistry

    _interface_name: str

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    def __init__(self, *, obj_path: ObjectPath):
        super().__init__()

        self.__proxy = Gio.DBusProxy.new_for_bus_sync(
            self.__bus_type,
            Gio.DBusProxyFlags.NONE,
            None,
            self.__name,
            obj_path,
            self._interface_name,
            None
        )

        self.__proxy.connect("g-properties-changed", self._properties_changed)

        self.__fallback = {'Icon': 'blueman', 'Class': 0, 'Appearance': 0}

        self.__variant_map = {str: 's', int: 'u', bool: 'b'}

        # Properties whose last forced refresh failed and are being served from
        # cache. PropertiesChanged clears the flag once a live value arrives.
        self.__stale: set[str] = set()

    def _properties_changed(self, _proxy: Gio.DBusProxy, changed_properties: GLib.Variant,
                            invalidated_properties: list[str]) -> None:
        changed = changed_properties.unpack()
        object_path = self.get_object_path()
        logging.debug(f"{object_path} {changed} {invalidated_properties} {self}")

        for key in list(changed) + invalidated_properties:
            self.__stale.discard(key)
            self.emit("property-changed", key, changed.get(key, None), object_path)

    def is_stale(self, name: str) -> bool:
        """True if ``name`` is currently served from cache after a failed refresh."""
        return name in self.__stale

    def _call(
        self,
        method: str,
        param: GLib.Variant | None = None,
        reply_handler: Callable[..., None] | None = None,
        error_handler: Callable[[BluezDBusException], None] | None = None,
    ) -> None:
        def callback(
            proxy: Gio.DBusProxy,
            result: Gio.AsyncResult,
            reply: Callable[..., None] | None,
            error: Callable[[BluezDBusException], None] | None,
        ) -> None:
            try:
                value = proxy.call_finish(result).unpack()
                if reply:
                    reply(*value)
            except GLib.Error as e:
                if error:
                    error(parse_dbus_error(e))
                else:
                    logging.error(f"Unhandled error for {self.__proxy.get_interface_name()}.{method}", exc_info=True)

        self.__proxy.call(method, param, Gio.DBusCallFlags.NONE, DBUS_TIMEOUT, None,
                          callback, reply_handler, error_handler)

    def get(self, name: str, fresh: bool = False) -> Any:
        # Prefer the proxy's local property cache, which Gio keeps current from
        # PropertiesChanged signals, over a synchronous Properties.Get round-trip
        # on every read. Bluez devices expose the same properties repeatedly to
        # the UI; serving them from cache avoids a blocking D-Bus call each time.
        # Callers that need a guaranteed-live value pass fresh=True.
        if not fresh:
            cached = self.__proxy.get_cached_property(name)
            if cached is not None:
                return cached.unpack()

        try:
            prop = self.__proxy.call_sync(
                'org.freedesktop.DBus.Properties.Get',
                GLib.Variant('(ss)', (self._interface_name, name)),
                Gio.DBusCallFlags.NONE,
                DBUS_TIMEOUT,
                None)
            self.__stale.discard(name)
            return prop.unpack()[0]
        except GLib.Error as e:
            # The refresh failed: fall back to the last cached value if we have
            # one, but record that it is stale so callers can tell.
            cached = self.__proxy.get_cached_property(name)
            if cached is not None:
                logging.debug(f"{self._interface_name}.{name}: serving cached value after "
                              f"refresh error: {e.message}")
                self.__stale.add(name)
                return cached.unpack()
            if name in self.__fallback:
                return self.__fallback[name]
            raise parse_dbus_error(e)

    def set(self, name: str, value: str | int | bool) -> None:
        v = GLib.Variant(self.__variant_map[type(value)], value)
        param = GLib.Variant('(ssv)', (self._interface_name, name, v))
        self.__proxy.call('org.freedesktop.DBus.Properties.Set',
                          param,
                          Gio.DBusCallFlags.NONE,
                          DBUS_TIMEOUT,
                          None)

    def get_object_path(self) -> ObjectPath:
        return ObjectPath(self.__proxy.get_object_path())

    def get_properties(self) -> dict[str, Any]:
        param = GLib.Variant('(s)', (self._interface_name,))
        res = self.__proxy.call_sync('org.freedesktop.DBus.Properties.GetAll',
                                     param,
                                     Gio.DBusCallFlags.NONE,
                                     DBUS_TIMEOUT,
                                     None)

        props: dict[str, Any] = res.unpack()[0]
        for k, v in self.__fallback.items():
            if k in props:
                continue
            else:
                props[k] = v

        return props

    def destroy(self) -> None:
        registry = type(self).__dict__.get("_registry")
        if registry is not None:
            registry.remove(self.get_object_path())
        if self.__proxy:
            del self.__proxy

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: str | int | bool) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self.get_properties()

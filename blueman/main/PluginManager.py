from gettext import gettext as _
import logging
import traceback
import importlib
import pathlib
from types import ModuleType
from typing import TypeVar, Generic
from collections.abc import Iterable

from gi.repository import GObject, Gio

from blueman.Functions import bmexit, plugin_names
from blueman.gui.CommonUi import ErrorDialog
from blueman.plugins.BasePlugin import BasePlugin
from blueman.bluemantyping import GSignals
from blueman.plugins.errors import PluginException, PluginError, PluginDependencyError


class LoadException(Exception):
    pass


_T = TypeVar("_T", bound=BasePlugin)


class PluginDependencyResolver(Generic[_T]):
    """Owns the dependency/conflict graph and answers load-ordering queries.

    Pure graph queries only; performing side effects (loading, unloading,
    enabling) stays with the manager that owns the live plugin state.
    """

    def __init__(self, classes: dict[str, type[_T]], conflicts: dict[str, list[str]]) -> None:
        self.__classes = classes
        self.__conflicts = conflicts

    def required(self, cls: type[_T]) -> list[type[_T]]:
        """Dependency classes that must load before cls, in declaration order.

        Raises PluginDependencyError if a declared dependency is unregistered.
        """
        result = []
        for dep in cls.__depends__:
            if dep not in self.__classes:
                raise PluginDependencyError(f"Could not satisfy dependency {cls.__name__} -> {dep}")
            result.append(self.__classes[dep])
        return result

    def conflicts(self, cls: type[_T]) -> list[tuple[str, type[_T] | None]]:
        """Conflicting (name, registered class or None) pairs declared against cls."""
        return [(cfl, self.__classes.get(cfl)) for cfl in self.__conflicts[cls.__name__]]


class PluginManager(GObject.GObject, Generic[_T]):
    __gsignals__: GSignals = {
        'plugin-loaded': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_STRING,)),
        'plugin-unloaded': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_STRING,)),
    }

    def __init__(self, plugin_class: type[_T], module_path: ModuleType, parent: object) -> None:
        super().__init__()
        self.__deps: dict[str, list[str]] = {}
        self.__cfls: dict[str, list[str]] = {}
        self._plugins: dict[str, _T] = {}
        self.__classes: dict[str, type[_T]] = {}
        self.__loaded: list[str] = []
        # Per-manager unloadable flags; never mutate the shared class attribute.
        self.__unloadable: dict[str, bool] = {}
        self.__resolver: PluginDependencyResolver[_T] = PluginDependencyResolver(self.__classes, self.__cfls)
        self.parent = parent

        self.module_path = module_path
        self.plugin_class = plugin_class

    @property
    def config_list(self) -> list[str]:
        return []

    def get_classes(self) -> dict[str, type[_T]]:
        return self.__classes

    def get_loaded(self) -> list[str]:
        return self.__loaded

    def get_dependencies(self) -> dict[str, list[str]]:
        return self.__deps

    def get_conflicts(self) -> dict[str, list[str]]:
        return self.__cfls

    def load_plugin(self, name: str | None = None, user_action: bool = False) -> None:
        if name:
            try:
                self.__load_plugin(self.__classes[name])
            except LoadException as e:
                logging.warning(f"Not loading plugin {name}: {e}")
            except Exception:
                if user_action:
                    d = ErrorDialog(_("<b>An error has occurred while loading "
                                      "a plugin. Please notify the developers "
                                      "with the content of this message to our </b>\n"
                                      "<a href=\"http://github.com/blueman-project/blueman/issues\">website.</a>"),
                                    excp=traceback.format_exc())
                    d.run()
                    d.destroy()
                    raise

            return

        assert self.module_path.__file__ is not None
        path = pathlib.Path(self.module_path.__file__)
        plugins = plugin_names(path)

        logging.info(plugins)
        for plugin in plugins:
            try:
                importlib.import_module(self.module_path.__name__ + f".{plugin}")
            except ImportError:
                logging.error(f"Unable to load plugin module {plugin}", exc_info=True)
            except PluginException as err:
                logging.warning(f"Failed to start plugin {plugin}: {err}")

        for cls in self.plugin_class.__subclasses__():
            self.__classes[cls.__name__] = cls
            self.__unloadable.setdefault(cls.__name__, cls.__unloadable__)
            if cls.__name__ not in self.__deps:
                self.__deps[cls.__name__] = []

            if cls.__name__ not in self.__cfls:
                self.__cfls[cls.__name__] = []

            for c in cls.__depends__:
                if c not in self.__deps:
                    self.__deps[c] = []
                self.__deps[c].append(cls.__name__)

            for c in cls.__conflicts__:
                if c not in self.__cfls:
                    self.__cfls[c] = []
                self.__cfls[c].append(cls.__name__)
                if c not in self.__cfls[cls.__name__]:
                    self.__cfls[cls.__name__].append(c)

        cl = self.config_list
        for name, cls in self.__classes.items():
            for dep in self.__deps[name]:
                # plugins that are required by not unloadable plugins are not unloadable too
                if not self.is_unloadable(dep):
                    self.__unloadable[name] = False

            if (cls.__autoload__ or (cl and cls.__name__ in cl)) and \
                    not (self.is_unloadable(cls.__name__) and cl and "!" + cls.__name__ in cl):
                try:
                    self.__load_plugin(cls)
                except LoadException as e:
                    logging.warning(f"Not loading plugin {cls.__name__}: {e}")

    def disable_plugin(self, plugin: str) -> bool:
        return False

    def enable_plugin(self, plugin: str) -> bool:
        return True

    def __load_plugin(self, cls: type[_T]) -> None:
        if cls.__name__ in self.__loaded:
            return

        self.__load_dependencies(cls)
        if not self.__resolve_conflicts(cls):
            return
        self.__activate(cls)

    def __load_dependencies(self, cls: type[_T]) -> None:
        for dep_cls in self.__resolver.required(cls):
            if dep_cls.__name__ not in self.__loaded:
                try:
                    self.__load_plugin(dep_cls)
                except Exception as e:
                    logging.exception(e)
                    raise

    def __resolve_conflicts(self, cls: type[_T]) -> bool:
        """Return True if cls may load. Unloads a lower-priority conflict when it
        should yield; raises LoadException when cls itself must yield."""
        for cfl, cfl_cls in self.__resolver.conflicts(cls):
            if cfl_cls is not None:
                if cfl_cls.__priority__ > cls.__priority__ and not self.disable_plugin(cfl) \
                        and not self.enable_plugin(cls.__name__):
                    logging.warning(f"Not loading {cls.__name__} because its conflict has higher priority")
                    return False

            if cfl in self.__loaded:
                if cls.__priority__ > self.__classes[cfl].__priority__ and not self.enable_plugin(cfl):
                    self.unload_plugin(cfl)
                else:
                    raise LoadException(f"Not loading conflicting plugin {cls.__name__} due to lower priority")
        return True

    def __activate(self, cls: type[_T]) -> None:
        logging.info(f"loading {cls}")
        inst = cls(self.parent)
        try:
            inst._load()
        except Exception:
            logging.error(f"Failed to load {cls.__name__}", exc_info=True)
            if not self.is_unloadable(cls.__name__):
                bmexit()

            raise  # NOTE TO SELF: might cause bugs

        else:
            self._plugins[cls.__name__] = inst

            self.__loaded.append(cls.__name__)
            self.emit("plugin-loaded", cls.__name__)

    def __getattr__(self, key: str) -> object:
        try:
            return self._plugins[key]
        except KeyError:
            return self.__dict__[key]

    def is_unloadable(self, name: str) -> bool:
        if name in self.__unloadable:
            return self.__unloadable[name]
        return self.__classes[name].__unloadable__

    def unload_plugin(self, name: str) -> None:
        if self.is_unloadable(name):
            for d in self.__deps[name]:
                self.unload_plugin(d)

            if name in self.__loaded:
                logging.info(f"Unloading {name}")
                try:
                    inst = self._plugins[name]
                    inst._unload()
                except NotImplementedError:
                    logging.warning("Plugin cannot be unloaded")
                else:
                    self.__loaded.remove(name)
                    del self._plugins[name]
                    self.emit("plugin-unloaded", name)

        else:
            raise PluginError(f"Plugin {name} is not unloadable")

    def get_plugins(self) -> dict[str, _T]:
        return self._plugins

    def get_plugin(self, name: str) -> _T:
        """Return the loaded plugin instance by name.

        Explicit, type-checkable alternative to attribute access via __getattr__,
        which is opaque to IDEs and refactoring tools. Raises KeyError if the
        plugin is not loaded.
        """
        return self._plugins[name]

    _U = TypeVar("_U")

    def get_loaded_plugins(self, protocol: type[_U]) -> Iterable[_U]:
        for name in self.__loaded:
            plugin = self._plugins[name]
            if isinstance(plugin, protocol):
                yield plugin


class PersistentPluginManager(PluginManager[_T]):
    def __init__(self, plugin_class: type[_T], module_path: ModuleType, parent: object) -> None:
        super().__init__(plugin_class, module_path, parent)

        self.__config = Gio.Settings(schema_id="org.blueman.general")

        self.__config.connect("changed::plugin-list", self.on_property_changed)

    def disable_plugin(self, plugin: str) -> bool:
        plugins = self.__config["plugin-list"]
        return "!" + plugin in plugins

    def enable_plugin(self, plugin: str) -> bool:
        plugins = self.__config["plugin-list"]
        return plugin in plugins

    def set_config(self, plugin: str, state: bool) -> None:
        plugins = self.__config["plugin-list"]
        if plugin in plugins:
            plugins.remove(plugin)
        elif "!" + plugin in plugins:
            plugins.remove("!" + plugin)

        plugins.append(str("!" + plugin) if not state else str(plugin))
        self.__config["plugin-list"] = plugins

    @property
    def config_list(self) -> list[str]:
        lst: list[str] = self.__config["plugin-list"]
        return lst

    def on_property_changed(self, config: Gio.Settings, key: str) -> None:
        for item in config[key]:
            disable = item.startswith("!")
            if disable:
                item = item.lstrip("!")

            try:
                if item not in self.get_classes():
                    raise KeyError(item)
                if not self.is_unloadable(item) and disable:
                    logging.warning(f"warning: {item} is not unloadable")
                elif item in self.get_loaded() and disable:
                    self.unload_plugin(item)
                elif item not in self.get_loaded() and not disable:
                    try:
                        self.load_plugin(item, user_action=True)
                    except Exception as e:
                        logging.exception(e)
                        self.set_config(item, False)

            except KeyError:
                logging.warning(f"warning: Plugin {item} not found")
                continue

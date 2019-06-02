# coding=utf-8
import os
import builtins
import logging
import traceback
import importlib

from blueman.main.Config import Config
from blueman.gui.CommonUi import ErrorDialog

from gi.repository import GObject


class StopException(Exception):
    pass


class LoadException(Exception):
    pass


builtins.StopException = StopException


class PluginManager(GObject.GObject):
    __gsignals__ = {
        'plugin-loaded': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_STRING,)),
        'plugin-unloaded': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_STRING,)),
    }

    def __init__(self, plugin_class, module_path, parent):
        super().__init__()
        self.__plugins = {}
        self.__classes = {}
        self.__deps = {}
        self.__cfls = {}
        self.__loaded = []
        self.parent = parent

        self.module_path = module_path
        self.plugin_class = plugin_class

    @property
    def config_list(self):
        return []

    def get_classes(self):
        return self.__classes

    def get_loaded(self):
        return self.__loaded

    def get_dependencies(self):
        return self.__deps

    def get_conflicts(self):
        return self.__cfls

    def load_plugin(self, name=None, user_action=False):
        if name:
            try:
                self.__load_plugin(self.__classes[name])
            except LoadException:
                pass
            except Exception:
                if user_action:
                    d = ErrorDialog(_("<b>An error has occured while loading "
                                      "a plugin. Please notify the developers "
                                      "with the content of this message to our </b>\n"
                                      "<a href=\"http://github.com/blueman-project/blueman/issues\">website.</a>"),
                                    excp=traceback.format_exc())
                    d.run()
                    d.destroy()
                    raise

            return

        path = os.path.dirname(self.module_path.__file__)
        plugins = []
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".py") and not (f.endswith(".pyc") or f.endswith("_.py")):
                    plugins.append(f[0:-3])

        logging.info(plugins)
        for plugin in plugins:
            try:
                importlib.import_module(self.module_path.__name__ + ".%s" % plugin)
            except ImportError:
                logging.error("Unable to load plugin module %s" % plugin, exc_info=True)

        for cls in self.plugin_class.__subclasses__():
            self.__classes[cls.__name__] = cls
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

        c = self.config_list
        for name, cls in self.__classes.items():
            for dep in self.__deps[name]:
                # plugins that are required by not unloadable plugins are not unloadable too
                if not self.__classes[dep].__unloadable__:
                    cls.__unloadable__ = False

            if (cls.__autoload__ or (c and cls.__name__ in c)) and \
                    not (cls.__unloadable__ and c and "!" + cls.__name__ in c):
                self.__load_plugin(cls)

    def disable_plugin(self, plugin):
        return False

    def enable_plugin(self, plugin):
        return True

    def __load_plugin(self, cls):
        if cls.__name__ in self.__loaded:
            return

        for dep in cls.__depends__:
            if dep not in self.__loaded:
                if dep not in self.__classes:
                    raise Exception("Could not satisfy dependency %s -> %s" % (cls.__name__, dep))
                try:
                    self.__load_plugin(self.__classes[dep])
                except Exception as e:
                    logging.exception(e)
                    raise

        for cfl in self.__cfls[cls.__name__]:
            if cfl in self.__classes:
                if self.__classes[cfl].__priority__ > cls.__priority__ and not self.disable_plugin(cfl) \
                        and not self.enable_plugin(cls.__name__):
                    logging.warning("Not loading %s because its conflict has higher priority" % cls.__name__)
                    return

            if cfl in self.__loaded:
                if cls.__priority__ > self.__classes[cfl].__priority__ and not self.enable_plugin(cfl):
                    self.unload_plugin(cfl)
                else:
                    raise LoadException("Not loading conflicting plugin %s due to lower priority" % cls.__name__)

        logging.info("loading %s" % cls)
        inst = cls(self.parent)
        try:
            inst._load()
        except Exception:
            logging.error("Failed to load %s" % cls.__name__, exc_info=True)
            if not cls.__unloadable__:
                os._exit(1)

            raise  # NOTE TO SELF: might cause bugs

        else:
            self.__plugins[cls.__name__] = inst

            self.__loaded.append(cls.__name__)
            self.emit("plugin-loaded", cls.__name__)

    def __getattr__(self, key):
        try:
            return self.__plugins[key]
        except KeyError:
            return self.__dict__[key]

    def unload_plugin(self, name):
        if self.__classes[name].__unloadable__:
            for d in self.__deps[name]:
                self.unload_plugin(d)

            if name in self.__loaded:
                logging.info("Unloading %s" % name)
                try:
                    inst = self.__plugins[name]
                    inst._unload()
                except NotImplementedError:
                    logging.warning("Plugin cannot be unloaded")
                else:
                    self.__loaded.remove(name)
                    del self.__plugins[name]
                    self.emit("plugin-unloaded", name)

        else:
            raise Exception("Plugin %s is not unloadable" % name)

    def get_plugins(self):
        return self.__plugins

    # executes a function on all plugin instances
    def run(self, func, *args, **kwargs):
        rets = []
        for inst in self.__plugins.values():
            try:
                ret = getattr(inst, func)(*args, **kwargs)
                rets.append(ret)
            except Exception:
                logging.error("Function %s on %s failed" % (func, inst.__class__.__name__), exc_info=True)

        return rets

    # executes a function on all plugin instances, runs a callback after each plugin returns something
    def run_ex(self, func, callback, *args, **kwargs):
        for inst in self.__plugins.values():
            ret = getattr(inst, func)(*args, **kwargs)
            try:
                ret = callback(inst, ret)
            except StopException:
                return ret
            except Exception:
                logging.error("Function %s on %s failed" % (func, inst.__class__.__name__), exc_info=True)
                return

            if ret is not None:
                args = ret


class PersistentPluginManager(PluginManager):
    def __init__(self, *args):
        super().__init__(*args)

        self.__config = Config("org.blueman.general")

        self.__config.connect("changed::plugin-list", self.on_property_changed)

    def disable_plugin(self, plugin):
        plugins = self.__config["plugin-list"]
        return "!" + plugin in plugins

    def enable_plugin(self, plugin):
        plugins = self.__config["plugin-list"]
        return plugin in plugins

    def set_config(self, plugin, state):
        plugins = self.__config["plugin-list"]
        if plugin in plugins:
            plugins.remove(plugin)
        elif "!" + plugin in plugins:
            plugins.remove("!" + plugin)

        plugins.append(str("!" + plugin) if not state else str(plugin))
        self.__config["plugin-list"] = plugins

    @property
    def config_list(self):
        return self.__config["plugin-list"]

    def on_property_changed(self, config, key):
        for item in config[key]:
            disable = item.startswith("!")
            if disable:
                item = item.lstrip("!")

            try:
                cls = self.get_classes()[item]
                if not cls.__unloadable__ and disable:
                    logging.warning("warning: %s is not unloadable" % item)
                elif item in self.get_loaded() and disable:
                    self.unload_plugin(item)
                elif item not in self.get_loaded() and not disable:
                    try:
                        self.load_plugin(item, user_action=True)
                    except Exception as e:
                        logging.exception(e)
                        self.set_config(item, False)

            except KeyError:
                logging.warning("warning: Plugin %s not found" % item)
                continue

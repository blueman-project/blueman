from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject
import os
try: import __builtin__ as builtins
except ImportError: import builtins
import traceback

from blueman.Functions import *


class StopException(Exception):
    pass


class LoadException(Exception):
    pass


builtins.StopException = StopException


class PluginManager(GObject.GObject):
    __gsignals__ = {
    str('plugin-loaded'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_STRING,)),
    str('plugin-unloaded'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_STRING,)),
    }

    def __init__(self, plugin_class, module_path, user_data):
        GObject.GObject.__init__(self)
        self.__plugins = {}
        self.__classes = {}
        self.__deps = {}
        self.__cfls = {}
        self.__loaded = []
        self.user_data = user_data

        self.module_path = module_path
        self.plugin_class = plugin_class

    @property
    def config_list(self):
        return []

    def GetClasses(self):
        return self.__classes

    def GetLoaded(self):
        return self.__loaded

    def GetDependencies(self):
        return self.__deps

    def GetConflicts(self):
        return self.__cfls

    def Load(self, name=None, user_action=False):
        if name:
            try:
                self.__load_plugin(self.__classes[name])
            except LoadException as e:
                pass
            except Exception as e:
                if user_action:
                    d = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                          buttons=Gtk.ButtonsType.CLOSE)
                    d.set_markup(_("<b>An error has occured while loading "
                                   "a plugin. Please notify the developers "
                                   "with the content of this message.</b>"))
                    d.props.secondary_text = traceback.format_exc()
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

        dprint(plugins)
        for plugin in plugins:
            try:
                __import__(self.module_path.__name__ + ".%s" % plugin, None, None, [])
            except ImportError as e:
                dprint("Unable to load plugin module %s\n%s" % (plugin, e))

        for cls in self.plugin_class.__subclasses__():
            self.__classes[cls.__name__] = cls
            if not cls.__name__ in self.__deps:
                self.__deps[cls.__name__] = []

            if not cls.__name__ in self.__cfls:
                self.__cfls[cls.__name__] = []

            for c in cls.__depends__:
                if not c in self.__deps:
                    self.__deps[c] = []
                self.__deps[c].append(cls.__name__)

            for c in cls.__conflicts__:
                if not c in self.__cfls:
                    self.__cfls[c] = []
                self.__cfls[c].append(cls.__name__)
                if c not in self.__cfls[cls.__name__]:
                    self.__cfls[cls.__name__].append(c)

        c = self.config_list
        for name, cls in self.__classes.items():
            for dep in self.__deps[name]:
                #plugins that are required by not unloadable plugins are not unloadable too
                if not self.__classes[dep].__unloadable__:
                    cls.__unloadable__ = False

            if (cls.__autoload__ or (c and cls.__name__ in c)) and not (cls.__unloadable__ and c and "!" + cls.__name__ in c):
                try:
                    self.__load_plugin(cls)
                except:
                    pass

    def Disabled(self, plugin):
        return False

    def Enabled(self, plugin):
        return True

    def __load_plugin(self, cls):
        if cls.__name__ in self.__loaded:
            return

        for dep in cls.__depends__:
            if not dep in self.__loaded:
                if not dep in self.__classes:
                    raise Exception("Could not satisfy dependency %s -> %s" % (cls.__name__, dep))
                try:
                    self.__load_plugin(self.__classes[dep])
                except Exception as e:
                    dprint(e)
                    raise

        for cfl in self.__cfls[cls.__name__]:
            if cfl in self.__classes:
                if self.__classes[cfl].__priority__ > cls.__priority__ and not self.Disabled(cfl) and not self.Enabled(
                        cls.__name__):
                    dprint("Not loading %s because it's conflict has higher priority" % cls.__name__)
                    return

            if cfl in self.__loaded:
                if cls.__priority__ > self.__classes[cfl].__priority__ and not self.Enabled(cfl):
                    self.Unload(cfl)
                else:
                    raise LoadException("Not loading conflicting plugin %s due to lower priority" % cls.__name__)

        dprint("loading", cls)
        inst = cls(self.user_data)
        try:
            inst._load(self.user_data)
        except Exception as e:
            dprint("Failed to load %s\n%s" % (cls.__name__, e))
            if not cls.__unloadable__:
                os._exit(1)

            raise #NOTE TO SELF: might cause bugs

        else:
            self.__plugins[cls.__name__] = inst

            self.__loaded.append(cls.__name__)
            self.emit("plugin-loaded", cls.__name__)

    def __getattr__(self, key):
        try:
            return self.__plugins[key]
        except:
            return self.__dict__[key]

    def Unload(self, name):
        if self.__classes[name].__unloadable__:
            for d in self.__deps[name]:
                self.Unload(d)

            if name in self.__loaded:
                dprint("Unloading %s" % name)
                try:
                    inst = self.__plugins[name]
                    inst._unload()
                except NotImplementedError:
                    print("Plugin cannot be unloaded")
                else:
                    self.__loaded.remove(name)
                    del self.__plugins[name]
                    self.emit("plugin-unloaded", name)

        else:
            raise Exception("Plugin %s is not unloadable" % name)


    def get_plugins(self):
        return self.__plugins

    #executes a function on all plugin instances
    def Run(self, function, *args, **kwargs):
        rets = []
        for inst in self.__plugins.values():
            try:
                ret = getattr(inst, function)(*args, **kwargs)
                rets.append(ret)
            except Exception as e:
                dprint("Function", function, "on", inst.__class__.__name__, "Failed")
                traceback.print_exc()

        return rets

    #executes a function on all plugin instances, runs a callback after each plugin returns something
    def RunEx(self, function, callback, *args, **kwargs):
        for inst in self.__plugins.values():
            ret = getattr(inst, function)(*args, **kwargs)
            try:
                ret = callback(inst, ret)
            except StopException:
                return ret
            except Exception as e:
                dprint("Function", function, "on", inst.__class__.__name__, "Failed")
                traceback.print_exc()
                return

            if ret != None:
                args = ret


try:
    from blueman.main.Config import Config
except:
    pass


class PersistentPluginManager(PluginManager):
    def __init__(self, *args):
        super(PersistentPluginManager, self).__init__(*args)

        self.__config = Config("org.blueman.general")

        self.__config.connect("changed::plugin-list", self.on_property_changed)

    def Disabled(self, plugin):
        plugins = self.__config["plugin-list"]
        return "!" + plugin in plugins

    def Enabled(self, plugin):
        plugins = self.__config["plugin-list"]
        return plugin in plugins

    def SetConfig(self, plugin, state):
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
                cls = self.GetClasses()[item]
                if not cls.__unloadable__ and disable:
                    print(YELLOW("warning:"), item, "is not unloadable")
                elif item in self.GetLoaded() and disable:
                    self.Unload(item)
                elif item not in self.GetLoaded() and not disable:
                    try:
                        self.Load(item, user_action=True)
                    except:
                        self.SetConfig(item, False)

            except KeyError:
                print(YELLOW("warning:"), "Plugin %s not found" % item)
                continue

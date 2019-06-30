# coding=utf-8
import logging
import weakref
from typing import List, TYPE_CHECKING, Type, Dict, Tuple, Any

from blueman.main.Config import Config


class MethodAlreadyExists(Exception):
    pass


if TYPE_CHECKING:
    from mypy_extensions import TypedDict

    class OptionBase(TypedDict):
        type: Type
        default: Any

    class Option(OptionBase, total=False):
        name: str
        desc: str
        range: Tuple[int, int]

    class GSettings(TypedDict):
        schema: str
        path: None


class BasePlugin(object):
    __depends__: List[str] = []
    __conflicts__: List[str] = []
    __priority__ = 0

    __description__: str
    __author__: str

    __unloadable__ = True
    __autoload__ = True

    __instance__ = None

    __gsettings__: "GSettings"

    __options__: Dict[str, "Option"] = {}

    def __init__(self, parent):
        self.parent = parent

        self.__methods = []

        if self.__options__:
            self.__config = Config(
                self.__class__.__gsettings__.get("schema"),
                self.__class__.__gsettings__.get("path")
            )

        weakref.finalize(self, self._on_plugin_delete)

    def _on_plugin_delete(self):
        self.on_delete()
        logging.debug("Deleting plugin instance %s" % self)

    @classmethod
    def is_configurable(cls):
        res = map(lambda x: (len(x) > 2), cls.__options__.values())
        return True in res

    @classmethod
    def add_method(cls, func):
        """Add a new method that can be used by other plugins to listen for changes, query state, etc"""
        func.__self__.__methods.append((cls, func.__name__))

        if func.__name__ in cls.__dict__:
            raise MethodAlreadyExists
        else:
            setattr(cls, func.__name__, func)

    def _unload(self):
        self.on_unload()

        for cls, met in self.__methods:
            delattr(cls, met)

        self.__class__.__instance__ = None

    def _load(self):
        try:
            self.on_load()
            # self.on_manager_state_changed(applet.Manager != None)
            self.__class__.__instance__ = self
        except Exception as e:
            # AppletPlugin.instances.remove(self)
            self.__class__.__instance__ = None
            logging.exception(e)
            raise

    # virtual methods
    def on_load(self):
        """Do what is neccessary for the plugin to work like add watches or create ui elements"""
        pass

    def on_unload(self):
        """Tear down any watches and ui elements created in on_load"""
        raise NotImplementedError

    def on_delete(self):
        """Do cleanup that needs to happen when plugin is deleted"""
        pass

    def get_option(self, key):
        if key not in self.__class__.__options__:
            raise KeyError("No such option")
        return self.__config[key]

    def set_option(self, key, value):
        if key not in self.__class__.__options__:
            raise KeyError("No such option")
        opt = self.__class__.__options__[key]

        if type(value) == opt["type"]:
            self.__config[key] = value
            self.option_changed(key, value)
        else:
            raise TypeError("Wrong type, must be %s" % repr(opt["type"]))

    def option_changed(self, key, value):
        pass

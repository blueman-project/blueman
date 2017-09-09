# coding=utf-8
import logging
from blueman.main.Config import Config


class MethodAlreadyExists(Exception):
    pass


class BasePlugin(object):
    __depends__ = []
    __conflicts__ = []
    __priority__ = 0

    __description__ = None
    __author__ = None

    __unloadable__ = True
    __autoload__ = True

    __instance__ = None

    __gsettings__ = None

    __options__ = {}

    def __init__(self, parent):
        self.__parent__ = parent

        self.__methods = []

        if self.__options__:
            self.__config = Config(
                self.__class__.__gsettings__.get("schema"),
                self.__class__.__gsettings__.get("path")
            )

    def __del__(self):
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

    def _load(self, parent):
        try:
            self.on_load(parent)
            # self.on_manager_state_changed(applet.Manager != None)
            self.__class__.__instance__ = self
        except Exception as e:
            # AppletPlugin.instances.remove(self)
            self.__class__.__instance__ = None
            logging.exception(e)
            raise

    # virtual methods
    def on_load(self, applet):
        """Do what is neccessary for the plugin to work like add watches or create ui elements"""
        pass

    def on_unload(self):
        """Tear down any watches and ui elements created in on_load"""
        raise NotImplementedError

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

# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import logging


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

    def __init__(self, parent):
        self.__parent__ = parent

        self.__methods = []

    def __del__(self):
        logging.debug("Deleting plugin instance %s" % self)

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

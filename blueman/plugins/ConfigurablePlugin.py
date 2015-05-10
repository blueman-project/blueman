from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.Config import Config
from blueman.plugins.BasePlugin import BasePlugin


class ConfigurablePlugin(BasePlugin):
    __gsettings__ = None

    def on_unload(self):
        pass

    __options__ = {}

    @classmethod
    def is_configurable(cls):
        res = map(lambda x: (len(x) > 2), cls.__options__.values())
        return True in res

    def get_option(self, key):
        if key not in self.__class__.__options__:
            raise KeyError("No such option")
        return self.__config[key]

    def set_option(self, key, value):
        if key not in self.__class__.__options__:
            raise KeyError("No such option")
        opt = self.__class__.__options__[key]

        # Workaround the unicode_literals in python2.
        is_string = hasattr(value, "format") and hasattr(value, "encode")

        if type(value) == opt["type"] or is_string:
            self.__config[key] = value
            self.option_changed(key, value)
        else:
            raise TypeError("Wrong type, must be %s" % repr(opt["type"]))

    def option_changed(self, key, value):
        pass

    def __init__(self, parent):
        super(ConfigurablePlugin, self).__init__(parent)

        if self.__options__ != {}:
            self.__config = Config(
                self.__class__.__gsettings__.get("schema"),
                self.__class__.__gsettings__.get("path")
            )

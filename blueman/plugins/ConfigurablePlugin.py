from blueman.main.Config import Config
from blueman.plugins.BasePlugin import BasePlugin


class ConfigurablePlugin(BasePlugin):
    def on_unload(self):
        pass

    __options__ = {}

    @classmethod
    def is_configurable(cls):
        res = map(lambda x: (len(x) > 2), cls.__options__.values())
        return True in res

    def get_option(self, name):
        if name not in self.__class__.__options__:
            raise KeyError("No such option")
        return getattr(self.__config.props, name)

    def set_option(self, name, value):
        if name not in self.__class__.__options__:
            raise KeyError("No such option")
        opt = self.__class__.__options__[name]
        if type(value) == opt["type"]:
            setattr(self.__config.props, name, value)
            self.option_changed(name, value)
        else:
            raise TypeError("Wrong type, must be %s" % repr(opt["type"]))

    def option_changed(self, name, value):
        pass

    def __init__(self, parent):
        super(ConfigurablePlugin, self).__init__(parent)

        if self.__options__ != {}:
            self.__config = Config("plugins/" + self.__class__.__name__)

            for k, v in self.__options__.items():
                if getattr(self.__config.props, k) is None:
                    setattr(self.__config.props, k, v["default"])

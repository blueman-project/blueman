from gi.repository import GObject
import weakref


class ConfigPlugin(GObject.GObject):
    __plugin__ = None
    __priority__ = None

    __gsignals__ = {
        # @param: self key value
        'property-changed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    class props:
        def __init__(self, Config):
            self.__dict__["Config"] = Config

        def __setattr__(self, key, value):
            self.__dict__["Config"]().set(key, value)

        def __getattr__(self, key):
            return self.__dict__["Config"]().get(key)

    def __init__(self, section=""):
        GObject.GObject.__init__(self)

        self.props = ConfigPlugin.props(weakref.ref(self))

        self.on_load(section)

    # virtual functions
    def on_load(self, section):
        pass

    def get(self, key):
        pass

    def set(self, key, val):
        pass

    def list_dirs(self):
        pass

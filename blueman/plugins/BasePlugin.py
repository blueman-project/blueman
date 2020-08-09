import logging
import weakref
from gettext import gettext as _
from typing import List, TYPE_CHECKING, Dict, Tuple, Any, TypeVar, Type, Optional

from blueman.main.Config import Config


if TYPE_CHECKING:
    from typing_extensions import TypedDict

    # type is actually Type[T] and default is T but this is not supported https://github.com/python/mypy/issues/3863
    class OptionBase(TypedDict):
        type: type
        default: Any

    class Option(OptionBase, total=False):
        name: str
        desc: str
        range: Tuple[int, int]

    class GSettings(TypedDict):
        schema: str
        path: None
else:
    Option = dict


class BasePlugin:
    __depends__: List[str] = []
    __conflicts__: List[str] = []
    __priority__ = 0

    __description__: str = _("Unspecified")
    __author__: str = _("Unspecified")

    __unloadable__ = True
    __autoload__ = True

    __instance__ = None

    __gsettings__: "GSettings"

    __options__: Dict[str, "Option"] = {}

    def __init__(self, *_args: object) -> None:
        if self.__options__:
            self.__config = Config(
                self.__class__.__gsettings__["schema"],
                self.__class__.__gsettings__["path"]
            )

        weakref.finalize(self, self._on_plugin_delete)

    _T = TypeVar("_T", bound="BasePlugin")

    @classmethod
    def get_instance(cls: Type[_T]) -> Optional[_T]:
        return cls.__instance__

    def _on_plugin_delete(self) -> None:
        self.on_delete()
        logging.debug(f"Deleting plugin instance {self}")

    @classmethod
    def is_configurable(cls) -> bool:
        res = map(lambda x: (len(x) > 2), cls.__options__.values())
        return True in res

    def _unload(self) -> None:
        self.on_unload()

        self.__class__.__instance__ = None

    def _load(self) -> None:
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
    def on_load(self) -> None:
        """Do what is neccessary for the plugin to work like add watches or create ui elements"""
        pass

    def on_unload(self) -> None:
        """Tear down any watches and ui elements created in on_load"""
        raise NotImplementedError

    def on_delete(self) -> None:
        """Do cleanup that needs to happen when plugin is deleted"""
        pass

    def get_option(self, key: str) -> Any:
        if key not in self.__class__.__options__:
            raise KeyError("No such option")
        return self.__config[key]

    def set_option(self, key: str, value: Any) -> None:
        if key not in self.__class__.__options__:
            raise KeyError("No such option")
        opt = self.__class__.__options__[key]

        if type(value) == opt["type"]:
            self.__config[key] = value
            self.option_changed(key, value)
        else:
            raise TypeError(f"Wrong type, must be {repr(opt['type'])}")

    def option_changed(self, key: str, value: Any) -> None:
        pass

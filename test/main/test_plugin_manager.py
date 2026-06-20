from unittest import TestCase
from unittest.mock import MagicMock

from blueman.main.PluginManager import PluginManager, LoadException


class _Plugin:
    __depends__: list = []
    __conflicts__: list = []
    __priority__ = 0
    __autoload__ = True
    __unloadable__ = True

    def __init__(self, parent: object) -> None:
        self.parent = parent
        self.loaded = False

    def _load(self) -> None:
        self.loaded = True

    def _unload(self) -> None:
        pass


def _plugin_class(name: str, **attrs: object) -> type:
    return type(name, (_Plugin,), dict(attrs))


def _manager() -> PluginManager:
    return PluginManager(_Plugin, MagicMock(), MagicMock())


def _register(manager: PluginManager, cls: type, deps: list | None = None, cfls: list | None = None) -> None:
    manager.get_classes()[cls.__name__] = cls
    manager.get_dependencies()[cls.__name__] = deps or []
    manager.get_conflicts()[cls.__name__] = cfls or []


class TestLoadExceptionLogged(TestCase):
    def test_conflict_load_exception_is_logged(self) -> None:
        manager = _manager()
        high = _plugin_class("High", __priority__=10)
        low = _plugin_class("Low", __priority__=0)
        _register(manager, high)
        _register(manager, low, cfls=["High"])
        manager.get_loaded().append("High")
        manager.get_plugins()["High"] = high(manager.parent)

        with self.assertLogs(level="WARNING") as cm:
            manager.load_plugin("Low")

        self.assertTrue(any("Low" in line for line in cm.output))
        self.assertNotIn("Low", manager.get_loaded())

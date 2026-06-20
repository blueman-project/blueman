from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.main.PluginManager import PluginManager, LoadException
from blueman.plugins.errors import PluginError, PluginDependencyError


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


class TestErrorTypes(TestCase):
    def test_missing_dependency_raises_dependency_error(self) -> None:
        manager = _manager()
        dependent = _plugin_class("Dependent", __depends__=["Absent"])
        _register(manager, dependent)
        with self.assertRaises(PluginDependencyError):
            manager._PluginManager__load_plugin(dependent)

    def test_unload_non_unloadable_raises_plugin_error(self) -> None:
        manager = _manager()
        fixed = _plugin_class("Fixed", __unloadable__=False)
        _register(manager, fixed)
        with self.assertRaises(PluginError):
            manager.unload_plugin("Fixed")

    def test_dependency_error_is_a_plugin_error(self) -> None:
        self.assertTrue(issubclass(PluginDependencyError, PluginError))


class TestGetPlugin(TestCase):
    def test_returns_loaded_instance(self) -> None:
        manager = _manager()
        cls = _plugin_class("Widget")
        instance = cls(manager.parent)
        manager.get_plugins()["Widget"] = instance
        self.assertIs(manager.get_plugin("Widget"), instance)

    def test_matches_getattr_access(self) -> None:
        manager = _manager()
        cls = _plugin_class("Widget")
        instance = cls(manager.parent)
        manager.get_plugins()["Widget"] = instance
        self.assertIs(manager.get_plugin("Widget"), manager.Widget)

    def test_unknown_plugin_raises_key_error(self) -> None:
        manager = _manager()
        with self.assertRaises(KeyError):
            manager.get_plugin("Nope")


class TestPerInstanceUnloadable(TestCase):
    def test_is_unloadable_defaults_to_class_attribute(self) -> None:
        manager = _manager()
        fixed = _plugin_class("Fixed", __unloadable__=False)
        flex = _plugin_class("Flex", __unloadable__=True)
        _register(manager, fixed)
        _register(manager, flex)
        self.assertFalse(manager.is_unloadable("Fixed"))
        self.assertTrue(manager.is_unloadable("Flex"))

    def test_per_instance_flag_does_not_mutate_class(self) -> None:
        manager = _manager()
        cls = _plugin_class("Flex", __unloadable__=True)
        _register(manager, cls)
        manager._PluginManager__unloadable["Flex"] = False
        self.assertFalse(manager.is_unloadable("Flex"))
        self.assertTrue(cls.__unloadable__)  # the shared class attribute is untouched

    def test_dependency_rule_is_per_manager_not_global(self) -> None:
        # A (non-unloadable) depends on B -> B becomes non-unloadable, but only
        # in this manager's flags; the B class attribute must stay True so a
        # second manager (or the class itself) is unaffected.
        base = type("UniqueBase", (_Plugin,), {})
        b = type("B", (base,), {"__autoload__": False})
        a = type("A", (base,), {"__unloadable__": False, "__depends__": ["B"], "__autoload__": False})
        self.assertIsNotNone(a)  # keep A alive so __subclasses__() sees the dependent

        module_path = MagicMock()
        module_path.__file__ = "/x"
        module_path.__name__ = "m"
        manager: PluginManager = PluginManager(base, module_path, MagicMock())
        with patch("blueman.main.PluginManager.plugin_names", return_value=[]):
            manager.load_plugin()

        self.assertFalse(manager.is_unloadable("B"))  # demoted by non-unloadable dependent A
        self.assertTrue(b.__unloadable__)             # class attribute never mutated

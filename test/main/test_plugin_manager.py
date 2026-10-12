from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.main.PluginManager import (
    PluginManager,
    PluginDependencyResolver,
    LoadStrategy,
    DefaultLoadStrategy,
)
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


class TestDependencyResolver(TestCase):
    def test_required_returns_dependency_classes_in_order(self) -> None:
        a = _plugin_class("A")
        b = _plugin_class("B")
        dependent = _plugin_class("Dependent", __depends__=["A", "B"])
        resolver: PluginDependencyResolver = PluginDependencyResolver({"A": a, "B": b, "Dependent": dependent}, {})
        self.assertEqual(resolver.required(dependent), [a, b])

    def test_required_raises_on_unregistered_dependency(self) -> None:
        dependent = _plugin_class("Dependent", __depends__=["Gone"])
        resolver: PluginDependencyResolver = PluginDependencyResolver({"Dependent": dependent}, {})
        with self.assertRaises(PluginDependencyError):
            resolver.required(dependent)

    def test_conflicts_returns_registered_and_unregistered_pairs(self) -> None:
        a = _plugin_class("A")
        resolver: PluginDependencyResolver = PluginDependencyResolver({"A": a}, {"A": ["A", "Ghost"]})
        self.assertEqual(resolver.conflicts(a), [("A", a), ("Ghost", None)])


class TestLoadOrderingAndConflicts(TestCase):
    def test_dependency_is_loaded_before_dependent(self) -> None:
        manager = _manager()
        dep = _plugin_class("Dep")
        main_cls = _plugin_class("Main", __depends__=["Dep"])
        _register(manager, dep)
        _register(manager, main_cls)
        manager.load_plugin("Main")
        self.assertEqual(manager.get_loaded(), ["Dep", "Main"])

    def test_higher_priority_plugin_unloads_lower_priority_conflict(self) -> None:
        manager = _manager()
        manager.enable_plugin = lambda plugin: False  # type: ignore[method-assign]
        low = _plugin_class("Low", __priority__=0)
        high = _plugin_class("High", __priority__=10)
        _register(manager, low)
        _register(manager, high, cfls=["Low"])
        manager.load_plugin("Low")
        manager.load_plugin("High")
        self.assertIn("High", manager.get_loaded())
        self.assertNotIn("Low", manager.get_loaded())

    def test_already_loaded_plugin_is_not_reloaded(self) -> None:
        manager = _manager()
        cls = _plugin_class("Once")
        _register(manager, cls)
        manager.load_plugin("Once")
        first = manager.get_plugin("Once")
        manager.load_plugin("Once")
        self.assertIs(manager.get_plugin("Once"), first)


class TestActivateFailure(TestCase):
    def test_unloadable_plugin_load_failure_reraises(self) -> None:
        manager = _manager()
        cls = _plugin_class("Boom", __unloadable__=True)
        cls._load = lambda self: (_ for _ in ()).throw(RuntimeError("nope"))  # type: ignore[assignment]
        _register(manager, cls)
        with self.assertRaises(RuntimeError):
            manager._PluginManager__load_plugin(cls)
        self.assertNotIn("Boom", manager.get_loaded())

    @patch("blueman.main.PluginManager.bmexit")
    def test_non_unloadable_plugin_load_failure_calls_bmexit(self, bmexit_mock: MagicMock) -> None:
        manager = _manager()
        cls = _plugin_class("Critical", __unloadable__=False)
        cls._load = lambda self: (_ for _ in ()).throw(RuntimeError("nope"))  # type: ignore[assignment]
        _register(manager, cls)
        with self.assertRaises(RuntimeError):
            manager._PluginManager__load_plugin(cls)
        bmexit_mock.assert_called_once()


class TestLoadStrategySeam(TestCase):
    def test_custom_strategy_overrides_loading(self) -> None:
        calls = []

        class RecordingStrategy(LoadStrategy):
            def load(self, manager: PluginManager, cls: type) -> None:
                calls.append(cls.__name__)

        manager: PluginManager = PluginManager(_Plugin, MagicMock(), MagicMock(),
                                               load_strategy=RecordingStrategy())
        cls = _plugin_class("P")
        _register(manager, cls)
        manager.load_plugin("P")
        self.assertEqual(calls, ["P"])
        self.assertNotIn("P", manager.get_loaded())  # custom strategy chose not to activate

    def test_default_strategy_activates_plugin(self) -> None:
        manager = _manager()
        cls = _plugin_class("P")
        _register(manager, cls)
        manager.load_plugin("P")
        self.assertIn("P", manager.get_loaded())

    def test_default_load_strategy_is_used_by_default(self) -> None:
        manager = _manager()
        self.assertIsInstance(manager._PluginManager__strategy, DefaultLoadStrategy)

    def test_base_strategy_load_is_abstract(self) -> None:
        with self.assertRaises(NotImplementedError):
            LoadStrategy().load(_manager(), _plugin_class("P"))

    def test_is_loaded_hook_reflects_state(self) -> None:
        manager = _manager()
        cls = _plugin_class("P")
        _register(manager, cls)
        self.assertFalse(manager.is_loaded("P"))
        manager.load_plugin("P")
        self.assertTrue(manager.is_loaded("P"))


class TestUnloadPlugin(TestCase):
    def test_unload_removes_loaded_plugin(self) -> None:
        manager = _manager()
        cls = _plugin_class("P")
        _register(manager, cls)
        manager.load_plugin("P")
        manager.unload_plugin("P")
        self.assertNotIn("P", manager.get_loaded())
        self.assertNotIn("P", manager.get_plugins())

    def test_unload_recurses_into_dependents(self) -> None:
        manager = _manager()
        dep = _plugin_class("Dep")
        main_cls = _plugin_class("Main", __depends__=["Dep"])
        _register(manager, dep, deps=["Main"])  # __deps[Dep] holds Dep's dependents
        _register(manager, main_cls)
        manager.load_plugin("Main")
        manager.unload_plugin("Dep")  # Dep's dependent Main is unloaded first
        self.assertNotIn("Main", manager.get_loaded())
        self.assertNotIn("Dep", manager.get_loaded())

    def test_unload_warns_when_plugin_refuses(self) -> None:
        manager = _manager()
        cls = _plugin_class("Stubborn")
        cls._unload = lambda self: (_ for _ in ()).throw(NotImplementedError())  # type: ignore[assignment]
        _register(manager, cls)
        manager.load_plugin("Stubborn")
        with self.assertLogs(level="WARNING"):
            manager.unload_plugin("Stubborn")
        self.assertIn("Stubborn", manager.get_loaded())  # still loaded


@patch("blueman.main.PluginManager.importlib")
@patch("blueman.main.PluginManager.plugin_names", return_value=["modx"])
class TestDiscoveryImportFailures(TestCase):
    def _manager_over_empty_base(self) -> PluginManager:
        base = type("EmptyBase", (_Plugin,), {})
        module_path = MagicMock()
        module_path.__file__ = "/x"
        module_path.__name__ = "m"
        return PluginManager(base, module_path, MagicMock())

    def test_import_error_is_logged(self, _names: MagicMock, importlib_mock: MagicMock) -> None:
        importlib_mock.import_module.side_effect = ImportError("boom")
        manager = self._manager_over_empty_base()
        with self.assertLogs(level="ERROR"):
            manager.load_plugin()

    def test_plugin_exception_is_logged(self, _names: MagicMock, importlib_mock: MagicMock) -> None:
        importlib_mock.import_module.side_effect = PluginError("nope")
        manager = self._manager_over_empty_base()
        with self.assertLogs(level="WARNING"):
            manager.load_plugin()


@patch("blueman.main.PluginManager.Gio")
class TestPersistentPluginManager(TestCase):
    def _ppm(self, gio_mock: MagicMock, plugin_list: list) -> tuple:
        from blueman.main.PluginManager import PersistentPluginManager
        store = {"plugin-list": list(plugin_list)}
        config = MagicMock()
        config.__getitem__.side_effect = lambda key: store[key]
        config.__setitem__.side_effect = lambda key, value: store.__setitem__(key, value)
        gio_mock.Settings.return_value = config
        ppm = PersistentPluginManager(_Plugin, MagicMock(), MagicMock())
        return ppm, store

    def test_disable_and_enable_queries(self, gio_mock: MagicMock) -> None:
        ppm, _store = self._ppm(gio_mock, ["Enabled", "!Disabled"])
        self.assertTrue(ppm.enable_plugin("Enabled"))
        self.assertFalse(ppm.enable_plugin("Disabled"))
        self.assertTrue(ppm.disable_plugin("Disabled"))
        self.assertFalse(ppm.disable_plugin("Enabled"))

    def test_config_list_returns_setting(self, gio_mock: MagicMock) -> None:
        ppm, _store = self._ppm(gio_mock, ["A", "!B"])
        self.assertEqual(ppm.config_list, ["A", "!B"])

    def test_set_config_enable_and_disable(self, gio_mock: MagicMock) -> None:
        ppm, store = self._ppm(gio_mock, [])
        ppm.set_config("Foo", True)
        self.assertIn("Foo", store["plugin-list"])
        ppm.set_config("Foo", False)
        self.assertIn("!Foo", store["plugin-list"])
        self.assertNotIn("Foo", store["plugin-list"])

    def test_on_property_changed_unknown_plugin_logs(self, gio_mock: MagicMock) -> None:
        ppm, _store = self._ppm(gio_mock, ["Ghost"])
        with self.assertLogs(level="WARNING") as cm:
            ppm.on_property_changed(ppm._PersistentPluginManager__config, "plugin-list")
        self.assertTrue(any("not found" in line for line in cm.output))

    def test_on_property_changed_disables_loaded_plugin(self, gio_mock: MagicMock) -> None:
        ppm, _store = self._ppm(gio_mock, ["!Widget"])
        cls = _plugin_class("Widget")
        _register(ppm, cls)
        ppm.load_plugin("Widget")
        ppm.on_property_changed(ppm._PersistentPluginManager__config, "plugin-list")
        self.assertNotIn("Widget", ppm.get_loaded())

    def test_on_property_changed_warns_for_non_unloadable(self, gio_mock: MagicMock) -> None:
        ppm, _store = self._ppm(gio_mock, ["!Fixed"])
        cls = _plugin_class("Fixed", __unloadable__=False)
        _register(ppm, cls)
        with self.assertLogs(level="WARNING") as cm:
            ppm.on_property_changed(ppm._PersistentPluginManager__config, "plugin-list")
        self.assertTrue(any("not unloadable" in line for line in cm.output))


class TestDependencyChainFuzz(TestCase):
    def test_deep_chains_load_in_dependency_order(self) -> None:
        for depth in range(1, 12):
            manager = _manager()
            names = [f"P{i}" for i in range(depth)]
            for index, name in enumerate(names):
                deps = [names[index + 1]] if index + 1 < depth else []
                _register(manager, _plugin_class(name, __depends__=deps))
            manager.load_plugin(names[0])
            self.assertEqual(manager.get_loaded(), list(reversed(names)),
                             f"depth={depth} loaded out of order")

    def test_conflict_priority_matrix_is_deterministic(self) -> None:
        for winner_priority, loser_priority in [(1, 0), (10, 2), (5, 4), (100, 99)]:
            manager = _manager()
            manager.enable_plugin = lambda plugin: False  # type: ignore[method-assign]
            loser = _plugin_class("Loser", __priority__=loser_priority)
            winner = _plugin_class("Winner", __priority__=winner_priority)
            _register(manager, loser)
            _register(manager, winner, cfls=["Loser"])
            manager.load_plugin("Loser")
            manager.load_plugin("Winner")
            self.assertIn("Winner", manager.get_loaded())
            self.assertNotIn("Loser", manager.get_loaded())


class TestDependencyCycles(TestCase):
    def test_direct_cycle_raises_dependency_error(self) -> None:
        manager = _manager()
        a = _plugin_class("A", __depends__=["B"])
        b = _plugin_class("B", __depends__=["A"])
        _register(manager, a)
        _register(manager, b)
        with self.assertRaises(PluginDependencyError):
            manager._PluginManager__load_plugin(a)
        self.assertEqual(manager.get_loaded(), [])

    def test_self_cycle_raises_dependency_error(self) -> None:
        manager = _manager()
        a = _plugin_class("A", __depends__=["A"])
        _register(manager, a)
        with self.assertRaises(PluginDependencyError):
            manager._PluginManager__load_plugin(a)

    def test_loading_set_is_cleared_after_cycle(self) -> None:
        manager = _manager()
        a = _plugin_class("A", __depends__=["B"])
        b = _plugin_class("B", __depends__=["A"])
        _register(manager, a)
        _register(manager, b)
        with self.assertRaises(PluginDependencyError):
            manager._PluginManager__load_plugin(a)
        self.assertEqual(manager._PluginManager__loading, set())


class TestDiamondDependencies(TestCase):
    def test_shared_dependency_loaded_once_in_order(self) -> None:
        manager = _manager()
        for cls in (
            _plugin_class("A"),
            _plugin_class("B", __depends__=["A"]),
            _plugin_class("C", __depends__=["A"]),
            _plugin_class("D", __depends__=["B", "C"]),
        ):
            _register(manager, cls)
        manager.load_plugin("D")
        order = manager.get_loaded()
        self.assertEqual(order.count("A"), 1)
        self.assertEqual(set(order), {"A", "B", "C", "D"})
        self.assertLess(order.index("A"), order.index("B"))
        self.assertLess(order.index("C"), order.index("D"))


class TestLifecycleSignals(TestCase):
    def test_plugin_loaded_signal_is_emitted(self) -> None:
        manager = _manager()
        _register(manager, _plugin_class("P"))
        seen: list = []
        manager.connect("plugin-loaded", lambda mgr, name: seen.append(name))
        manager.load_plugin("P")
        self.assertEqual(seen, ["P"])

    def test_plugin_unloaded_signal_is_emitted(self) -> None:
        manager = _manager()
        _register(manager, _plugin_class("P"))
        manager.load_plugin("P")
        seen: list = []
        manager.connect("plugin-unloaded", lambda mgr, name: seen.append(name))
        manager.unload_plugin("P")
        self.assertEqual(seen, ["P"])

    def test_load_unload_reload_yields_fresh_instance(self) -> None:
        manager = _manager()
        _register(manager, _plugin_class("P"))
        manager.load_plugin("P")
        first = manager.get_plugin("P")
        manager.unload_plugin("P")
        self.assertNotIn("P", manager.get_loaded())
        manager.load_plugin("P")
        self.assertIn("P", manager.get_loaded())
        self.assertIsNot(manager.get_plugin("P"), first)


class _Marker:
    pass


class TestGetLoadedPluginsAndGetattr(TestCase):
    def test_get_loaded_plugins_filters_by_protocol(self) -> None:
        manager = _manager()
        plain = _plugin_class("Plain")
        marked = type("Marked", (_Plugin, _Marker), {})
        _register(manager, plain)
        _register(manager, marked)
        manager.load_plugin("Plain")
        manager.load_plugin("Marked")
        result = list(manager.get_loaded_plugins(_Marker))
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], _Marker)

    def test_getattr_missing_attribute_raises_key_error(self) -> None:
        manager = _manager()
        with self.assertRaises(KeyError):
            manager.totally_missing_attribute


class TestConflictHigherPrioritySkip(TestCase):
    def test_existing_higher_priority_conflict_blocks_load(self) -> None:
        manager = _manager()
        manager.disable_plugin = lambda plugin: False  # type: ignore[method-assign]
        manager.enable_plugin = lambda plugin: False  # type: ignore[method-assign]
        high = _plugin_class("High", __priority__=10)
        low = _plugin_class("Low", __priority__=0)
        _register(manager, high)
        _register(manager, low, cfls=["High"])
        with self.assertLogs(level="WARNING") as cm:
            manager.load_plugin("Low")
        self.assertTrue(any("higher priority" in line for line in cm.output))
        self.assertNotIn("Low", manager.get_loaded())


class TestUserActionErrorDialog(TestCase):
    @patch("blueman.main.PluginManager.ErrorDialog")
    def test_user_action_failure_shows_dialog_and_reraises(self, dialog_mock: MagicMock) -> None:
        manager = _manager()
        cls = _plugin_class("Boom")
        cls._load = lambda self: (_ for _ in ()).throw(RuntimeError("x"))  # type: ignore[assignment]
        _register(manager, cls)
        with self.assertRaises(RuntimeError):
            manager.load_plugin("Boom", user_action=True)
        dialog_mock.assert_called_once()
        dialog_mock.return_value.run.assert_called_once()
        dialog_mock.return_value.destroy.assert_called_once()


class TestFullDiscovery(TestCase):
    def test_discovery_builds_graph_and_autoloads(self) -> None:
        base = type("DiscBase", (_Plugin,), {})
        dep = type("DepP", (base,), {"__autoload__": False})
        main = type("MainP", (base,), {"__depends__": ["DepP"], "__conflicts__": ["Ghost"]})
        self.assertIsNotNone(dep)
        self.assertIsNotNone(main)
        module_path = MagicMock()
        module_path.__file__ = "/x"
        module_path.__name__ = "m"
        manager: PluginManager = PluginManager(base, module_path, MagicMock())
        with patch("blueman.main.PluginManager.plugin_names", return_value=[]):
            manager.load_plugin()
        self.assertIn("DepP", manager.get_dependencies())
        self.assertIn("Ghost", manager.get_conflicts())
        self.assertIn("MainP", manager.get_loaded())
        self.assertIn("DepP", manager.get_loaded())


@patch("blueman.main.PluginManager.Gio")
class TestPersistentConfigPaths(TestCase):
    def _ppm(self, gio_mock: MagicMock, plugin_list: list) -> tuple:
        from blueman.main.PluginManager import PersistentPluginManager
        store = {"plugin-list": list(plugin_list)}
        config = MagicMock()
        config.__getitem__.side_effect = lambda key: store[key]
        config.__setitem__.side_effect = lambda key, value: store.__setitem__(key, value)
        gio_mock.Settings.return_value = config
        ppm = PersistentPluginManager(_Plugin, MagicMock(), MagicMock())
        return ppm, store

    def test_set_config_reenable_removes_disabled_marker(self, gio_mock: MagicMock) -> None:
        ppm, store = self._ppm(gio_mock, ["!Foo"])
        ppm.set_config("Foo", True)
        self.assertIn("Foo", store["plugin-list"])
        self.assertNotIn("!Foo", store["plugin-list"])

    def test_on_property_changed_loads_enabled_plugin(self, gio_mock: MagicMock) -> None:
        ppm, _store = self._ppm(gio_mock, ["Widget"])
        _register(ppm, _plugin_class("Widget"))
        ppm.on_property_changed(ppm._PersistentPluginManager__config, "plugin-list")
        self.assertIn("Widget", ppm.get_loaded())

    @patch("blueman.main.PluginManager.ErrorDialog")
    def test_on_property_changed_load_failure_resets_config(self, _dialog: MagicMock, gio_mock: MagicMock) -> None:
        ppm, store = self._ppm(gio_mock, ["Bad"])
        cls = _plugin_class("Bad")
        cls._load = lambda self: (_ for _ in ()).throw(RuntimeError("x"))  # type: ignore[assignment]
        _register(ppm, cls)
        ppm.on_property_changed(ppm._PersistentPluginManager__config, "plugin-list")
        self.assertIn("!Bad", store["plugin-list"])
        self.assertNotIn("Bad", ppm.get_loaded())


class TestFullDiscoveryEdgeCases(TestCase):
    def test_dangling_dependency_and_autoload_conflict(self) -> None:
        base = type("EdgeBase", (_Plugin,), {})
        alpha = type("Alpha", (base,), {"__conflicts__": ["Beta"], "__priority__": 0})
        beta = type("Beta", (base,), {"__priority__": 0})
        gamma = type("Gamma", (base,), {"__depends__": ["Phantom"], "__autoload__": False})
        for cls in (alpha, beta, gamma):
            self.assertIsNotNone(cls)
        module_path = MagicMock()
        module_path.__file__ = "/x"
        module_path.__name__ = "m"
        manager: PluginManager = PluginManager(base, module_path, MagicMock())
        with patch("blueman.main.PluginManager.plugin_names", return_value=[]), \
                self.assertLogs(level="WARNING"):
            manager.load_plugin()
        # Dangling dependency name is registered in the graph but never loaded.
        self.assertIn("Phantom", manager.get_dependencies())
        self.assertNotIn("Phantom", manager.get_loaded())
        # Equal-priority conflict: the first autoloads, the second is skipped.
        loaded_conflicts = [n for n in manager.get_loaded() if n in ("Alpha", "Beta")]
        self.assertEqual(len(loaded_conflicts), 1)

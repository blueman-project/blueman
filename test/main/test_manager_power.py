import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from gi.repository import GLib

from blueman.main.Manager import Blueman


def fake_manager(plugins: list[str], powered: bool) -> SimpleNamespace:
    failure = GLib.Error.new_literal(GLib.quark_from_string("test"), "No such interface", 19)
    return SimpleNamespace(
        Applet=Mock(QueryPlugins=Mock(return_value=plugins)),
        PowerManager=Mock(
            get_bluetooth_status=Mock(side_effect=failure),
            set_bluetooth_status=Mock(side_effect=failure),
        ),
        List=SimpleNamespace(Adapter={"Powered": powered}),
    )


class TestManagerPowerFallback(unittest.TestCase):
    def test_status_falls_back_to_adapter_when_applet_interface_is_missing(self) -> None:
        manager = fake_manager(["PowerManager"], powered=True)
        self.assertTrue(Blueman._get_bluetooth_status(manager))

    def test_status_uses_adapter_without_power_manager_plugin(self) -> None:
        manager = fake_manager([], powered=True)
        self.assertTrue(Blueman._get_bluetooth_status(manager))
        manager.PowerManager.get_bluetooth_status.assert_not_called()

    def test_set_status_powers_adapter_when_applet_interface_is_missing(self) -> None:
        manager = fake_manager(["PowerManager"], powered=True)
        Blueman._set_bluetooth_status(manager, False)
        self.assertFalse(manager.List.Adapter["Powered"])


if __name__ == "__main__":
    unittest.main()

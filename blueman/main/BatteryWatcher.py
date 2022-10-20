import weakref
from typing import Callable

from blueman.bluez.Battery import Battery, AnyBattery
from blueman.bluez.Manager import Manager


class BatteryWatcher:
    def __init__(self, callback: Callable[[str, int], None]) -> None:
        super().__init__()
        manager = Manager()
        weakref.finalize(
            self,
            manager.disconnect_signal,
            manager.connect_signal(
                "battery-created",
                lambda _manager, obj_path: callback(obj_path, Battery(obj_path=obj_path)["Percentage"])
            )
        )

        any_battery = AnyBattery()
        weakref.finalize(
            self,
            any_battery.disconnect_signal,
            any_battery.connect_signal(
                "property-changed",
                lambda _any_battery, key, value, path: callback(path, value) if key == "Percentage" else None
            )
        )

from typing import Iterable, Optional

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk


class Animation:
    def __init__(self, icon: Gtk.Image, icons: Iterable[str], rate: int = 1) -> None:
        self.icon_names = list(icons)
        self.timer: Optional[int] = None
        self.current = 0
        self.icon = icon
        self.rate = int(1000 / rate)

    def status(self) -> bool:
        if self.timer:
            return True
        else:
            return False

    def set_rate(self, rate: float) -> None:
        if not self.rate == int(1000 / rate):
            self.rate = int(1000 / rate)
            self.stop()
            self.start()

    def start(self) -> None:
        self.timer = GLib.timeout_add(self.rate, self._animation)

    def stop(self) -> None:
        if self.timer:
            GLib.source_remove(self.timer)
            self.icon.props.icon_name = self.icon_names[0]
            self.timer = None

    def _animation(self) -> bool:
        self.current += 1
        if self.current > (len(self.icon_names) - 1):
            self.current = 0
        self.icon.props.icon_name = self.icon_names[self.current]

        return True

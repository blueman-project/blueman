from typing import TYPE_CHECKING, Optional

from _blueman import device_info
from gi.repository import GLib
from gi.repository import Gtk

from blueman.gui.Animation import Animation
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList
from blueman.main.SpeedCalc import SpeedCalc
from blueman.Functions import adapter_path_to_name
from blueman.Functions import format_bytes

import gettext

_ = gettext.gettext

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerStats:
    hbox: Gtk.Box

    def __init__(self, blueman: "Blueman") -> None:

        blueman.List.connect("adapter-changed", self.on_adapter_changed)

        assert blueman.List.Adapter is not None
        self.hci = adapter_path_to_name(blueman.List.Adapter.get_object_path())

        self.time = None

        self.up_speed = SpeedCalc()
        self.down_speed = SpeedCalc()

        self.im_upload = Gtk.Image(icon_name="blueman-up-inactive", pixel_size=16,
                                   halign=Gtk.Align.END, valign=Gtk.Align.CENTER,
                                   tooltip_text=_("Data activity indication"))
        self.im_download = Gtk.Image(icon_name="blueman-down-inactive", pixel_size=16,
                                     halign=Gtk.Align.END, valign=Gtk.Align.CENTER,
                                     tooltip_text=_("Data activity indication"))
        self.down_rate = Gtk.Label(halign=Gtk.Align.END, valign=Gtk.Align.CENTER,
                                   tooltip_text=_("Total data received and rate of transmission"))
        self.down_rate.show()

        self.up_rate = Gtk.Label(halign=Gtk.Align.END, valign=Gtk.Align.CENTER,
                                 tooltip_text=_("Total data sent and rate of transmission"))
        self.up_rate.show()

        self.uparrow = Gtk.Image(icon_name="go-up", pixel_size=16, halign=Gtk.Align.END, valign=Gtk.Align.CENTER,
                                 tooltip_text=_("Total data sent and rate of transmission"))
        self.downarrow = Gtk.Image(icon_name="go-down", pixel_size=16, halign=Gtk.Align.END, valign=Gtk.Align.CENTER,
                                   tooltip_text=_("Total data received and rate of transmission"))

        self.hbox = hbox = blueman.builder.get_widget("status_activity", Gtk.Box)

        hbox.pack_start(self.uparrow, False, False, 0)
        hbox.pack_start(self.up_rate, False, False, 0)

        hbox.pack_start(self.downarrow, False, False, 0)
        hbox.pack_start(self.down_rate, False, False, 0)

        hbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)

        hbox.pack_start(self.im_upload, False, False, 0)
        hbox.pack_start(self.im_download, False, False, 0)
        hbox.show_all()
        self.on_adapter_changed(blueman.List, blueman.List.get_adapter_path())

        self.up_blinker = Animation(self.im_upload, ["blueman-up-inactive", "blueman-up-active"])
        self.down_blinker = Animation(self.im_download, ["blueman-down-inactive", "blueman-down-active"])

        self.start_update()

    def on_adapter_changed(self, _lst: ManagerDeviceList, adapter_path: Optional[str]) -> None:
        self.hci = adapter_path_to_name(adapter_path)
        if self.hci is None:
            self.hbox.props.sensitive = False
        else:
            self.hbox.props.sensitive = True

        self.up_speed.reset()
        self.down_speed.reset()

    def set_blinker_by_speed(self, blinker: Animation, speed: float) -> None:

        if speed > 0 and not blinker.status():
            blinker.start()

        if speed > 40 * 1024 and blinker.status():
            blinker.set_rate(10)
        elif speed > (30 * 1024) and blinker.status():
            blinker.set_rate(8)
        elif speed > (20 * 1024) and blinker.status():
            blinker.set_rate(6)
        elif speed > (10 * 1024) and blinker.status():
            blinker.set_rate(4)
        elif speed > 1024 and blinker.status():
            blinker.set_rate(2)
        elif speed == 0 and blinker.status():
            blinker.stop()
        else:
            blinker.set_rate(1)

    def _update(self) -> bool:
        if self.hci is not None:
            devinfo = device_info(self.hci)
            _tx = devinfo["stat"]["byte_tx"]
            _rx = devinfo["stat"]["byte_rx"]

            tx, s_tx = format_bytes(_tx)
            rx, s_rx = format_bytes(_rx)

            _u_speed = self.up_speed.calc(_tx)
            _d_speed = self.down_speed.calc(_rx)

            self.set_blinker_by_speed(self.up_blinker, _u_speed)
            self.set_blinker_by_speed(self.down_blinker, _d_speed)

            u_speed, s_u_speed = format_bytes(_u_speed)
            d_speed, s_d_speed = format_bytes(_d_speed)

            self.set_data(tx, s_tx, rx, s_rx, u_speed, s_u_speed, d_speed, s_d_speed)

        return True

    def start_update(self) -> None:
        self._update()
        self.timer = GLib.timeout_add(1000, self._update)

    def stop_update(self) -> None:
        if self.timer:
            GLib.source_remove(self.timer)

    def set_data(self, uploaded: float, u_name: str, downloaded: float, d_name: str, u_speed: float, us_name: str,
                 d_speed: float, ds_name: str) -> None:
        self.down_rate.set_markup(
            f'<span size="small">{downloaded:.2f} {d_name} <i>{d_speed:5.2f} {ds_name}/s</i></span>')
        self.up_rate.set_markup(
            f'<span size="small">{uploaded:.2f} {u_name} <i>{u_speed:5.2f} {us_name}/s</i></span>')

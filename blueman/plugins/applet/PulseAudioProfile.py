import logging
from gettext import gettext as _
from html import escape
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Callable

from blueman.main.PulseAudioUtils import EventType, PulseAudioUtils
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.Sdp import (AUDIO_SINK_SVCLASS_ID, AUDIO_SOURCE_SVCLASS_ID,
                         ServiceUUID)

if TYPE_CHECKING:
    from blueman.bluez.Device import Device
    from blueman.main.PulseAudioUtils import CardInfo, CardProfileInfo
    from blueman.plugins.applet.Menu import MenuItem, SubmenuItemDict


class AudioProfiles(AppletPlugin):
    __depends__ = ["Menu"]
    __description__ = _("Adds audio profile selector to the status icon menu")
    __author__ = "Abhijeet Viswa"

    def on_load(self) -> None:
        self._devices: Dict[str, "CardInfo"] = {}
        self._device_menus: Dict[str, "MenuItem"] = {}

        self._menu = self.parent.Plugins.Menu

        pa = PulseAudioUtils()
        pa.connect("event", self.on_pa_event)
        pa.connect("connected", self.on_pa_ready)

    def generate_menu(self) -> None:
        devices = self.parent.Manager.get_devices()
        for device in devices:
            if device['Connected']:
                self.request_device_profile_menu(device)

    def request_device_profile_menu(self, device: "Device") -> None:
        audio_source = False
        for uuid in device['UUIDs']:
            if ServiceUUID(uuid).short_uuid in (AUDIO_SOURCE_SVCLASS_ID, AUDIO_SINK_SVCLASS_ID):
                audio_source = True
                break

        if device['Connected'] and audio_source:
            pa = PulseAudioUtils()
            if not pa.connected:
                return

            if not device['Address'] in self._devices:
                self.query_pa(device)
            else:
                self.add_device_profile_menu(device)

    def add_device_profile_menu(self, device: "Device") -> None:
        def _activate_profile_wrapper(device: "Device", profile: "CardProfileInfo") -> Callable[[], None]:
            def _wrapper() -> None:
                self.on_activate_profile(device, profile)
            return _wrapper

        def _generate_profiles_menu(info: "CardInfo") -> List["SubmenuItemDict"]:
            items: List["SubmenuItemDict"] = []
            if not info:
                return items
            for profile in info["profiles"]:
                profile_name = escape(profile["description"])
                profile_icon = "bluetooth-symbolic"
                if profile["name"] == info["active_profile"]:
                    profile_name = f"<b>{profile_name}</b>"
                    profile_icon = "dialog-ok"
                items.append({
                    "text": profile_name,
                    "markup": True,
                    "icon_name": profile_icon,
                    "sensitive": True,
                    "callback": _activate_profile_wrapper(device, profile),
                    "tooltip": "",
                })
            return items

        info = self._devices[device['Address']]
        idx = max((item.priority[1] for item in self._device_menus.values()), default=-1) + 1
        menu = self._menu.add(self, (42, idx), _("Audio Profiles for %s") % device.display_name,
                              icon_name="audio-card-symbolic",
                              submenu_function=lambda: _generate_profiles_menu(info))
        self._device_menus[device['Address']] = menu

    def query_pa(self, device: "Device") -> None:
        def list_cb(cards: Mapping[str, "CardInfo"]) -> None:
            for c in cards.values():
                if c["proplist"]["device.string"] == device['Address']:
                    self._devices[device['Address']] = c
                    self.add_device_profile_menu(device)
                    return

        pa = PulseAudioUtils()
        pa.list_cards(list_cb)

    def on_activate_profile(self, device: "Device", profile: "CardProfileInfo") -> None:
        pa = PulseAudioUtils()

        c = self._devices[device['Address']]

        def on_result(res: int) -> None:
            if not res:
                logging.error(f"Failed to change profile to {profile['name']}")

        pa.set_card_profile(c["index"], profile["name"], on_result)

    def on_pa_event(self, utils: PulseAudioUtils, event: int, idx: int) -> None:
        logging.debug(f"{event} {idx}")

        def get_card_cb(card: "CardInfo") -> None:
            drivers = ("module-bluetooth-device.c",
                       "module-bluez4-device.c",
                       "module-bluez5-device.c")

            if card["driver"] in drivers:
                self._devices[card["proplist"]["device.string"]] = card
                self.clear_menu()
                self.generate_menu()

        if event & EventType.FACILITY_MASK == EventType.CARD:
            logging.info("card")
            if event & EventType.TYPE_MASK == EventType.CHANGE:
                logging.info("change")
                utils.get_card(idx, get_card_cb)
            elif event & EventType.TYPE_MASK == EventType.REMOVE:
                logging.info("remove")
            else:
                logging.info("add")
                utils.get_card(idx, get_card_cb)

    def on_pa_ready(self, _utils: PulseAudioUtils) -> None:
        logging.info("PulseAudio Ready")
        self.generate_menu()

    def on_adapter_added(self, path: str) -> None:
        self.clear_menu()
        self.generate_menu()

    def on_adapter_removed(self, path: str) -> None:
        self.clear_menu()
        self.generate_menu()

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Connected":
            self.clear_menu()
            self.generate_menu()

    def on_manager_state_changed(self, state: bool) -> None:
        self.clear_menu()

    def on_unload(self) -> None:
        self.clear_menu()

    def clear_menu(self) -> None:
        self._device_menus = {}
        self._menu.unregister(self)

from gettext import gettext as _
import logging
from typing import Dict, List, TYPE_CHECKING, Mapping, Sequence

from blueman.bluez.Device import Device
from blueman.plugins.ManagerPlugin import ManagerPlugin
from blueman.main.PulseAudioUtils import PulseAudioUtils, EventType
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu, MenuItemsProvider, DeviceMenuItem
from blueman.gui.MessageArea import MessageArea
from blueman.Functions import create_menuitem
from blueman.Sdp import AUDIO_SOURCE_SVCLASS_ID, AUDIO_SINK_SVCLASS_ID, ServiceUUID

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


if TYPE_CHECKING:
    from blueman.main.PulseAudioUtils import CardInfo  # noqa: F401


class PulseAudioProfile(ManagerPlugin, MenuItemsProvider):
    def on_load(self) -> None:
        self.devices: Dict[str, "CardInfo"] = {}

        self.deferred: List[Device] = []

        pa = PulseAudioUtils()
        pa.connect("event", self.on_pa_event)
        pa.connect("connected", self.on_pa_ready)

    def on_pa_ready(self, _utils: PulseAudioUtils) -> None:
        logging.info("connected")
        for dev in self.deferred:
            self.regenerate_with_device(dev['Address'])

        self.deferred = []

    # updates all menu instances with the following device address
    def regenerate_with_device(self, device_addr: str) -> None:
        for inst in ManagerDeviceMenu.__instances__:
            if inst.SelectedDevice['Address'] == device_addr and not inst.is_popup:
                inst.generate()

    def on_pa_event(self, utils: PulseAudioUtils, event: int, idx: int) -> None:
        logging.debug(f"{event} {idx}")

        def get_card_cb(card: "CardInfo") -> None:
            drivers = ("module-bluetooth-device.c",
                       "module-bluez4-device.c",
                       "module-bluez5-device.c")

            if card["driver"] in drivers:
                self.devices[card["proplist"]["device.string"]] = card
                self.regenerate_with_device(card["proplist"]["device.string"])

        if event & EventType.CARD:
            logging.info("card")
            if event & EventType.CHANGE:
                logging.info("change")
                utils.get_card(idx, get_card_cb)
            elif event & EventType.REMOVE:
                logging.info("remove")
            else:
                logging.info("add")
                utils.get_card(idx, get_card_cb)

    def query_pa(self, device: Device, item: Gtk.MenuItem) -> None:
        def list_cb(cards: Mapping[str, "CardInfo"]) -> None:
            for c in cards.values():
                if c["proplist"]["device.string"] == device['Address']:
                    self.devices[device['Address']] = c
                    self.generate_menu(device, item)
                    return

        pa = PulseAudioUtils()
        pa.list_cards(list_cb)

    def on_selection_changed(self, item: Gtk.CheckMenuItem, device: Device, profile: str) -> None:
        if item.get_active():
            pa = PulseAudioUtils()

            c = self.devices[device['Address']]

            def on_result(res: int) -> None:
                if not res:
                    MessageArea.show_message(_("Failed to change profile to %s" % profile))

            pa.set_card_profile(c["index"], profile, on_result)

    def generate_menu(self, device: Device, item: Gtk.MenuItem) -> None:
        info = self.devices[device['Address']]
        group: Sequence[Gtk.RadioMenuItem] = []

        sub = Gtk.Menu()

        if info:
            for profile in info["profiles"]:
                i = Gtk.RadioMenuItem.new_with_label(group, profile["description"])
                group = i.get_group()

                if profile["name"] == info["active_profile"]:
                    i.set_active(True)

                i.connect("toggled", self.on_selection_changed,
                          device, profile["name"])

                sub.append(i)
                i.show()

            item.set_submenu(sub)
            item.show()

    def on_request_menu_items(self, manager_menu: ManagerDeviceMenu, device: Device) -> List[DeviceMenuItem]:
        audio_source = False
        for uuid in device['UUIDs']:
            if ServiceUUID(uuid).short_uuid in (AUDIO_SOURCE_SVCLASS_ID, AUDIO_SINK_SVCLASS_ID):
                audio_source = True
                break

        if device['Connected'] and audio_source:

            pa = PulseAudioUtils()
            if not pa.connected:
                self.deferred.append(device)
                return []

            item = create_menuitem(_("Audio Profile"), "audio-card")
            item.props.tooltip_text = _("Select audio profile for PulseAudio")

            if not device['Address'] in self.devices:
                self.query_pa(device, item)
            else:
                self.generate_menu(device, item)

        else:
            return []

        return [DeviceMenuItem(item, DeviceMenuItem.Group.ACTIONS, 300)]

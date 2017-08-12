# coding=utf-8
import logging

from blueman.plugins.ManagerPlugin import ManagerPlugin
from blueman.main.PulseAudioUtils import PulseAudioUtils, EventType
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.gui.MessageArea import MessageArea
from blueman.Functions import create_menuitem
from blueman.Sdp import AUDIO_SOURCE_SVCLASS_ID, AUDIO_SINK_SVCLASS_ID, ServiceUUID

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class PulseAudioProfile(ManagerPlugin):
    def on_load(self):
        self.devices = {}
        self.item = None

        self.deferred = []

        pa = PulseAudioUtils()
        pa.connect("event", self.on_pa_event)
        pa.connect("connected", self.on_pa_ready)

    def on_pa_ready(self, utils):
        logging.info("connected")
        for dev in self.deferred:
            self.regenerate_with_device(dev['Address'])

        self.deferred = []

    # updates all menu instances with the following device address
    def regenerate_with_device(self, device_addr):
        for inst in ManagerDeviceMenu.__instances__:
            if inst.SelectedDevice['Address'] == device_addr and not inst.is_popup:
                inst.generate()

    def on_pa_event(self, utils, event, idx):
        logging.debug("%s %s" % (event, idx))

        def get_card_cb(card):
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

    def query_pa(self, device):
        def list_cb(cards):
            for c in cards.values():
                if c["proplist"]["device.string"] == device['Address']:
                    self.devices[device['Address']] = c
                    self.generate_menu(device)
                    return

        pa = PulseAudioUtils()
        pa.list_cards(list_cb)

    def on_selection_changed(self, item, device, profile):
        if item.get_active():
            pa = PulseAudioUtils()

            c = self.devices[device['Address']]

            def on_result(res):
                if not res:
                    MessageArea.show_message(_("Failed to change profile to %s" % profile))

            pa.set_card_profile(c["index"], profile, on_result)

    def generate_menu(self, device):
        info = self.devices[device['Address']]
        group = []

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

            self.item.set_submenu(sub)
            self.item.show()

    def on_request_menu_items(self, manager_menu, device):
        audio_source = False
        for uuid in device['UUIDs']:
            if ServiceUUID(uuid).short_uuid in (AUDIO_SOURCE_SVCLASS_ID, AUDIO_SINK_SVCLASS_ID):
                audio_source = True
                break

        if device['Connected'] and audio_source:

            pa = PulseAudioUtils()
            if not pa.connected:
                self.deferred.append(device)
                return

            self.item = create_menuitem(_("Audio Profile"), "audio-card")
            self.item.props.tooltip_text = _("Select audio profile for PulseAudio")

            if not device['Address'] in self.devices:
                self.query_pa(device)
            else:
                self.generate_menu(device)

        else:
            return

        return [(self.item, 300)]

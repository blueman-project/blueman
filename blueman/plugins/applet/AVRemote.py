# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.Constants import *
from blueman.Sdp import uuid128_to_uuid16, AV_REMOTE_TARGET_SVCLASS_ID
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.AVRemote import AVRemote
from gi.repository import GLib
import blueman.bluez as Bluez

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib
import gettext
import os
import time
from locale import bind_textdomain_codeset
import cgi


class PlayerWindow(Gtk.Window):
    running = False

    def __init__(self):
        if not PlayerWindow.running:
            PlayerWindow.running = True
        else:
            return

        super(PlayerWindow, self).__init__(title="MediaPlayer")

        builder = Gtk.Builder()
        builder.add_from_file(UI_PATH + "/media-player.ui")
        builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")

        self.add(builder.get_object("media_player"))

        self._control_buttons = {}
        self._control_buttons['play'] = builder.get_object("media_play")
        self._control_buttons['pause'] = builder.get_object("media_pause")
        self._control_buttons['stop'] = builder.get_object("media_stop")
        self._control_buttons['next'] = builder.get_object("media_next")
        self._control_buttons['prev'] = builder.get_object("media_previous")

        self._control_buttons['play'].connect("clicked", self._on_media_button_clicked, "play")
        self._control_buttons['pause'].connect("clicked", self._on_media_button_clicked, "pause")
        self._control_buttons['stop'].connect("clicked", self._on_media_button_clicked, "stop")
        self._control_buttons['next'].connect("clicked", self._on_media_button_clicked, "next")
        self._control_buttons['prev'].connect("clicked", self._on_media_button_clicked, "prev")

        self._artist = builder.get_object("media_artist")
        self._track = builder.get_object("media_track")
        self._time = builder.get_object("media_time")

        self.set_icon(get_icon("multimedia-player"))
        self.show()
        self.connect("delete-event", self._on_window_delete)

        cr_name_address = builder.get_object("name_address")
        cr_name_address.props.ellipsize = Pango.EllipsizeMode.END

        cr_connected = builder.get_object("connected")
        cr_connected.props.sensitive = False
        cr_connected.props.style = Pango.Style.ITALIC

        self.liststore = Gtk.ListStore(str, str, object)
        self.device_combo = builder.get_object("device_combo")
        self.device_combo.set_model(self.liststore)
        self.device_combo.connect("changed", self._on_device_combo_changed)

        self._manager = Bluez.Manager()

        self._remote_control_devices = {}
        self.active_remote = None

        for adapter in self._manager.list_adapters():
            for device in adapter.list_devices():
                if self._has_remote_control(device['UUIDs']):
                    object_path = device.get_object_path()
                    player_path = os.path.join(object_path, 'player0')
                    remote_control = AVRemote(player_path)
                    sig = remote_control.connect_signal("property-changed", self._on_property_changed)
                    self._remote_control_devices[object_path] = (remote_control, sig)

                    self.add_to_list(device)
                    dprint("Added device: ", player_path)

        GLib.timeout_add_seconds(1, self._update_time)

    def add_to_list(self, device):
        dev_info = "%s\n<small>%s</small>" % (device['Alias'], device['Address'])
        if device['Connected']:
            conn_info = "Connected"
        else:
            conn_info = "Not Connected"

        titer = self.liststore.append([dev_info, conn_info, device.get_object_path()])

    def _has_remote_control(self, uuids):
        for uuid in uuids:
            uuid16 = uuid128_to_uuid16(uuid)
            if uuid16 == AV_REMOTE_TARGET_SVCLASS_ID:
                return True
        return False

    def update_track_info(self, remote):
        self._update_artist()
        self._update_time()
        self._update_track()

    def _update_time(self):
        if self.active_remote is None:
            return True

        pos = self.active_remote['Position']
        track_lenght = float(self.active_remote['Track']['Duration'])
        time_left = (track_lenght - pos) / 1000
        left_string = time.strftime('%M:%S', time.gmtime(time_left))
        self._time.set_markup("<b>%s</b>" % left_string)

        return True

    def _update_artist(self):
        artist = self.active_remote['Track']['Artist']
        artist_markup = "<b>%s</b>" % cgi.escape(artist)
        self._artist.set_markup(artist_markup)

    def _update_track(self):
        track = self.active_remote['Track']['Title']
        self._track.set_markup(cgi.escape(track))

    def _on_device_combo_changed(self, combo):
        titer = combo.get_active_iter()
        object_path = self.liststore[titer][2]
        self.active_remote = self._remote_control_devices[object_path][0]
        self.update_track_info(self.active_remote)
        dprint(object_path)

    def _on_media_button_clicked(self, button, action):
        dprint(action)
        if self.active_remote is None:
            return

        if action == "play":
            self.active_remote.play()
        elif action == "pause":
            self.active_remote.pause()
        elif action == "next":
            self.active_remote.next()
        elif action == "prev":
            self.active_remote.previous()
        elif action == "stop":
            self.active_remote.stop()

    def _on_window_delete(self, win, event):
        for path in list(self._remote_control_devices.keys()):
            remote, sig = self._remote_control_devices.pop(path)
            remote.disconnect_signal(sig)

        self.active_remote = None
        self._remote_control_devices = {}
        PlayerWindow.running = False
        self.destroy()

    def _update_track_times(self, track_lenght, time_left):
        position = self.active_remote['Position']
        self.time_label.set_markup("<b>%s</b>")

    def _on_device_created(self, object_path):
        dprint(object_path)

    def _on_device_removed(self, object_path):
        dprint(object_path)

    def _on_property_changed(self, remote, name, val, path):
        if not path == self.active_remote.get_object_path():
            return

        dprint(name, val)
        if name == "Track":
            self._update_artist()
            self._update_track()
        elif name == "Position":
            self._update_time()
        elif name == "Status":
            if val == "stopped":
                self._control_buttons['play'].props.sensitive = True
                self._control_buttons['stop'].props.sensitive = False
                self._control_buttons['pause'].props.sensitive = False
            elif val == "playing":
                self._control_buttons['play'].props.sensitive = False
                self._control_buttons['stop'].props.sensitive = True
                self._control_buttons['pause'].props.sensitive = True
            elif val == "paused":
                self._control_buttons['play'].props.sensitive = True
                self._control_buttons['stop'].props.sensitive = False
                self._control_buttons['pause'].props.sensitive = False


class RemoteMediaPlayer(AppletPlugin):
    __depends__ = ["Menu"]
    __icon__ = "multimedia-player"
    __description__ = _(
        "Allows you to control remote A/V media devices.")
    __author__ = "Sander Sweers (infirit)"
    __autoload__ = False

    def on_load(self, applet):
        item = create_menuitem(_("Media _Player"), get_icon("multimedia-player", 16))
        item.props.tooltip_text = _("Show a media player remote control")
        item.connect("activate", self.activate_ui)

        self.Applet.Plugins.Menu.Register(self, item, 85, True)

        self.player_window = None

    def on_unload(self):
        self.Applet.Plugins.Menu.Unregister(self)
        if self.player_window is not None:
            self.player_window.destroy()

    def activate_ui(self, item):
        if not self.player_window:
            self.player_window = PlayerWindow()
        elif self.player_window.running:
            self.player_window.present()

    def on_device_created(self, device):
        self.player_window._on_device_created(device)

    def on_device_removed(self, device):
        self.player_window._on_device_removed(device)

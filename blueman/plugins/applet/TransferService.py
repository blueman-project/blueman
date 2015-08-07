from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, GLib, Gtk
from datetime import datetime
import os
import shutil
from blueman.bluez import obex
from blueman.Functions import dprint, get_icon, launch
from blueman.gui.Notification import Notification
from blueman.main.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config

import dbus
import dbus.service


class _Agent:
    def __init__(self, applet):
        self._applet = applet
        self._config = Config("org.blueman.transfer")

        self._agent_path = '/org/blueman/obex_agent'

        self._agent = obex.Agent(self._agent_path)
        self._agent.connect('release', self._on_release)
        self._agent.connect('authorize', self._on_authorize)
        self._agent.connect('cancel', self._on_cancel)

        self._allowed_devices = []
        self._notification = None
        self._pending_transfer = None
        self.transfers = {}

        obex.AgentManager().register_agent(self._agent_path)

    def __del__(self):
        obex.AgentManager().unregister_agent(self._agent_path)

    def _on_release(self, _agent):
        raise Exception(self._agent_path + " was released unexpectedly")

    def _on_action(self, _notification, action):
        dprint(action)

        if action == "accept":
            self.transfers[self._pending_transfer['transfer_path']] = {
                'path': self._pending_transfer['root'] + '/' + os.path.basename(self._pending_transfer['filename']),
                'size': self._pending_transfer['size'],
                'name': self._pending_transfer['name']
            }
            self._agent.reply(self.transfers[self._pending_transfer['transfer_path']]['path'])
            self._allowed_devices.append(self._pending_transfer['address'])
            GObject.timeout_add(60000, self._allowed_devices.remove, self._pending_transfer['address'])
        else:
            self._agent.reply(obex.Error.Rejected)

    def _on_authorize(self, _agent, transfer_path, address=None, filename=None, size=None):
        if address and filename and size:
            # stand-alone obexd
            # FIXME: /tmp is only the default. Can we get the actual root
            # directory from stand-alone obexd?
            root = '/tmp'
        else:
            # BlueZ 5 integrated obexd
            transfer = obex.Transfer(transfer_path)
            session = obex.Session(transfer.session)
            root = session.root
            address = session.address
            filename = transfer.name
            size = transfer.size

        try:
            device = Device(self._applet.Manager.get_adapter().find_device(address))
            name = device.Alias
            trusted = device.Trusted
        except Exception as e:
            dprint(e)
            name = address
            trusted = False

        self._pending_transfer = {'transfer_path': transfer_path, 'address': address, 'root': root,
                                  'filename': filename, 'size': size, 'name': name}

        try:
            status_icon = self._applet.Plugins.StatusIcon
        except:
            status_icon = None

        # This device was neither allowed nor is it trusted -> ask for confirmation
        if address not in self._allowed_devices and not (self._config['opp-accept'] and trusted):
            self._notification = Notification(_("Incoming file over Bluetooth"),
                _("Incoming file %(0)s from %(1)s") % {"0": "<b>" + filename + "</b>",
                                                       "1": "<b>" + name + "</b>"},
                30000, [["accept", _("Accept"), "help-about"], ["reject", _("Reject"), "help-about"]], self._on_action,
                pixbuf=get_icon("blueman", 48), status_icon=status_icon)
        # Device is trusted or was already allowed, larger file -> display a notification, but auto-accept
        elif size > 350000:
            self._notification = Notification(_("Receiving file"),
                _("Receiving file %(0)s from %(1)s") % {"0": "<b>" + filename + "</b>",
                                                        "1": "<b>" + name + "</b>"},
                pixbuf=get_icon("blueman", 48), status_icon=status_icon)
            self._on_action(self._notification, 'accept')
        # Device is trusted or was already allowed. very small file -> auto-accept and transfer silently
        else:
            self._notification = None
            self._on_action(self._notification, "accept")

    def _on_cancel(self, agent):
        self._notification.close()
        agent.reply(obex.Error.Canceled)


class TransferService(AppletPlugin):
    __author__ = "cschramm"
    __description__ = _("Provides OBEX file transfer capabilities")
    __icon__ = "blueman-send-file"

    _config = None

    _silent_transfers = 0
    _normal_transfers = 0

    _manager = None
    _agent = None
    _watch = None

    def on_load(self, applet):
        self._config = Config("org.blueman.transfer")

        if not self._config["shared-path"]:
            d = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
            if not d:
                self._config["shared-path"] = os.path.expanduser("~")
            else:
                self._config["shared-path"] = d

        if not os.path.isdir(self._config["shared-path"]):
            dprint("Configured share directory %s does not exist" % self._config["shared-path"])

            dlg = Gtk.MessageDialog(None, buttons=Gtk.ButtonsType.OK, type=Gtk.MessageType.ERROR)
            text = _("Configured directory for incoming files does not exist")
            secondary_text = _("Please make sure that directory \"<b>%s</b>\" exists or configure it with blueman-services")
            dlg.props.text = text
            dlg.format_secondary_markup(secondary_text % self._config["shared-path"])

            dlg.run()
            dlg.destroy()

        self._manager = obex.Manager()
        self._manager.connect("transfer-started", self._on_transfer_started)
        self._manager.connect("transfer-completed", self._on_transfer_completed)
        self._manager.connect('session-removed', self._on_session_removed)

        self._watch = dbus.SessionBus().watch_name_owner("org.bluez.obex", self._on_obex_owner_changed)

    def on_unload(self):
        if self._watch:
            self._watch.cancel()

        self._agent = None

    def on_manager_state_changed(self, state):
        if not state:
            self._agent = None

    def _on_obex_owner_changed(self, owner):
        dprint("obex owner changed:", owner)
        if owner == "":
            self._agent = None
        else:
            self._agent = _Agent(self._applet)

    def _on_transfer_started(self, _manager, transfer_path):
        if transfer_path not in self._agent.transfers:
            # This is not an incoming transfer we authorized
            return

        if self._agent.transfers[transfer_path]['size'] > 350000:
            self._normal_transfers += 1
        else:
            self._silent_transfers += 1

    @staticmethod
    def _add_open(n, name, path):
        if Notification.actions_supported():
            print("adding action")

            def on_open(*_args):
                print("open")
                launch("xdg-open", [path], True)

            n.add_action("open", name, on_open, None)
            n.show()

    def _on_transfer_completed(self, _manager, transfer_path, success):
        try:
            attributes = self._agent.transfers[transfer_path]
        except KeyError:
            # This is probably not an incoming transfer we authorized
            return

        src = attributes['path']
        dest_dir = self._config["shared-path"]
        filename = os.path.basename(src)

        # We get bytes from pygobject under python 2.7
        if hasattr(dest_dir, "upper",) and hasattr(dest_dir, "decode"):
            dest_dir = dest_dir.decode("UTF-8")

        if os.path.exists(os.path.join(dest_dir, filename)):
            now = datetime.now()
            filename = "%s_%s" % (now.strftime("%Y%m%d%H%M%S"), filename)
            dprint("Destination file exists, renaming to: %s" % filename)

        dest = os.path.join(dest_dir, filename)
        shutil.move(src, dest)

        try:
            status_icon = self._applet.Plugins.StatusIcon
        except:
            status_icon = None

        if success:
            n = Notification(_("File received"),
                             _("File %(0)s from %(1)s successfully received") % {
                                 "0": "<b>" + filename + "</b>",
                                 "1": "<b>" + attributes['name'] + "</b>"},
                             pixbuf=get_icon("blueman", 48), status_icon=status_icon)
            self._add_open(n, "Open", dest)
        elif not success:
            Notification(_("Transfer failed"),
                         _("Transfer of file %(0)s failed") % {
                             "0": "<b>" + filename + "</b>",
                             "1": "<b>" + attributes['name'] + "</b>"},
                         pixbuf=get_icon("blueman", 48), status_icon=status_icon)

            if attributes['size'] > 350000:
                self._normal_transfers -= 1
            else:
                self._silent_transfers -= 1

        del self._agent.transfers[transfer_path]

    def _on_session_removed(self, _manager, _session_path):
        if self._silent_transfers == 0:
            return

        try:
            status_icon = self._applet.Plugins.StatusIcon
        except:
            status_icon = None

        if self._normal_transfers == 0:
            n = Notification(_("Files received"),
                             ngettext("Received %d file in the background", "Received %d files in the background",
                                      self._silent_transfers) % self._silent_transfers,
                             pixbuf=get_icon("blueman", 48), status_icon=status_icon)

            self._add_open(n, "Open Location", self._config["shared-path"])
        else:
            n = Notification(_("Files received"),
                             ngettext("Received %d more file in the background",
                                      "Received %d more files in the background",
                                      self._silent_transfers) % self._silent_transfers,
                             pixbuf=get_icon("blueman", 48), status_icon=status_icon)
            self._add_open(n, "Open Location", self._config["shared-path"])

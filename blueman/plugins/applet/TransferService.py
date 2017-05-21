# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Gio
from datetime import datetime
import os
import shutil
import logging
from blueman.bluez import obex
from blueman.Functions import get_icon, launch
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config

from html import escape


class Agent(obex.Agent):
    __agent_path = '/org/bluez/obex/agent/blueman'

    def __init__(self, applet):
        super(Agent, self).__init__(self.__agent_path, self._handle_method_call)

        self._applet = applet
        self._config = Config("org.blueman.transfer")

        self._allowed_devices = []
        self._notification = None
        self._pending_transfer = None
        self.transfers = {}

    def _handle_method_call(self, connection, sender, agent_path, interface_name, method_name, parameters, invocation):
        log_msg = "%s %s" % (method_name, agent_path)
        if method_name == 'Release':
            logging.info(log_msg)
            self._on_release()
        elif method_name == 'AuthorizePush':
            logging.info(log_msg)
            self._on_authorize(parameters, invocation)
        elif method_name == 'Cancel':
            logging.info(log_msg)
            self._on_cancel(parameters, invocation)

    def register(self):
        obex.AgentManager().register_agent(self.__agent_path)

    def unregister(self):
        obex.AgentManager().unregister_agent(self.__agent_path)

    def _on_release(self):
        raise Exception(self.__agent_path + " was released unexpectedly")

    def _on_authorize(self, parameters, invocation):
        def on_action(action):
            logging.info("Action %s" % action)

            if action == "accept":
                self.transfers[self._pending_transfer['transfer_path']] = {
                    'path': self._pending_transfer['root'] + '/' + os.path.basename(self._pending_transfer['filename']),
                    'size': self._pending_transfer['size'],
                    'name': self._pending_transfer['name']
                }

                param = GLib.Variant('(s)', (self.transfers[self._pending_transfer['transfer_path']]['path'],))
                invocation.return_value(param)

                self._allowed_devices.append(self._pending_transfer['address'])
                GLib.timeout_add(60000, self._allowed_devices.remove, self._pending_transfer['address'])
            else:
                invocation.return_dbus_error('org.bluez.obex.Error.Rejected', 'Rejected')

        transfer_path = parameters.unpack()[0]

        transfer = obex.Transfer(transfer_path)
        session = obex.Session(transfer.session)
        root = session.root
        address = session.address
        filename = transfer.name
        size = transfer.size

        try:
            adapter = self._applet.Manager.get_adapter()
            device = self._applet.Manager.find_device(address, adapter.get_object_path())
            name = device["Alias"]
            trusted = device["Trusted"]
        except Exception as e:
            logging.exception(e)
            name = address
            trusted = False

        self._pending_transfer = {'transfer_path': transfer_path, 'address': address, 'root': root,
                                  'filename': filename, 'size': size, 'name': name}

        notif_kwargs = {"icon_name": "blueman"}
        try:
            notif_kwargs["pos_hint"] = self._applet.Plugins.StatusIcon.geometry
        except AttributeError:
            logging.error("Failed to get StatusIcon")

        # This device was neither allowed nor is it trusted -> ask for confirmation
        if address not in self._allowed_devices and not (self._config['opp-accept'] and trusted):
            self._notification = Notification(_("Incoming file over Bluetooth"),
                _("Incoming file %(0)s from %(1)s") % {"0": "<b>" + escape(filename) + "</b>",
                                                       "1": "<b>" + escape(name) + "</b>"},
                30000, [["accept", _("Accept"), "help-about"], ["reject", _("Reject"), "help-about"]], on_action,
                **notif_kwargs)
            self._notification.show()
        # Device is trusted or was already allowed, larger file -> display a notification, but auto-accept
        elif size > 350000:
            self._notification = Notification(_("Receiving file"),
                _("Receiving file %(0)s from %(1)s") % {"0": "<b>" + escape(filename) + "</b>",
                                                        "1": "<b>" + escape(name) + "</b>"},
                **notif_kwargs)
            on_action('accept')
            self._notification.show()
        # Device is trusted or was already allowed. very small file -> auto-accept and transfer silently
        else:
            self._notification = None
            on_action("accept")

    def _on_cancel(self, parameters, invocation):
        self._notification.close()
        invocation.return_dbus_error('org.bluez.obex.Error.Canceled', 'Canceled')


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
            logging.info("Configured share directory %s does not exist" % self._config["shared-path"])

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

        self._watch = obex.Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)

    def on_unload(self):
        if self._watch:
            Gio.bus_unwatch_name(self._watch)

        self._unregister_agent()

    def _register_agent(self):
        if not self.__class__._agent:
            self.__class__._agent = Agent(self.Applet)
        self._agent.register()

    @classmethod
    def _unregister_agent(cls):
        if cls._agent:
            cls._agent.unregister()

    def on_manager_state_changed(self, state):
        if not state:
            self._unregister_agent()

    def _on_dbus_name_appeared(self, _connection, name, owner):
        logging.info("%s %s" % (name, owner))
        self._register_agent()

    def _on_dbus_name_vanished(self, _connection, name):
        logging.info(name)
        self._unregister_agent()

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
        if n.actions_supported:
            logging.info("adding action")

            def on_open(*_args):
                logging.info("open")
                launch("xdg-open", [path], True)

            n.add_action("open", name, on_open)

    @property
    def _notify_kwargs(self):
        kwargs = {"icon_name": "blueman"}
        try:
            kwargs["pos_hint"] = self.Applet.Plugins.StatusIcon.geometry
        except AttributeError:
            logging.error("No statusicon found")

        return kwargs

    def _on_transfer_completed(self, _manager, transfer_path, success):
        try:
            attributes = self._agent.transfers[transfer_path]
        except KeyError:
            logging.info("This is probably not an incoming transfer we authorized")
            return

        src = attributes['path']
        dest_dir = self._config["shared-path"]
        filename = os.path.basename(src)

        dest = os.path.join(dest_dir, filename)
        if os.path.exists(dest):
            now = datetime.now()
            filename = "%s_%s" % (now.strftime("%Y%m%d%H%M%S"), filename)
            logging.info("Destination file exists, renaming to: %s" % filename)

        try:
            shutil.move(src, dest)
        except Exception:
            logging.error("Failed to move files", exc_info=True)
            success = False

        if success:
            n = Notification(_("File received"),
                             _("File %(0)s from %(1)s successfully received") % {
                                 "0": "<b>" + escape(filename) + "</b>",
                                 "1": "<b>" + escape(attributes['name']) + "</b>"},
                             **self._notify_kwargs)
            self._add_open(n, "Open", dest)
            n.show()
        elif not success:
            n = Notification(_("Transfer failed"),
                         _("Transfer of file %(0)s failed") % {
                             "0": "<b>" + escape(filename) + "</b>",
                             "1": "<b>" + escape(attributes['name']) + "</b>"},
                         **self._notify_kwargs)
            n.show()
            if attributes['size'] > 350000:
                self._normal_transfers -= 1
            else:
                self._silent_transfers -= 1

        del self._agent.transfers[transfer_path]

    def _on_session_removed(self, _manager, _session_path):
        if self._silent_transfers == 0:
            return

        if self._normal_transfers == 0:
            n = Notification(_("Files received"),
                             ngettext("Received %d file in the background", "Received %d files in the background",
                                      self._silent_transfers) % self._silent_transfers,
                             **self._notify_kwargs)

            self._add_open(n, "Open Location", self._config["shared-path"])
            n.show()
        else:
            n = Notification(_("Files received"),
                             ngettext("Received %d more file in the background",
                                      "Received %d more files in the background",
                                      self._silent_transfers) % self._silent_transfers,
                             **self._notify_kwargs)
            self._add_open(n, "Open Location", self._config["shared-path"])
            n.show()

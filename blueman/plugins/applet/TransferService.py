from datetime import datetime
from gettext import gettext as _, ngettext
import os
import shutil
import logging
from html import escape
from typing import List, Dict, TYPE_CHECKING, Callable, Tuple, Optional, Union

from blueman.bluez.obex.AgentManager import AgentManager
from blueman.bluez.obex.Manager import Manager
from blueman.bluez.obex.Transfer import Transfer
from blueman.bluez.obex.Session import Session
from blueman.Functions import launch
from blueman.gui.Notification import Notification, _NotificationBubble, _NotificationDialog
from blueman.main.Applet import BluemanApplet
from blueman.main.DbusService import DbusService, DbusError
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config

from gi.repository import GLib, Gio

if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class TransferDict(TypedDict):
        path: str
        size: Optional[int]
        name: str

    class PendingTransferDict(TypedDict):
        transfer_path: str
        address: str
        root: str
        filename: str
        size: Optional[int]
        name: str

NotificationType = Union[_NotificationBubble, _NotificationDialog]


class ObexErrorRejected(DbusError):
    _name = "org.bluez.obex.Error.Rejected"


class ObexErrorCanceled(DbusError):
    _name = "org.bluez.obex.Error.Canceled"


class Agent(DbusService):
    __agent_path = '/org/bluez/obex/agent/blueman'

    def __init__(self, applet: BluemanApplet):
        super().__init__(None, "org.bluez.obex.Agent1", self.__agent_path, Gio.BusType.SESSION)

        self.add_method("Release", (), "", self._release)
        self.add_method("Cancel", (), "", self._cancel)
        self.add_method("AuthorizePush", ("o",), "s", self._authorize_push, is_async=True)
        self.register()

        self._applet = applet
        self._config = Config("org.blueman.transfer")

        self._allowed_devices: List[str] = []
        self._notification: Optional[NotificationType] = None
        self._pending_transfer: Optional["PendingTransferDict"] = None
        self.transfers: Dict[str, "TransferDict"] = {}

    def register_at_manager(self) -> None:
        AgentManager().register_agent(self.__agent_path)

    def unregister_from_manager(self) -> None:
        AgentManager().unregister_agent(self.__agent_path)

    def _release(self) -> None:
        raise Exception(self.__agent_path + " was released unexpectedly")

    def _authorize_push(self, transfer_path: str, ok: Callable[[str], None],
                        err: Callable[[ObexErrorRejected], None]) -> None:
        def on_action(action: str) -> None:
            logging.info("Action %s" % action)

            if action == "accept":
                assert self._pending_transfer
                self.transfers[self._pending_transfer['transfer_path']] = {
                    'path': self._pending_transfer['root'] + '/' + os.path.basename(self._pending_transfer['filename']),
                    'size': self._pending_transfer['size'],
                    'name': self._pending_transfer['name']
                }

                ok(self.transfers[self._pending_transfer['transfer_path']]['path'])

                self._allowed_devices.append(self._pending_transfer['address'])

                def _remove() -> bool:
                    assert self._pending_transfer is not None  # https://github.com/python/mypy/issues/2608
                    self._allowed_devices.remove(self._pending_transfer['address'])
                    return False

                GLib.timeout_add(60000, _remove)
            else:
                err(ObexErrorRejected("Rejected"))

        transfer = Transfer(obj_path=transfer_path)
        session = Session(obj_path=transfer.session)
        root = session.root
        address = session.address
        filename = transfer.name
        size = transfer.size

        try:
            adapter = self._applet.Manager.get_adapter()
            device = self._applet.Manager.find_device(address, adapter.get_object_path())
            assert device is not None
            name = device["Alias"]
            trusted = device["Trusted"]
        except Exception as e:
            logging.exception(e)
            name = address
            trusted = False

        self._pending_transfer = {'transfer_path': transfer_path, 'address': address, 'root': root,
                                  'filename': filename, 'size': size, 'name': name}

        # This device was neither allowed nor is it trusted -> ask for confirmation
        if address not in self._allowed_devices and not (self._config['opp-accept'] and trusted):
            self._notification = notification = Notification(
                _("Incoming file over Bluetooth"),
                _("Incoming file %(0)s from %(1)s") % {"0": "<b>" + escape(filename) + "</b>",
                                                       "1": "<b>" + escape(name) + "</b>"},
                30000, [("accept", _("Accept")), ("reject", _("Reject"))], on_action,
                icon_name="blueman"
            )
            notification.show()
        # Device is trusted or was already allowed, larger file -> display a notification, but auto-accept
        elif size and size > 350000:
            self._notification = notification = Notification(
                _("Receiving file"),
                _("Receiving file %(0)s from %(1)s") % {"0": "<b>" + escape(filename) + "</b>",
                                                        "1": "<b>" + escape(name) + "</b>"},
                icon_name="blueman"
            )
            on_action('accept')
            notification.show()
        # Device is trusted or was already allowed. very small file -> auto-accept and transfer silently
        else:
            self._notification = None
            on_action("accept")

    def _cancel(self) -> None:
        if self._notification:
            self._notification.close()
        raise ObexErrorCanceled("Canceled")


class TransferService(AppletPlugin):
    __author__ = "cschramm"
    __description__ = _("Provides OBEX file transfer capabilities")
    __icon__ = "blueman-send-file"

    _silent_transfers = 0
    _normal_transfers = 0

    _manager = None
    _agent = None
    _watch = None
    _notification = None
    _handlerids: List[int] = []

    def on_load(self) -> None:
        def on_reset(_action: str) -> None:
            self._notification = None
            self._config.reset('shared-path')
            logging.info('Reset share path')

        self._config = Config("org.blueman.transfer")

        share_path, invalid_share_path = self._make_share_path()

        if invalid_share_path:
            text = _('Configured directory for incoming files does not exist')
            secondary_text = _('Please make sure that directory "<b>%s</b>" exists or '
                               'configure it with blueman-services. Until then the default "%s" will be used')
            self._notification = Notification(text, secondary_text % (self._config["shared-path"], share_path),
                                              icon_name='blueman', timeout=30000,
                                              actions=[('reset', 'Reset to default')], actions_cb=on_reset)
            self._notification.show()

        self._watch = Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)

    def on_unload(self) -> None:
        if self._watch:
            Gio.bus_unwatch_name(self._watch)

        self._unregister_agent()

    def _make_share_path(self) -> Tuple[str, bool]:
        config_path = self._config["shared-path"]
        default_path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
        path = None
        error = False

        if config_path == '':
            path = default_path
        elif not os.path.isdir(config_path):
            path = default_path
            error = True
            logging.warning('Invalid shared-path %s' % config_path)
        else:
            path = config_path

        if not path:
            path = os.path.expanduser("~")
            logging.warning('Failed to get Download dir from XDG')

        # We used to always store the full path which caused problems
        if config_path == default_path:
            logging.info('Reset stored path, identical to default path.')
            self._config["shared-path"] = ''

        return path, error

    def _register_agent(self) -> None:
        if not self._agent:
            self._agent = Agent(self.parent)
        self._agent.register_at_manager()

    def _unregister_agent(self) -> None:
        if self._agent:
            self._agent.unregister_from_manager()
            self._agent.unregister()
            self._agent = None

    def _on_dbus_name_appeared(self, _connection: Gio.DBusConnection, name: str, owner: str) -> None:
        logging.info(f"{name} {owner}")

        self._manager = Manager()
        self._handlerids.append(self._manager.connect("transfer-started", self._on_transfer_started))
        self._handlerids.append(self._manager.connect("transfer-completed", self._on_transfer_completed))
        self._handlerids.append(self._manager.connect('session-removed', self._on_session_removed))

        self._register_agent()

    def _on_dbus_name_vanished(self, _connection: Gio.DBusConnection, name: str) -> None:
        logging.info(f"{name} not running or was stopped")

        if self._manager:
            for sigid in self._handlerids:
                self._manager.disconnect(sigid)
            self._manager = None
            self._handlerids = []

        if self._agent:
            self._agent.unregister()
            self._agent = None

    def _on_transfer_started(self, _manager: Manager, transfer_path: str) -> None:
        if not self._agent or transfer_path not in self._agent.transfers:
            # This is not an incoming transfer we authorized
            return

        size = self._agent.transfers[transfer_path]['size']
        assert size is not None
        if size > 350000:
            self._normal_transfers += 1
        else:
            self._silent_transfers += 1

    def _add_open(self, n: NotificationType, name: str, path: str) -> None:
        if n.actions_supported:
            logging.info("adding action")

            def on_open(_action: str) -> None:
                self._notification = None
                logging.info("open")
                launch("xdg-open", paths=[path], system=True)

            n.add_action("open", name, on_open)

    def _on_transfer_completed(self, _manager: Manager, transfer_path: str, success: bool) -> None:
        if not self._agent or transfer_path not in self._agent.transfers:
            logging.info("This is probably not an incoming transfer we authorized")
            return

        attributes = self._agent.transfers[transfer_path]

        src = attributes['path']
        dest_dir, ignored = self._make_share_path()
        filename = os.path.basename(src)

        dest = os.path.join(dest_dir, filename)
        if os.path.exists(dest):
            now = datetime.now()
            filename = f"{now.strftime('%Y%m%d%H%M%S')}_{filename}"
            logging.info(f"Destination file exists, renaming to: {filename}")

        try:
            shutil.move(src, dest)
        except (OSError, PermissionError):
            logging.error("Failed to move files", exc_info=True)
            success = False

        if success:
            self._notification = Notification(_("File received"),
                                              _("File %(0)s from %(1)s successfully received") % {
                                                  "0": "<b>" + escape(filename) + "</b>",
                                                  "1": "<b>" + escape(attributes['name']) + "</b>"},
                                              icon_name="blueman")
            self._add_open(self._notification, "Open", dest)
            self._notification.show()
        elif not success:
            n = Notification(
                _("Transfer failed"),
                _("Transfer of file %(0)s failed") % {
                    "0": "<b>" + escape(filename) + "</b>",
                    "1": "<b>" + escape(attributes['name']) + "</b>"},
                icon_name="blueman"
            )
            n.show()
            assert attributes['size'] is not None
            if attributes['size'] > 350000:
                self._normal_transfers -= 1
            else:
                self._silent_transfers -= 1

        del self._agent.transfers[transfer_path]

    def _on_session_removed(self, _manager: Manager, _session_path: str) -> None:
        if self._silent_transfers == 0:
            return

        share_path, ignored = self._make_share_path()
        if self._normal_transfers == 0:
            self._notification = Notification(_("Files received"),
                                              ngettext("Received %(files)d file in the background",
                                                       "Received %(files)d files in the background",
                                                       self._silent_transfers) % {"files": self._silent_transfers},
                                              icon_name="blueman")

            self._add_open(self._notification, "Open Location", share_path)
            self._notification.show()
        else:
            self._notification = Notification(_("Files received"),
                                              ngettext("Received %(files)d more file in the background",
                                                       "Received %(files)d more files in the background",
                                                       self._silent_transfers) % {"files": self._silent_transfers},
                                              icon_name="blueman")
            self._add_open(self._notification, "Open Location", share_path)
            self._notification.show()

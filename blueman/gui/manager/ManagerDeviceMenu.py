import logging
from enum import Enum, auto
from gettext import gettext as _
from operator import attrgetter
from typing import TYPE_CHECKING
from collections.abc import Iterable
from blueman.bluemantyping import BtAddress

from blueman.bluemantyping import ObjectPath
from blueman.Functions import create_menuitem, e_
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Network import AnyNetwork
from blueman.bluez.Device import AnyDevice, Device
from blueman.config.AutoConnectConfig import AutoConnectConfig
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.main.Builder import Builder
from blueman.main.DBusProxies import AppletService, DBusProxyFailed
from blueman.Sdp import (
    ServiceUUID,
    AUDIO_SOURCE_SVCLASS_ID,
    AUDIO_SINK_SVCLASS_ID,
    HANDSFREE_AGW_SVCLASS_ID,
    HANDSFREE_SVCLASS_ID,
    HEADSET_SVCLASS_ID,
    HID_SVCLASS_ID)

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk
from gi.repository import GLib

if TYPE_CHECKING:
    from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList
    from blueman.main.Manager import Blueman


class DeviceMenuItem:
    class Group(Enum):
        CONNECT = auto()
        DISCONNECT = auto()
        AUTOCONNECT = auto()
        ACTIONS = auto()

    def __init__(self, item: Gtk.MenuItem, group: Group, position: int):
        self.item = item
        self.group = group
        self.position = position


class MenuItemsProvider:
    def on_request_menu_items(
        self,
        _manager_menu:
        "ManagerDeviceMenu",
        _device: Device,
        _powered: bool,
    ) -> list[DeviceMenuItem]:
        return []


class ManagerDeviceMenu(Gtk.Menu):
    __ops__: dict[ObjectPath, str] = {}
    __instances__: list["ManagerDeviceMenu"] = []

    SelectedDevice: Device

    def __init__(self, blueman: "Blueman") -> None:
        super().__init__()
        self.set_name("ManagerDeviceMenu")
        self.Blueman = blueman

        self.is_popup = False

        self._device_property_changed_signal = self.Blueman.List.connect("device-property-changed",
                                                                         self.on_device_property_changed)
        ManagerDeviceMenu.__instances__.append(self)

        self._any_network = AnyNetwork()
        self._any_network.connect_signal('property-changed', self._on_service_property_changed)

        self._any_device = AnyDevice()
        self._any_device.connect_signal('property-changed', self._on_service_property_changed)

        try:
            self._appl: AppletService | None = AppletService()
        except DBusProxyFailed:
            logging.error("** Failed to connect to applet", exc_info=True)
            self._appl = None

        self.generate()

    def __del__(self) -> None:
        logging.debug("deleting devicemenu")

    def popup_at_pointer(self, event: Gdk.Event | None) -> None:
        self.is_popup = True
        self.generate()

        super().popup_at_pointer(event)

    def clear(self) -> None:
        def remove_and_destroy(child: Gtk.Widget) -> None:
            self.remove(child)
            child.destroy()

        self.foreach(remove_and_destroy)

    def set_op(self, device: Device, message: str) -> None:
        ManagerDeviceMenu.__ops__[device.get_object_path()] = message
        for inst in ManagerDeviceMenu.__instances__:
            logging.info(f"op: regenerating instance {inst}")
            if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
                inst.generate()

    def get_op(self, device: Device) -> str | None:
        try:
            return ManagerDeviceMenu.__ops__[device.get_object_path()]
        except KeyError:
            return None

    def unset_op(self, device: Device) -> None:
        object_path = device.get_object_path()
        message = self.__ops__.pop(object_path, None)
        if message is None:
            logging.error(f"No message found for {object_path}")

        for inst in ManagerDeviceMenu.__instances__:
            logging.info(f"op: regenerating instance {inst}")
            if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
                inst.generate()

    def _on_service_property_changed(self, _service: AnyNetwork | AnyDevice, key: str, _value: object,
                                     _path: str) -> None:
        if key == "Connected":
            self.generate()

    GENERIC_CONNECT = "00000000-0000-0000-0000-000000000000"

    def connect_service(self, device: Device, uuid: str = GENERIC_CONNECT) -> None:
        def success(_obj: AppletService, _result: None, _user_data: None) -> None:
            logging.info("success")
            prog.message(_("Success!"))

            self.unset_op(device)

        def fail(_obj: AppletService | None, result: GLib.Error, _user_data: None) -> None:
            prog.message(_("Failed"))

            self.unset_op(device)
            logging.warning(f"fail {result}")
            self._handle_error_message(result)

        self.set_op(device, _("Connecting…"))
        prog = ManagerProgressbar(self.Blueman, cancellable=uuid == self.GENERIC_CONNECT)
        if uuid == self.GENERIC_CONNECT:
            prog.connect("cancelled", lambda x: self.disconnect_service(device))

        if self._appl is None:
            fail(None, GLib.Error('Applet DBus Service not available'), None)
            return

        self._appl.ConnectService('(os)', device.get_object_path(), uuid,
                                  result_handler=success, error_handler=fail,
                                  timeout=GLib.MAXINT)

        prog.start()

    def disconnect_service(self, device: Device, uuid: str = GENERIC_CONNECT, port: int = 0) -> None:
        def ok(_obj: AppletService, _result: None, _user_date: None) -> None:
            logging.info("disconnect success")
            self.generate()

        def err(_obj: AppletService | None, result: GLib.Error, _user_date: None) -> None:
            logging.warning(f"disconnect failed {result}")
            msg, tb = e_(result.message)
            self.Blueman.infobar_update(_("Disconnection Failed: ") + msg, bt=tb)
            self.generate()

        if self._appl is None:
            err(None, GLib.Error('Applet DBus Service not available'), None)
            return

        self._appl.DisconnectService('(osd)', device.get_object_path(), uuid, port,
                                     result_handler=ok, error_handler=err, timeout=GLib.MAXINT)

    def on_device_property_changed(self, lst: "ManagerDeviceList", _device: Device, tree_iter: Gtk.TreeIter,
                                   key_value: tuple[str, object]) -> None:
        key, value = key_value
        # print "menu:", key, value
        if lst.compare(tree_iter, lst.selected()):
            if key in ("Connected", "UUIDs", "Trusted", "Paired", "Blocked"):
                self.generate()

    def _handle_error_message(self, error: GLib.Error) -> None:
        err = self._BLUEZ_ERROR_MAP.get(error.message.split(":", 3)[-1].strip())

        if err == self._BluezError.PROFILE_UNAVAILABLE:
            logging.warning("No audio endpoints registered to bluetoothd. "
                            "Pulseaudio Bluetooth module, bluez-alsa, PipeWire or other audio support missing.")
            msg = _("No audio endpoints registered")
        elif err == self._BluezError.CREATE_SOCKET:
            logging.warning("bluetoothd reported input/output error. Check its logs for context.")
            msg = _("Input/output error")
        elif err == self._BluezError.PAGE_TIMEOUT:
            msg = _("Device did not respond")
        elif err == self._BluezError.UNKNOWN:
            logging.warning("bluetoothd reported an unknown error. "
                            "Retry or check its logs for context.")
            msg = _("Unknown error")
        else:
            msg = error.message.split(":", 3)[-1].strip()

        if err != self._BluezError.CANCELED:
            self.Blueman.infobar_update(_("Connection Failed: ") + msg)

    class _BluezError(Enum):
        PAGE_TIMEOUT = auto()
        PROFILE_UNAVAILABLE = auto()
        CREATE_SOCKET = auto()
        CANCELED = auto()
        UNKNOWN = auto()

    # BlueZ 5.62 introduced machine-readable error strings while earlier versions
    # used strerror() so that the messages depend on the libc implementation:
    # https://sourceware.org/git/?p=glibc.git;a=blob;f=sysdeps/gnu/errlist.h
    # https://git.musl-libc.org/cgit/musl/tree/src/errno/__strerror.h
    # https://git.uclibc.org/uClibc/tree/libc/string/_string_syserrmsgs.c
    _BLUEZ_ERROR_MAP = {
        "Protocol not available": _BluezError.PROFILE_UNAVAILABLE,
        "br-connection-profile-unavailable": _BluezError.PROFILE_UNAVAILABLE,
        "Input/output error": _BluezError.CREATE_SOCKET,
        "I/O error": _BluezError.CREATE_SOCKET,
        "br-connection-create-socket": _BluezError.CREATE_SOCKET,
        "le-connection-create-socket": _BluezError.CREATE_SOCKET,
        "Host is down": _BluezError.PAGE_TIMEOUT,
        "br-connection-page-timeout": _BluezError.PAGE_TIMEOUT,
        "br-connection-unknown": _BluezError.UNKNOWN,
        "Cancelled": _BluezError.CANCELED,
        "br-connection-canceled": _BluezError.CANCELED,
    }

    def show_generic_connect_calc(self, device_uuids: Iterable[str]) -> bool:
        # Generic (dis)connect
        for uuid in device_uuids:
            service_uuid = ServiceUUID(uuid)
            if service_uuid.short_uuid in (
                    AUDIO_SOURCE_SVCLASS_ID, AUDIO_SINK_SVCLASS_ID, HANDSFREE_AGW_SVCLASS_ID, HANDSFREE_SVCLASS_ID,
                    HEADSET_SVCLASS_ID, HID_SVCLASS_ID, 0x1812
            ):
                return True
            elif not service_uuid.reserved:
                if uuid == '03b80e5a-ede8-4b33-a751-6ce34ec4c700':
                    return True
        # LE devices do not appear to expose certain properties like uuids until connect to at least once.
        return not device_uuids

    def _add_seperator(self) -> None:
        sep_item = Gtk.SeparatorMenuItem(visible=True)
        self.append(sep_item)

    def _add_menu_item(self, label: str, icon_name: str | None = None, sensitive: bool = True,
                       tooltip: str | None = None) -> Gtk.ImageMenuItem:
        item = create_menuitem(text=label, icon_name=icon_name)
        item.set_sensitive(sensitive)
        if tooltip is not None:
            item.set_tooltip_text(tooltip)
        self.append(item)
        return item

    def generate(self) -> None:
        self.clear()

        if not self.is_popup or self.props.visible:
            selected = self.Blueman.List.selected()
            if not selected:
                return
        else:
            (x, y) = self.Blueman.List.get_pointer()
            posdata = self.Blueman.List.get_path_at_pos(x, y)
            if posdata is None:
                return

            path = posdata[0]
            if path is None:
                raise TypeError("Path should never be None")

            tree_iter = self.Blueman.List.filter.get_iter(path)
            assert tree_iter is not None
            selected = self.Blueman.List.filter.convert_iter_to_child_iter(tree_iter)
            assert selected is not None

        row = self.Blueman.List.get(selected, "alias", "paired", "connected", "trusted", "objpush", "device", "blocked")
        self.SelectedDevice = row["device"]

        op = self.get_op(self.SelectedDevice)

        if op is not None:
            self._add_menu_item(label=op, icon_name="network-transmit-receive-symbolic", sensitive=False)
            return

        show_generic_connect = self.show_generic_connect_calc(self.SelectedDevice['UUIDs'])

        powered = Adapter(obj_path=self.SelectedDevice["Adapter"])["Powered"]
        blocked = self.SelectedDevice["Blocked"]

        if not row["connected"] and show_generic_connect and powered:
            if blocked:
                tooltip = _("Not available (Blocked)")
            else:
                tooltip = _("Connects auto connect profiles A2DP source, A2DP sink, and HID")

            connect_item = self._add_menu_item(
                label=_("<b>_Connect</b>"),
                icon_name="bluetooth-symbolic",
                tooltip=tooltip,
                sensitive=not blocked
            )
            connect_item.connect("activate", lambda _item: self.connect_service(self.SelectedDevice))
        elif row["connected"] and show_generic_connect:
            connect_item = self._add_menu_item(
                label=_("<b>_Disconnect</b>"),
                icon_name="bluetooth-disabled-symbolic",
                tooltip=_("Forcefully disconnect the device")
            )
            connect_item.connect("activate", lambda _item: self.disconnect_service(self.SelectedDevice))

        logging.debug(row["alias"])

        items = [item for plugin in self.Blueman.Plugins.get_loaded_plugins(MenuItemsProvider)
                 for item in plugin.on_request_menu_items(self, self.SelectedDevice, powered)]

        connect_items = [i for i in items if i.group == DeviceMenuItem.Group.CONNECT]
        disconnect_items = [i for i in items if i.group == DeviceMenuItem.Group.DISCONNECT]
        autoconnect_items = [item for item in items if item.group == DeviceMenuItem.Group.AUTOCONNECT]
        action_items = [i for i in items if i.group == DeviceMenuItem.Group.ACTIONS]

        if connect_items and not blocked:
            self.append(self._create_header(_("<b>Connect To:</b>")))
            for it in sorted(connect_items, key=attrgetter("position")):
                self.append(it.item)

        if disconnect_items:
            self.append(self._create_header(_("<b>Disconnect:</b>")))
            for it in sorted(disconnect_items, key=attrgetter("position")):
                self.append(it.item)

        auto_connect_config = AutoConnectConfig()
        generic_service = ServiceUUID("00000000-0000-0000-0000-000000000000")
        object_path = self.SelectedDevice.get_object_path()
        btaddress: BtAddress = self.SelectedDevice["Address"]
        generic_autoconnect = (object_path, str(generic_service)) in set(auto_connect_config["services"])

        if row["connected"] or generic_autoconnect or autoconnect_items:
            self.append(self._create_header(_("<b>Auto-connect:</b>")))

            if row["connected"] or generic_autoconnect:
                auto_connect_item = Gtk.CheckMenuItem(label=generic_service.name)
                auto_connect_config.bind_to_menuitem(auto_connect_item, (btaddress, str(generic_service)))
                auto_connect_item.show()
                self.append(auto_connect_item)

            for it in sorted(autoconnect_items, key=attrgetter("position")):
                self.append(it.item)

        if (powered and show_generic_connect) or connect_items or disconnect_items or autoconnect_items:
            self._add_seperator()

        for it in sorted(action_items, key=attrgetter("position")):
            self.append(it.item)

        if powered and row["objpush"] and not blocked:
            send_item = self._add_menu_item(
                label=_("Send a _File…"),
                icon_name="blueman-send-symbolic"
            )
            send_item.connect("activate", lambda _: self.Blueman.send(self.SelectedDevice))

            self._add_seperator()

        self._add_menu_item(
            label=_("_Pair"),
            icon_name="blueman-pair-symbolic",
            tooltip=_("Create pairing with the device") if not blocked else _("Not available (Blocked)"),
            sensitive=False if blocked else not row["paired"]
        )

        trust_item = self._add_menu_item(
            label=_("_Untrust") if row["trusted"] else _("_Trust"),
            icon_name="blueman-untrust-symbolic" if row["trusted"] else "blueman-trust-symbolic",
            tooltip=_("Mark/Unmark this device as trusted"),
        )
        trust_item.connect("activate", lambda _: self.Blueman.toggle_trust(self.SelectedDevice))

        block_item = self._add_menu_item(
            label=_("_Unblock") if row["blocked"] else _("_Block"),
            icon_name="blueman-block-symbolic",
            tooltip=_("Block/Unblock this device")
        )
        block_item.connect("activate", lambda _: self.Blueman.toggle_blocked(self.SelectedDevice))

        def on_rename(_item: Gtk.MenuItem, device: Device) -> None:
            def on_response(rename_dialog: Gtk.Dialog, response_id: int) -> None:
                if response_id == Gtk.ResponseType.ACCEPT:
                    assert isinstance(alias_entry, Gtk.Entry)  # https://github.com/python/mypy/issues/2608
                    device.set('Alias', alias_entry.get_text())
                elif response_id == 1:
                    device.set('Alias', '')
                rename_dialog.destroy()

            builder = Builder("rename-device.ui")
            dialog = builder.get_widget("dialog", Gtk.Dialog)
            dialog.set_transient_for(self.Blueman.window)

            alias_entry = builder.get_widget("alias_entry", Gtk.Entry)
            alias_entry.set_text(device['Alias'])
            dialog.connect("response", on_response)
            dialog.present()

        rename_item = self._add_menu_item(label=_("R_ename device…"))
        rename_item.connect('activate', on_rename, self.SelectedDevice)

        self._add_seperator()

        remove_item = self._add_menu_item(
            label=_("_Remove…"),
            icon_name="list-remove-symbolic",
            tooltip=_("Remove this device from the known devices list")
        )
        remove_item.connect("activate", lambda _: self.Blueman.remove(self.SelectedDevice))

    @staticmethod
    def _create_header(text: str) -> Gtk.MenuItem:
        item = Gtk.MenuItem()
        label = Gtk.Label()
        label.set_markup(text)
        label.props.xalign = 0.0

        label.show()
        item.add(label)
        item.props.sensitive = False
        item.show()
        return item

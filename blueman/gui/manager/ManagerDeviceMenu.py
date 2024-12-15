import logging
from enum import Enum, auto
from gettext import gettext as _
from operator import attrgetter
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING, Union, Iterable
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
    ) -> List[DeviceMenuItem]:
        return []


class ManagerDeviceMenu(Gtk.Menu):
    __ops__: Dict[ObjectPath, str] = {}
    __instances__: List["ManagerDeviceMenu"] = []

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
            self._appl: Optional[AppletService] = AppletService()
        except DBusProxyFailed:
            logging.error("** Failed to connect to applet", exc_info=True)
            self._appl = None

        self.generate()

    def __del__(self) -> None:
        logging.debug("deleting devicemenu")

    def popup_at_pointer(self, event: Optional[Gdk.Event]) -> None:
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

    def get_op(self, device: Device) -> Optional[str]:
        try:
            return ManagerDeviceMenu.__ops__[device.get_object_path()]
        except KeyError:
            return None

    def unset_op(self, device: Device) -> None:
        del ManagerDeviceMenu.__ops__[device.get_object_path()]
        for inst in ManagerDeviceMenu.__instances__:
            logging.info(f"op: regenerating instance {inst}")
            if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
                inst.generate()

    def _on_service_property_changed(self, _service: Union[AnyNetwork, AnyDevice], key: str, _value: object,
                                     _path: str) -> None:
        if key == "Connected":
            self.generate()

    GENERIC_CONNECT = "00000000-0000-0000-0000-000000000000"

    def connect_service(self, device: Device, uuid: str = GENERIC_CONNECT) -> None:
        def success(_obj: AppletService, _result: None, _user_data: None) -> None:
            logging.info("success")
            prog.message(_("Success!"))

            self.unset_op(device)

        def fail(_obj: Optional[AppletService], result: GLib.Error, _user_data: None) -> None:
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

        def err(_obj: Optional[AppletService], result: GLib.Error, _user_date: None) -> None:
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
                                   key_value: Tuple[str, object]) -> None:
        key, value = key_value
        # print "menu:", key, value
        if lst.compare(tree_iter, lst.selected()):
            if key in ("Connected", "UUIDs", "Trusted", "Paired", "Blocked"):
                self.generate()

    def _handle_error_message(self, error: GLib.Error) -> None:
        bt_error_code = error.message.split(":", 3)[-1].strip()
        err = self._BLUEZ_ERROR_MAP.get(bt_error_code)
        if err == self._BluezError.CANCELED:
            logging.info("bluetoothd: " + "Canceled.")
            return
        if err == self._BluezError.PROFILE_UNAVAILABLE:
            logging.warning("bluetoothd: " + "No audio endpoints registered." + " " +
                            "PulseAudio Bluetooth module, bluez-alsa, PipeWire or other audio support missing.")
            msg = _("No audio endpoints registered.")
        elif err == self._BluezError.CREATE_SOCKET:
            logging.warning("bluetoothd: " + "Input/output error." + " " + "Check bluetoothd logs.")
            msg = _("Input/output error.")
        elif err == self._BluezError.PAGE_TIMEOUT:
            logging.info("bluetoothd: " + "Device did not respond")
            msg = _("Device did not respond")
        elif err == self._BluezError.UNKNOWN:
            logging.warning("bluetoothd: " + "Unknown error." + " " + "Check bluetoothd logs.")
            msg = _("Unknown error.")
        else:
            logging.warning("bluetoothd: " + bt_error_code + " " + "Check bluetoothd logs.")
            msg = bt_error_code
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

    def generate(self) -> None:
        self.clear()

        if not self.is_popup or self.props.visible:
            selected = self.Blueman.List.selected()
            if not selected:
                return
            row = self.Blueman.List.get(selected, "alias", "paired", "connected", "trusted", "objpush", "device",
                                        "blocked")
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
            child_iter = self.Blueman.List.filter.convert_iter_to_child_iter(tree_iter)
            assert child_iter is not None

            row = self.Blueman.List.get(child_iter, "alias", "paired", "connected", "trusted", "objpush", "device",
                                        "blocked")

        self.SelectedDevice = row["device"]

        op = self.get_op(self.SelectedDevice)

        if op is not None:
            item: Gtk.MenuItem = create_menuitem(op, "network-transmit-receive-symbolic")
            item.props.sensitive = False
            item.show()
            self.append(item)
            return

        show_generic_connect = self.show_generic_connect_calc(self.SelectedDevice['UUIDs'])

        powered = Adapter(obj_path=self.SelectedDevice["Adapter"])["Powered"]

        if not row["connected"] and show_generic_connect and powered:
            connect_item = create_menuitem(_("<b>_Connect</b>"), "bluetooth-symbolic")
            connect_item.connect("activate", lambda _item: self.connect_service(self.SelectedDevice))
            connect_item.props.tooltip_text = _("Connects auto connect profiles A2DP source, A2DP sink, and HID")
            connect_item.show()
            self.append(connect_item)
        elif row["connected"] and show_generic_connect:
            connect_item = create_menuitem(_("<b>_Disconnect</b>"), "bluetooth-disabled-symbolic")
            connect_item.props.tooltip_text = _("Forcefully disconnect the device")
            connect_item.connect("activate", lambda _item: self.disconnect_service(self.SelectedDevice))
            connect_item.show()
            self.append(connect_item)

        logging.debug(row["alias"])

        items = [item for plugin in self.Blueman.Plugins.get_loaded_plugins(MenuItemsProvider)
                 for item in plugin.on_request_menu_items(self, self.SelectedDevice, powered)]

        connect_items = [i for i in items if i.group == DeviceMenuItem.Group.CONNECT]
        disconnect_items = [i for i in items if i.group == DeviceMenuItem.Group.DISCONNECT]
        autoconnect_items = [item for item in items if item.group == DeviceMenuItem.Group.AUTOCONNECT]
        action_items = [i for i in items if i.group == DeviceMenuItem.Group.ACTIONS]

        if connect_items:
            self.append(self._create_header(_("<b>Connect To:</b>")))
            for it in sorted(connect_items, key=attrgetter("position")):
                self.append(it.item)

        if disconnect_items:
            self.append(self._create_header(_("<b>Disconnect:</b>")))
            for it in sorted(disconnect_items, key=attrgetter("position")):
                self.append(it.item)

        config = AutoConnectConfig()
        generic_service = ServiceUUID("00000000-0000-0000-0000-000000000000")
        object_path = self.SelectedDevice.get_object_path()
        btaddress: BtAddress = self.SelectedDevice["Address"]
        generic_autoconnect = (object_path, str(generic_service)) in set(config["services"])

        if row["connected"] or generic_autoconnect or autoconnect_items:
            self.append(self._create_header(_("<b>Auto-connect:</b>")))

            if row["connected"] or generic_autoconnect:
                item = Gtk.CheckMenuItem(label=generic_service.name)
                config.bind_to_menuitem(item, (btaddress, str(generic_service)))
                item.show()
                self.append(item)

            for it in sorted(autoconnect_items, key=attrgetter("position")):
                self.append(it.item)

        if (powered and show_generic_connect) or connect_items or disconnect_items or autoconnect_items:
            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

        for it in sorted(action_items, key=attrgetter("position")):
            self.append(it.item)

        if powered:
            send_item = create_menuitem(_("Send a _File…"), "blueman-send-symbolic")
            send_item.props.sensitive = False
            self.append(send_item)
            send_item.show()

            if row["objpush"]:
                send_item.connect("activate", lambda x: self.Blueman.send(self.SelectedDevice))
                send_item.props.sensitive = True

            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

        item = create_menuitem(_("_Pair"), "blueman-pair-symbolic")
        item.props.tooltip_text = _("Create pairing with the device")
        self.append(item)
        item.show()
        if not row["paired"]:
            item.connect("activate", lambda x: self.Blueman.bond(self.SelectedDevice))
        else:
            item.props.sensitive = False

        if not row["trusted"]:
            item = create_menuitem(_("_Trust"), "blueman-trust-symbolic")
            item.connect("activate", lambda x: self.Blueman.toggle_trust(self.SelectedDevice))
            self.append(item)
            item.show()
        else:
            item = create_menuitem(_("_Untrust"), "blueman-untrust-symbolic")
            self.append(item)
            item.connect("activate", lambda x: self.Blueman.toggle_trust(self.SelectedDevice))
            item.show()
        item.props.tooltip_text = _("Mark/Unmark this device as trusted")

        if not row["blocked"]:
            item = create_menuitem(_("_Block"), "blueman-block-symbolic")
            item.connect("activate", lambda x: self.Blueman.toggle_blocked(self.SelectedDevice))
            self.append(item)
            item.show()
        else:
            item = create_menuitem(_("_Unblock"), "blueman-block-symbolic")
            self.append(item)
            item.connect("activate", lambda x: self.Blueman.toggle_blocked(self.SelectedDevice))
            item.show()
        item.props.tooltip_text = _("Block/Unblock this device")

        def on_rename(_item: Gtk.MenuItem, device: Device) -> None:
            def on_response(dialog: Gtk.Dialog, response_id: int) -> None:
                if response_id == Gtk.ResponseType.ACCEPT:
                    assert isinstance(alias_entry, Gtk.Entry)  # https://github.com/python/mypy/issues/2608
                    device.set('Alias', alias_entry.get_text())
                elif response_id == 1:
                    device.set('Alias', '')
                dialog.destroy()

            builder = Builder("rename-device.ui")
            dialog = builder.get_widget("dialog", Gtk.Dialog)
            dialog.set_transient_for(self.Blueman.window)
            dialog.props.icon_name = "blueman"
            alias_entry = builder.get_widget("alias_entry", Gtk.Entry)
            alias_entry.set_text(device['Alias'])
            dialog.connect("response", on_response)
            dialog.present()

        item = Gtk.MenuItem.new_with_mnemonic(_("R_ename device…"))
        item.connect('activate', on_rename, self.SelectedDevice)
        self.append(item)
        item.show()

        item = Gtk.SeparatorMenuItem()
        item.show()
        self.append(item)

        item = create_menuitem(_("_Remove…"), "list-remove-symbolic")
        item.connect("activate", lambda x: self.Blueman.remove(self.SelectedDevice))
        self.append(item)
        item.show()
        item.props.tooltip_text = _("Remove this device from the known devices list")

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

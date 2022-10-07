import errno
import logging
from enum import Enum, auto
from gettext import gettext as _
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING, Union, Iterable, Callable

from blueman.Functions import create_menuitem, e_
from blueman.bluez.Network import AnyNetwork
from blueman.bluez.Device import AnyDevice, Device
from blueman.config.AutoConnectConfig import AutoConnectConfig
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.main.Builder import Builder
from blueman.main.DBusProxies import AppletService, DBusProxyFailed
from blueman.gui.MessageArea import MessageArea
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
    def on_request_menu_items(self, manager_menu: "ManagerDeviceMenu", device: Device) -> List[DeviceMenuItem]:
        ...


class ManagerDeviceMenu(Gtk.Menu):
    __ops__: Dict[str, str] = {}
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
            if not hasattr(inst, "SelectedDevice"):
                return
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
            if not hasattr(inst, "SelectedDevice"):
                return
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

            MessageArea.close()

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

        def connect(error_handler: Callable[[AppletService, GLib.Error, None], None]) -> None:
            assert self._appl is not None  # https://github.com/python/mypy/issues/2608
            self._appl.ConnectService('(os)', device.get_object_path(), uuid,
                                      result_handler=success, error_handler=error_handler,
                                      timeout=GLib.MAXINT)

        def initial_error_handler(obj: AppletService, result: GLib.Error, user_date: None) -> None:
            # There are (Intel) drivers that fail to connect while a discovery is running
            if self._get_errno(result) == errno.EAGAIN:
                assert self.Blueman.List.Adapter is not None
                self.Blueman.List.Adapter.stop_discovery()
                connect(fail)
            else:
                fail(obj, result, user_date)

        connect(initial_error_handler)

        prog.start()

    def disconnect_service(self, device: Device, uuid: str = GENERIC_CONNECT, port: int = 0) -> None:
        def ok(_obj: AppletService, _result: None, _user_date: None) -> None:
            logging.info("disconnect success")
            self.generate()

        def err(_obj: Optional[AppletService], result: GLib.Error, _user_date: None) -> None:
            logging.warning(f"disconnect failed {result}")
            msg, tb = e_(result.message)
            MessageArea.show_message(_("Disconnection Failed: ") + msg, tb)
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
        err = self._get_errno(error)

        if err == errno.ENOPROTOOPT:
            logging.warning("No audio endpoints registered to bluetoothd. "
                            "Pulseaudio Bluetooth module, bluez-alsa, PipeWire or other audio support missing.")
            msg = _("No audio endpoints registered")
        elif err == errno.EIO:
            logging.warning("bluetoothd reported input/output error. Check its logs for context.")
            msg = _("Input/output error")
        elif err == errno.EHOSTDOWN:
            msg = _("Device did not respond")
        elif err == errno.EAGAIN:
            logging.warning("bluetoothd reported resource temporarily unavailable. "
                            "Retry or check its logs for context.")
            msg = _("Resource temporarily unavailable")
        else:
            msg = error.message.split(":", 3)[-1].strip()

        if msg != "Cancelled":
            MessageArea.show_message(_("Connection Failed: ") + msg)

    @staticmethod
    def _get_errno(error: GLib.Error) -> Optional[int]:
        msg = error.message.split(":", 3)[-1].strip()

        # https://sourceware.org/git/?p=glibc.git;a=blob;f=sysdeps/gnu/errlist.h
        # https://git.musl-libc.org/cgit/musl/tree/src/errno/__strerror.h
        # https://git.uclibc.org/uClibc/tree/libc/string/_string_syserrmsgs.c
        if msg == "Protocol not available":
            return errno.ENOPROTOOPT
        if msg in ("Input/output error", "I/O error"):
            return errno.EIO
        if msg == "Host is down":
            # Bluetooth errors 0x04 (Page Timeout) or 0x3c (Advertising Timeout)
            return errno.EHOSTDOWN
        if msg == "Resource temporarily unavailable":
            return errno.EAGAIN

        return None

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
            path = self.Blueman.List.get_path_at_pos(x, y)
            if path is not None:
                assert path[0] is not None
                treepath = self.Blueman.List.filter.convert_path_to_child_path(path[0])
                if treepath is None:
                    raise TypeError("Path should never be None")
                row = self.Blueman.List.get(treepath, "alias", "paired", "connected", "trusted", "objpush", "device",
                                            "blocked")
            else:
                return

        self.SelectedDevice = row["device"]

        op = self.get_op(self.SelectedDevice)

        if op is not None:
            item: Gtk.MenuItem = create_menuitem(op, "network-transmit-receive-symbolic")
            item.props.sensitive = False
            item.show()
            self.append(item)
            return

        show_generic_connect = self.show_generic_connect_calc(self.SelectedDevice['UUIDs'])

        if not row["connected"] and show_generic_connect:
            connect_item = create_menuitem(_("<b>_Connect</b>"), "bluetooth-symbolic")
            connect_item.connect("activate", lambda _item: self.connect_service(self.SelectedDevice))
            connect_item.props.tooltip_text = _("Connects auto connect profiles A2DP source, A2DP sink, and HID")
            connect_item.show()
            self.append(connect_item)
        elif show_generic_connect:
            connect_item = create_menuitem(_("<b>_Disconnect</b>"), "bluetooth-disabled-symbolic")
            connect_item.props.tooltip_text = _("Forcefully disconnect the device")
            connect_item.connect("activate", lambda _item: self.disconnect_service(self.SelectedDevice))
            connect_item.show()
            self.append(connect_item)

        logging.debug(row["alias"])

        items = [item for plugin in self.Blueman.Plugins.get_loaded_plugins(MenuItemsProvider)
                 for item in plugin.on_request_menu_items(self, self.SelectedDevice)]

        connect_items = [i for i in items if i.group == DeviceMenuItem.Group.CONNECT]
        disconnect_items = [i for i in items if i.group == DeviceMenuItem.Group.DISCONNECT]
        autoconnect_items = [item for item in items if item.group == DeviceMenuItem.Group.AUTOCONNECT]
        action_items = [i for i in items if i.group == DeviceMenuItem.Group.ACTIONS]

        if connect_items:
            self.append(self._create_header(_("<b>Connect To:</b>")))
            for it in sorted(connect_items, key=lambda i: i.position):
                self.append(it.item)

        if disconnect_items:
            self.append(self._create_header(_("<b>Disconnect:</b>")))
            for it in sorted(disconnect_items, key=lambda i: i.position):
                self.append(it.item)

        config = AutoConnectConfig()
        generic_service = ServiceUUID("00000000-0000-0000-0000-000000000000")
        generic_autoconnect = (self.SelectedDevice.get_object_path(), str(generic_service)) in set(config["services"])

        if row["connected"] or generic_autoconnect or autoconnect_items:
            self.append(self._create_header(_("<b>Auto-connect:</b>")))

            if row["connected"] or generic_autoconnect:
                item = Gtk.CheckMenuItem(label=generic_service.name)
                config.bind_to_menuitem(item, self.SelectedDevice, str(generic_service))
                item.show()
                self.append(item)

            for it in sorted(autoconnect_items, key=lambda i: i.position):
                self.append(it.item)

        if show_generic_connect or connect_items or disconnect_items or autoconnect_items:
            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

        for it in sorted(action_items, key=lambda i: i.position):
            self.append(it.item)

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

import logging
from gettext import gettext as _
from operator import itemgetter
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING, Union, Iterable

from blueman.Functions import create_menuitem, e_
from blueman.Service import Service
from blueman.bluez.Network import AnyNetwork
from blueman.bluez.Device import AnyDevice, Device
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


class MenuItemsProvider:
    def on_request_menu_items(self, manager_menu: "ManagerDeviceMenu",
                              device: Device) -> List[Tuple[Gtk.MenuItem, int]]:
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

    def on_connect(self, _item: Gtk.MenuItem, service: Service) -> None:
        device = service.device

        def success(_obj: AppletService, _result: None, _user_data: None) -> None:
            logging.info("success")
            prog.message(_("Success!"))

            MessageArea.close()

            self.unset_op(device)

        def fail(_obj: Optional[AppletService], result: GLib.Error, _user_data: None) -> None:
            prog.message(_("Failed"))

            self.unset_op(device)
            logging.warning(f"fail {result}")
            msg, tb = e_(result.message)
            MessageArea.show_message(_("Connection Failed: ") + msg, tb)

        self.set_op(device, _("Connecting…"))
        prog = ManagerProgressbar(self.Blueman, False)

        if self._appl is None:
            fail(None, GLib.Error('Applet DBus Service not available'), None)
            return

        self._appl.ConnectService('(os)', device.get_object_path(), service.uuid,
                                  result_handler=success, error_handler=fail,
                                  timeout=GLib.MAXINT)

        prog.start()

    def on_disconnect(self, _item: Gtk.MenuItem, service: Service, port: int = 0) -> None:
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

        self._appl.DisconnectService('(osd)', service.device.get_object_path(), service.uuid, port,
                                     result_handler=ok, error_handler=err)

    def on_device_property_changed(self, lst: "ManagerDeviceList", _device: Device, tree_iter: Gtk.TreeIter,
                                   key_value: Tuple[str, object]) -> None:
        key, value = key_value
        # print "menu:", key, value
        if lst.compare(tree_iter, lst.selected()):
            if key in ("Connected", "UUIDs", "Trusted", "Paired"):
                self.generate()

    def generic_connect(self, _item: Optional[Gtk.MenuItem], device: Device, connect: bool) -> None:
        def fail(_obj: AppletService, result: GLib.Error, _user_data: None) -> None:
            logging.info(f"fail: {result}")
            prog.message(_("Failed"))
            self.unset_op(device)
            msg, tb = e_(result.message)
            MessageArea.show_message(_("Connection Failed: ") + msg)

        def success(_obj: AppletService, _result: None, _user_data: None) -> None:
            logging.info("success")
            prog.message(_("Success!"))
            MessageArea.close()
            self.unset_op(device)

        assert self._appl

        if connect:
            self.set_op(self.SelectedDevice, _("Connecting…"))
            self._appl.ConnectService("(os)",
                                      device.get_object_path(),
                                      '00000000-0000-0000-0000-000000000000',
                                      result_handler=success, error_handler=fail,
                                      timeout=GLib.MAXINT)
        else:
            self.set_op(self.SelectedDevice, _("Disconnecting…"))
            self._appl.DisconnectService("(osd)",
                                         device.get_object_path(),
                                         '00000000-0000-0000-0000-000000000000',
                                         0,
                                         result_handler=success, error_handler=fail,
                                         timeout=GLib.MAXINT)

        prog = ManagerProgressbar(self.Blueman, False)
        prog.start()

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

        items: List[Tuple[int, Gtk.MenuItem]] = []

        if not self.is_popup or self.props.visible:
            selected = self.Blueman.List.selected()
            if not selected:
                return
            row = self.Blueman.List.get(selected, "alias", "paired", "connected", "trusted", "objpush", "device")
        else:
            (x, y) = self.Blueman.List.get_pointer()
            path = self.Blueman.List.get_path_at_pos(x, y)
            if path is not None:
                assert path[0] is not None
                row = self.Blueman.List.get(path[0], "alias", "paired", "connected", "trusted", "objpush", "device")
            else:
                return

        self.SelectedDevice = row["device"]

        op = self.get_op(self.SelectedDevice)

        if op is not None:
            item: Gtk.MenuItem = create_menuitem(op, "network-transmit-receive")
            item.props.sensitive = False
            item.show()
            self.append(item)
            return

        show_generic_connect = self.show_generic_connect_calc(self.SelectedDevice['UUIDs'])

        if not row["connected"] and show_generic_connect:
            connect_item = create_menuitem(_("_<b>Connect</b>"), "blueman")
            connect_item.connect("activate", self.generic_connect, self.SelectedDevice, True)
            connect_item.props.tooltip_text = _("Connects auto connect profiles A2DP source, A2DP sink, and HID")
            connect_item.show()
            self.append(connect_item)
        elif show_generic_connect:
            connect_item = create_menuitem(_("_<b>Disconnect</b>"), "network-offline")
            connect_item.props.tooltip_text = _("Forcefully disconnect the device")
            connect_item.connect("activate", self.generic_connect, self.SelectedDevice, False)
            connect_item.show()
            self.append(connect_item)

        for plugin in self.Blueman.Plugins.get_loaded_plugins(MenuItemsProvider):
            for item, pos in plugin.on_request_menu_items(self, self.SelectedDevice):
                items.append((pos, item))

        logging.debug(row["alias"])

        have_disconnectables = False
        have_connectables = False

        if True in map(lambda x: 100 <= x[0] < 200, items):
            have_disconnectables = True

        if True in map(lambda x: x[0] < 100, items):
            have_connectables = True

        if True in map(lambda x: x[0] >= 200, items) and (have_connectables or have_disconnectables):
            item = Gtk.SeparatorMenuItem()
            item.show()
            items.append((199, item))

        if have_connectables:
            item = Gtk.MenuItem()
            label = Gtk.Label()
            label.set_markup(_("<b>Connect To:</b>"))
            label.props.xalign = 0.0

            label.show()
            item.add(label)
            item.props.sensitive = False
            item.show()
            items.append((0, item))

        if have_disconnectables:
            item = Gtk.MenuItem()
            label = Gtk.Label()
            label.set_markup(_("<b>Disconnect:</b>"))
            label.props.xalign = 0.0

            label.show()
            item.add(label)
            item.props.sensitive = False
            item.show()
            items.append((99, item))

        items.sort(key=itemgetter(0))
        for priority, item in items:
            self.append(item)

        if items:
            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

        del items

        send_item = create_menuitem(_("Send a _File…"), "edit-copy")
        send_item.props.sensitive = False
        self.append(send_item)
        send_item.show()

        if row["objpush"]:
            send_item.connect("activate", lambda x: self.Blueman.send(self.SelectedDevice))
            send_item.props.sensitive = True

        item = Gtk.SeparatorMenuItem()
        item.show()
        self.append(item)

        item = create_menuitem(_("_Pair"), "dialog-password")
        item.props.tooltip_text = _("Create pairing with the device")
        self.append(item)
        item.show()
        if not row["paired"]:
            item.connect("activate", lambda x: self.Blueman.bond(self.SelectedDevice))
        else:
            item.props.sensitive = False

        if not row["trusted"]:
            item = create_menuitem(_("_Trust"), "blueman-trust")
            item.connect("activate", lambda x: self.Blueman.toggle_trust(self.SelectedDevice))
            self.append(item)
            item.show()
        else:
            item = create_menuitem(_("_Untrust"), "blueman-untrust")
            self.append(item)
            item.connect("activate", lambda x: self.Blueman.toggle_trust(self.SelectedDevice))
            item.show()
        item.props.tooltip_text = _("Mark/Unmark this device as trusted")

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

        item = create_menuitem(_("_Remove…"), "edit-delete")
        item.connect("activate", lambda x: self.Blueman.remove(self.SelectedDevice))
        self.append(item)
        item.show()
        item.props.tooltip_text = _("Remove this device from the known devices list")

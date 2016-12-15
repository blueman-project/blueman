# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from locale import bind_textdomain_codeset
from operator import itemgetter
from blueman.Sdp import SERIAL_PORT_SVCLASS_ID, OBEX_OBJPUSH_SVCLASS_ID, OBEX_FILETRANS_SVCLASS_ID
from blueman.Functions import get_icon, composite_icon, create_menuitem, e_
from blueman.bluez.Network import AnyNetwork
from blueman.bluez.Device import AnyDevice
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.main.AppletService import AppletService
from blueman.gui.MessageArea import MessageArea

from blueman.services import SerialPort

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject


def get_x_icon(icon_name, size):
    ic = get_icon(icon_name, size)
    x = get_icon("blueman-x", size)
    pixbuf = composite_icon(ic, [(x, 0, 0, 255)])

    return pixbuf


class ManagerDeviceMenu(Gtk.Menu):
    __ops__ = {}
    __instances__ = []

    def __init__(self, blueman):
        super(ManagerDeviceMenu, self).__init__()
        self.set_name("ManagerDeviceMenu")
        self.Blueman = blueman
        self.SelectedDevice = None

        self.is_popup = False

        self._device_property_changed_signal = self.Blueman.List.connect("device-property-changed",
                                                                         self.on_device_property_changed)
        self._selection_done_signal = None

        ManagerDeviceMenu.__instances__.append(self)

        self._any_network = AnyNetwork()
        self._any_network.connect_signal('property-changed', self._on_service_property_changed)

        self._any_device = AnyDevice()
        self._any_device.connect_signal('property-changed', self._on_service_property_changed)

        try:
            self._appl = AppletService()
        except Exception:
            logging.error("** Failed to connect to applet", exc_info=True)
            self._appl = None

        self.Generate()

    def __del__(self):
        logging.debug("deleting devicemenu")

    def popup(self, *args):
        self.is_popup = True

        if not self._device_property_changed_signal:
            self._device_property_changed_signal = self.Blueman.List.connect("device-property-changed",
                                                                             self.on_device_property_changed)

        if not self._selection_done_signal:
            def disconnectall(x):
                self.disconnect(self._device_property_changed_signal)
                self.disconnect(self._selection_done_signal)

            self._selection_done_signal = self.connect("selection-done", disconnectall)

        self.Generate()

        Gtk.Menu.popup(self, *args)

    def clear(self):
        def each(child, data):
            self.remove(child)
            child.destroy()

        self.foreach(each, None)

    def set_op(self, device, message):
        ManagerDeviceMenu.__ops__[device.get_object_path()] = message
        for inst in ManagerDeviceMenu.__instances__:
            logging.info("op: regenerating instance %s" % inst)
            if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
                inst.Generate()

    def get_op(self, device):
        try:
            return ManagerDeviceMenu.__ops__[device.get_object_path()]
        except KeyError:
            return None

    def unset_op(self, device):
        del ManagerDeviceMenu.__ops__[device.get_object_path()]
        for inst in ManagerDeviceMenu.__instances__:
            logging.info("op: regenerating instance %s" % inst)
            if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
                inst.Generate()

    def _on_service_property_changed(self, _service, key, _value, _path):
        if key == "Connected":
            self.Generate()

    def on_connect(self, _item, service):
        device = service.device

        def success(obj, result, _user_data):
            logging.info("success")
            prog.message(_("Success!"))

            if isinstance(service, SerialPort) and SERIAL_PORT_SVCLASS_ID == service.short_uuid:
                MessageArea.show_message(_("Serial port connected to %s") % result, None, "dialog-information")
            else:
                MessageArea.close()

            self.unset_op(device)

        def fail(obj, result, _user_data):
            prog.message(_("Failed"))

            self.unset_op(device)
            logging.warning("fail %s" % result)
            msg, tb = e_(result.message)
            MessageArea.show_message(_("Connection Failed: ") + msg, tb)

        self.set_op(device, _("Connecting..."))
        prog = ManagerProgressbar(self.Blueman, False)

        if self._appl is None:
            fail(None, GLib.Error('Applet DBus Service not available'), None)
            return

        try:
            self._appl.SetTimeHint(str('(u)'), Gtk.get_current_event_time())
        except Exception as e:
            logging.exception(e)

        self._appl.connect_service(str('(os)'), device.get_object_path(), service.uuid,
                                   result_handler=success, error_handler=fail,
                                   timeout=GLib.MAXINT)

        prog.start()

    def on_disconnect(self, item, service, port=0):
        def ok(obj, result, user_date):
            logging.info("disconnect success")
            self.Generate()

        def err(obj, result, user_date):
            logging.warning("disconnect failed %s" % result)
            msg, tb = e_(result.message)
            MessageArea.show_message(_("Disconnection Failed: ") + msg, tb)
            self.Generate()

        if self._appl is None:
            err(None, GLib.Error('Applet DBus Service not available'), None)
            return

        self._appl.disconnect_service(str('(osd)'), service.device.get_object_path(), service.uuid, port,
                                      result_handler=ok, error_handler=err)

    def on_device_property_changed(self, List, device, tree_iter, key_value):
        key, value = key_value
        # print "menu:", key, value
        if List.compare(tree_iter, List.selected()):
            if key in ("Connected", "UUIDs", "Trusted",  "Paired"):
                self.Generate()

    def Generate(self):
        self.clear()

        items = []

        if not self.is_popup or self.props.visible:
            selected = self.Blueman.List.selected()
            if not selected:
                return
            row = self.Blueman.List.get(selected, "alias", "bonded", "connected", "trusted", "objpush", "device")
        else:
            (x, y) = self.Blueman.List.get_pointer()
            path = self.Blueman.List.get_path_at_pos(x, y)
            if path is not None:
                row = self.Blueman.List.get(path[0], "alias", "bonded", "connected", "trusted", "objpush", "device")
            else:
                return

        self.SelectedDevice = row["device"]

        op = self.get_op(self.SelectedDevice)

        if op is not None:
            item = create_menuitem(op, get_icon("network-transmit-recieve", 16))
            item.props.sensitive = False
            item.show()
            self.append(item)
            return

        rets = self.Blueman.Plugins.Run("on_request_menu_items", self, self.SelectedDevice)

        for ret in rets:
            if ret:
                for (item, pos) in ret:
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

        send_item = create_menuitem(_("Send a _File..."), get_icon("edit-copy", 16))
        send_item.props.sensitive = False
        self.append(send_item)
        send_item.show()

        if row["objpush"]:
            send_item.connect("activate", lambda x: self.Blueman.send(self.SelectedDevice))
            send_item.props.sensitive = True

        item = Gtk.SeparatorMenuItem()
        item.show()
        self.append(item)

        item = create_menuitem(_("_Pair"), get_icon("dialog-password", 16))
        item.props.tooltip_text = _("Create pairing with the device")
        self.append(item)
        item.show()
        if not row["bonded"]:
            item.connect("activate", lambda x: self.Blueman.bond(self.SelectedDevice))
        else:
            item.props.sensitive = False

        if not row["trusted"]:
            item = create_menuitem(_("_Trust"), get_icon("blueman-trust", 16))
            item.connect("activate", lambda x: self.Blueman.toggle_trust(self.SelectedDevice))
            self.append(item)
            item.show()
        else:
            item = create_menuitem(_("_Untrust"), get_icon("blueman-untrust", 16))
            self.append(item)
            item.connect("activate", lambda x: self.Blueman.toggle_trust(self.SelectedDevice))
            item.show()
        item.props.tooltip_text = _("Mark/Unmark this device as trusted")

        item = create_menuitem(_("_Setup..."), get_icon("document-properties", 16))
        self.append(item)
        item.connect("activate", lambda x: self.Blueman.setup(self.SelectedDevice))
        item.show()
        item.props.tooltip_text = _("Run the setup assistant for this device")

        def on_rename(_item, device):
            def on_response(dialog, response_id):
                if response_id == Gtk.ResponseType.ACCEPT:
                    device.set('Alias', alias_entry.get_text())
                elif response_id == 1:
                    device.set('Alias', '')
                dialog.destroy()

            builder = Gtk.Builder()
            builder.set_translation_domain("blueman")
            bind_textdomain_codeset("blueman", "UTF-8")
            builder.add_from_file(UI_PATH + "/rename-device.ui")
            dialog = builder.get_object("dialog")
            dialog.set_transient_for(self.Blueman)
            dialog.props.icon_name = "blueman"
            alias_entry = builder.get_object("alias_entry")
            alias_entry.set_text(device['Alias'])
            dialog.connect("response", on_response)
            dialog.present()

        item = Gtk.MenuItem.new_with_mnemonic("R_ename device...")
        item.connect('activate', on_rename, self.SelectedDevice)
        self.append(item)
        item.show()

        item = Gtk.SeparatorMenuItem()
        item.show()
        self.append(item)

        item = create_menuitem(_("_Remove..."), get_icon("edit-delete", 16))
        item.connect("activate", lambda x: self.Blueman.remove(self.SelectedDevice))
        self.append(item)
        item.show()
        item.props.tooltip_text = _("Remove this device from the known devices list")

        item = Gtk.SeparatorMenuItem()
        item.show()
        self.append(item)

        item = create_menuitem(_("_Disconnect"), get_icon("network-offline", 16))
        item.props.tooltip_text = _("Forcefully disconnect the device")

        self.append(item)
        item.show()

        def on_disconnect(item):
            def finished(*args):
                self.unset_op(self.SelectedDevice)
                
            self.set_op(self.SelectedDevice, _("Disconnecting..."))
            self.Blueman.disconnect(self.SelectedDevice,
                                    result_handler=finished,
                                    error_handler=finished)

        if row['connected']:
            item.connect("activate", on_disconnect)

        else:
            item.props.sensitive = False

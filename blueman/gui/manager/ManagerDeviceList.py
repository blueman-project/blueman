from gettext import gettext as _
from typing import Optional, TYPE_CHECKING, List, Any, cast, Callable, Set, Dict
import html
import logging
import cairo
import os

from blueman.bluez.Battery import Battery
from blueman.bluez.Device import Device
from blueman.bluez.Manager import Manager
from blueman.gui.DeviceList import DeviceList
from blueman.DeviceClass import get_minor_class, get_major_class, gatt_appearance_to_name
from blueman.gui.GenericList import ListDataDict
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.Constants import PIXMAP_PATH
from blueman.Functions import launch
from blueman.Sdp import ServiceUUID, OBEX_OBJPUSH_SVCLASS_ID
from blueman.gui.GtkAnimation import TreeRowFade, CellFade, AnimBase
from blueman.main.Config import Config
from _blueman import ConnInfoReadError, conn_info

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Pango

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerDeviceList(DeviceList):
    def __init__(self, adapter: Optional[str] = None, inst: Optional["Blueman"] = None) -> None:
        cr = Gtk.CellRendererText()
        cr.props.ellipsize = Pango.EllipsizeMode.END
        tabledata: List[ListDataDict] = [
            # device picture
            {"id": "device_surface", "type": str, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {}, "celldata_func": (self._set_cell_data, None)},
            # device caption
            {"id": "caption", "type": str, "renderer": cr,
             "render_attrs": {"markup": 1}, "view_props": {"expand": True}},
            {"id": "battery_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {}, "view_props": {"spacing": 0},
             "celldata_func": (self._set_cell_data, "battery")},
            {"id": "rssi_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {}, "view_props": {"spacing": 0},
             "celldata_func": (self._set_cell_data, "rssi")},
            {"id": "lq_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {}, "view_props": {"spacing": 0},
             "celldata_func": (self._set_cell_data, "lq")},
            {"id": "tpl_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {}, "view_props": {"spacing": 0},
             "celldata_func": (self._set_cell_data, "tpl")},
            {"id": "alias", "type": str},  # used for quick access instead of device.GetProperties
            {"id": "connected", "type": bool},  # used for quick access instead of device.GetProperties
            {"id": "paired", "type": bool},  # used for quick access instead of device.GetProperties
            {"id": "trusted", "type": bool},  # used for quick access instead of device.GetProperties
            {"id": "objpush", "type": bool},  # used to set Send File button
            {"id": "battery", "type": float},
            {"id": "rssi", "type": float},
            {"id": "lq", "type": float},
            {"id": "tpl", "type": float},
            {"id": "icon_info", "type": Gtk.IconInfo},
            {"id": "cell_fader", "type": CellFade},
            {"id": "row_fader", "type": TreeRowFade},
            {"id": "initial_anim", "type": bool},
            {"id": "blocked", "type": bool}
        ]
        super().__init__(adapter, tabledata)
        self.set_name("ManagerDeviceList")
        self.set_headers_visible(False)
        self.props.has_tooltip = True
        self.Blueman = inst

        self._monitored_devices: Set[str] = set()

        self.manager.connect_signal("battery-created", self.on_battery_created)
        self.manager.connect_signal("battery-removed", self.on_battery_removed)
        self._batteries: Dict[str, Battery] = {}

        self.Config = Config("org.blueman.general")
        self.Config.connect('changed', self._on_settings_changed)
        # Set the correct sorting
        self._on_settings_changed(self.Config, "sort-by")
        self._on_settings_changed(self.Config, "sort-type")

        self.connect("query-tooltip", self.tooltip_query)
        self.tooltip_row: Optional[Gtk.TreePath] = None
        self.tooltip_col: Optional[Gtk.TreeViewColumn] = None

        self.connect("popup-menu", self._on_popup_menu)
        self.connect("button_press_event", self.on_event_clicked)
        self.connect("button_release_event", self.on_event_clicked)

        self.menu: Optional[ManagerDeviceMenu] = None

        self.connect("drag_data_received", self.drag_recv)
        self.connect("drag-motion", self.drag_motion)

        Gtk.Widget.drag_dest_set(self, Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY | Gdk.DragAction.DEFAULT)
        Gtk.Widget.drag_dest_add_uri_targets(self)

        self.set_search_equal_func(self.search_func)
        self.filter.set_visible_func(self.filter_func)

    def _on_settings_changed(self, settings: Config, key: str) -> None:
        if key in ('sort-by', 'sort-order'):
            sort_by = settings['sort-by']
            sort_order = settings['sort-order']

            if sort_order == 'ascending':
                sort_type = Gtk.SortType.ASCENDING
            else:
                sort_type = Gtk.SortType.DESCENDING

            column_id = self.ids.get(sort_by)

            if column_id:
                self.liststore.set_sort_column_id(column_id, sort_type)

    def on_icon_theme_changed(self, _icon_them: Gtk.IconTheme) -> None:
        for row in self.liststore:
            device = self.get(row.iter, "device")["device"]
            self.row_setup_event(row.iter, device)

    def on_battery_created(self, _manager: Manager, obj_path: str) -> None:
        if obj_path not in self._batteries:
            battery_proxy = Battery(obj_path=obj_path)
            self._batteries[obj_path] = battery_proxy
            logging.debug(f"{obj_path} {battery_proxy['Percentage']}")

    def on_battery_removed(self, _manager: Manager, obj_path: str) -> None:
        if obj_path in self._batteries:
            battery = self._batteries.pop(obj_path)
            battery.destroy()

    def search_func(self, model: Gtk.TreeModel, column: int, key: str, tree_iter: Gtk.TreeIter) -> bool:
        row = self.get(tree_iter, "caption")
        if key.lower() in row["caption"].lower():
            return False
        logging.info(f"{model} {column} {key} {tree_iter}")
        return True

    def filter_func(self, _model: Gtk.TreeModel, tree_iter: Gtk.TreeIter, _data: Any) -> bool:
        no_name = self.get(tree_iter, "no_name")["no_name"]
        if no_name and self.Config["hide-unnamed"]:
            logging.debug("Hiding unnamed device")
            return False
        else:
            return True

    def drag_recv(self, _widget: Gtk.Widget, context: Gdk.DragContext, x: int, y: int, selection: Gtk.SelectionData,
                  _info: int, time: int) -> None:

        uris = list(selection.get_uris())

        context.finish(True, False, time)

        path = self.get_path_at_pos(x, y)
        if path:
            tree_iter = self.get_iter(path[0])
            assert tree_iter is not None
            device = self.get(tree_iter, "device")["device"]
            command = f"blueman-sendto --device={device['Address']}"

            launch(command, paths=uris, name=_("File Sender"))
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

    def drag_motion(self, _widget: Gtk.Widget, drag_context: Gdk.DragContext, x: int, y: int, timestamp: int) -> bool:
        result = self.get_path_at_pos(x, y)
        if result is not None:
            path = result[0]
            assert path is not None
            path = self.filter.convert_path_to_child_path(path)
            if path is None:
                return False

            if not self.selection.path_is_selected(path):
                tree_iter = self.get_iter(path)
                assert tree_iter is not None
                has_obj_push = self._has_objpush(self.get(tree_iter, "device")["device"])
                if has_obj_push:
                    Gdk.drag_status(drag_context, Gdk.DragAction.COPY, timestamp)
                    self.set_cursor(path)
                    return True
                else:
                    Gdk.drag_status(drag_context, Gdk.DragAction.DEFAULT, timestamp)
                    return False
            return False
        else:
            Gdk.drag_status(drag_context, Gdk.DragAction.DEFAULT, timestamp)
            return False

    def _on_popup_menu(self, _widget: Gtk.Widget) -> bool:
        if self.Blueman is None:
            return False

        if self.menu is None:
            self.menu = ManagerDeviceMenu(self.Blueman)

        window = self.get_window()
        assert window is not None
        selected = self.selected()
        assert selected is not None
        rect = self.get_cell_area(self.liststore.get_path(selected), self.get_column(1))
        self.menu.popup_at_rect(window, rect, Gdk.Gravity.CENTER, Gdk.Gravity.NORTH)

        return True

    def on_event_clicked(self, _widget: Gtk.Widget, event: Gdk.Event) -> bool:
        if event.type not in (Gdk.EventType._2BUTTON_PRESS, Gdk.EventType.BUTTON_PRESS):
            return False

        posdata = self.get_path_at_pos(int(cast(Gdk.EventButton, event).x), int(cast(Gdk.EventButton, event).y))
        if posdata is None:
            return False
        else:
            path = posdata[0]
            assert path is not None

        childpath = self.filter.convert_path_to_child_path(path)
        assert childpath is not None
        row = self.get(childpath, "device", "connected")
        if not row:
            return False

        if self.Blueman is None:
            return False

        if self.menu is None:
            self.menu = ManagerDeviceMenu(self.Blueman)

        if event.type == Gdk.EventType._2BUTTON_PRESS and cast(Gdk.EventButton, event).button == 1:
            if self.menu.show_generic_connect_calc(row["device"]['UUIDs']):
                if row["connected"]:
                    self.menu.disconnect_service(row["device"])
                else:
                    self.menu.connect_service(row["device"])

        if event.type == Gdk.EventType.BUTTON_PRESS and cast(Gdk.EventButton, event).button == 3:
            self.menu.popup_at_pointer(event)

        return False

    def get_icon_info(self, icon_name: str, size: int = 48, fallback: bool = True) -> Optional[Gtk.IconInfo]:
        if icon_name is None and not fallback:
            return None
        elif icon_name is None and fallback:
            icon_name = "image-missing"

        icon_info = self.icon_theme.lookup_icon_for_scale(icon_name, size, self.get_scale_factor(),
                                                          Gtk.IconLookupFlags.FORCE_SIZE)

        return icon_info

    def make_device_icon(self, icon_info: Gtk.IconInfo, is_paired: bool = False, is_trusted: bool = False,
                         is_blocked: bool = False) -> cairo.Surface:
        window = self.get_window()
        scale = self.get_scale_factor()
        target = icon_info.load_surface(window)
        ctx = cairo.Context(target)

        if is_paired:
            _icon_info = self.get_icon_info("blueman-paired-emblem", 16, False)
            assert _icon_info is not None
            paired_surface = _icon_info.load_surface(window)
            ctx.set_source_surface(paired_surface, 1 / scale, 1 / scale)
            ctx.paint_with_alpha(0.8)

        if is_trusted:
            _icon_info = self.get_icon_info("blueman-trusted-emblem", 16, False)
            assert _icon_info is not None
            trusted_surface = _icon_info.load_surface(window)
            assert isinstance(target, cairo.ImageSurface)
            assert isinstance(trusted_surface, cairo.ImageSurface)
            height = target.get_height()
            mini_height = trusted_surface.get_height()
            y = height / scale - mini_height / scale - 1 / scale

            ctx.set_source_surface(trusted_surface, 1 / scale, y)
            ctx.paint_with_alpha(0.8)

        if is_blocked:
            _icon_info = self.get_icon_info("blueman-blocked-emblem", 16, False)
            assert _icon_info is not None
            blocked_surface = _icon_info.load_surface(window)
            assert isinstance(target, cairo.ImageSurface)
            assert isinstance(blocked_surface, cairo.ImageSurface)
            width = target.get_width()
            mini_width = blocked_surface.get_width()
            ctx.set_source_surface(blocked_surface, (width - mini_width - 1) / scale, 1 / scale)
            ctx.paint_with_alpha(0.8)

        return target

    def device_remove_event(self, device: Device) -> None:
        tree_iter = self.find_device(device)
        assert tree_iter is not None

        iter_set, _child_tree_iter = self.filter.convert_child_iter_to_iter(tree_iter)
        if iter_set:
            row_fader = self.get(tree_iter, "row_fader")["row_fader"]
            self._prepare_fader(row_fader, lambda: self.__fader_finished(device))
            row_fader.animate(start=row_fader.get_state(), end=0.0, duration=400)

    def __fader_finished(self, device: Device) -> None:
        super().device_remove_event(device)
        self.emit("device-selected", None, None)

    def device_add_event(self, device: Device) -> None:
        self.add_device(device)

    @staticmethod
    def make_caption(name: str, klass: str, address: str) -> str:
        return "<span size='x-large'>%(0)s</span>\n<span size='small'>%(1)s</span>\n<i>%(2)s</i>" \
               % {"0": html.escape(name), "1": klass, "2": address}

    @staticmethod
    def get_device_class(device: Device) -> str:
        klass = get_minor_class(device['Class'])
        if klass != _("Uncategorized"):
            return klass
        else:
            return get_major_class(device['Class'])

    def row_setup_event(self, tree_iter: Gtk.TreeIter, device: Device) -> None:
        if not self.get(tree_iter, "initial_anim")["initial_anim"]:
            assert self.liststore is not None
            child_path = self.liststore.get_path(tree_iter)
            result = self.filter.convert_child_path_to_path(child_path)

            if child_path is not None:
                cell_fader = CellFade(self, child_path, [2, 3, 4, 5])
                row_fader = TreeRowFade(self, child_path)

                self.set(tree_iter, row_fader=row_fader, cell_fader=cell_fader)

                cell_fader.freeze()

                if result is not None:
                    self._prepare_fader(row_fader).animate(start=0.0, end=1.0, duration=500)
                    self.set(tree_iter, initial_anim=True)
                else:
                    self.set(tree_iter, initial_anim=False)

        has_objpush = self._has_objpush(device)
        klass = get_minor_class(device['Class'])
        # Bluetooth >= 4 devices use Appearance property
        appearance = device["Appearance"]
        if klass != _("Uncategorized") and klass != _("Unknown"):
            description = klass
        elif klass == _("Unknown") and appearance:
            description = gatt_appearance_to_name(appearance)
        else:
            description = get_major_class(device['Class'])

        icon_info = self.get_icon_info(device["Icon"], 48, False)
        caption = self.make_caption(device['Alias'], description, device['Address'])

        self.set(tree_iter, caption=caption, icon_info=icon_info, alias=device['Alias'], objpush=has_objpush)

        try:
            self.row_update_event(tree_iter, "Trusted", device['Trusted'])
        except Exception as e:
            logging.exception(e)
        try:
            self.row_update_event(tree_iter, "Paired", device['Paired'])
        except Exception as e:
            logging.exception(e)
        try:
            self.row_update_event(tree_iter, "Connected", device["Connected"])
        except Exception as e:
            logging.exception(e)
        try:
            self.row_update_event(tree_iter, "Blocked", device["Blocked"])
        except Exception as e:
            logging.exception(e)

        if device["Connected"]:
            self._monitor_power_levels(tree_iter, device)

    def _monitor_power_levels(self, tree_iter: Gtk.TreeIter, device: Device) -> None:
        if device["Address"] in self._monitored_devices:
            return

        assert self.Adapter is not None
        cinfo = conn_info(device["Address"], os.path.basename(self.Adapter.get_object_path()))
        try:
            cinfo.init()
        except ConnInfoReadError:
            logging.warning("Failed to get power levels, probably a LE device.")

        model = self.liststore
        assert isinstance(model, Gtk.TreeModel)
        r = Gtk.TreeRowReference.new(model, model.get_path(tree_iter))
        self._update_power_levels(tree_iter, device, cinfo)
        GLib.timeout_add(1000, self._check_power_levels, r, cinfo, device["Address"])
        self._monitored_devices.add(device["Address"])

    def _check_power_levels(self, row_ref: Gtk.TreeRowReference, cinfo: conn_info, address: str) -> bool:
        if not row_ref.valid():
            logging.warning("stopping monitor (row does not exist)")
            cinfo.deinit()
            self._monitored_devices.remove(address)
            return False

        tree_iter = self.get_iter(row_ref.get_path())
        assert tree_iter is not None

        device = self.get(tree_iter, "device")["device"]

        if device["Connected"]:
            self._update_power_levels(tree_iter, device, cinfo)
            return True
        else:
            cinfo.deinit()
            self._disable_power_levels(tree_iter)
            self._monitored_devices.remove(address)
            return False

    def row_update_event(self, tree_iter: Gtk.TreeIter, key: str, value: Any) -> None:
        logging.info(f"{key} {value}")

        if key == "Trusted":
            if value:
                self.set(tree_iter, trusted=True)
            else:
                self.set(tree_iter, trusted=False)

        elif key == "Paired":
            if value:
                self.set(tree_iter, paired=True)
            else:
                self.set(tree_iter, paired=False)

        elif key == "Alias":
            device = self.get(tree_iter, "device")["device"]
            c = self.make_caption(value, self.get_device_class(device), device['Address'])
            self.set(tree_iter, caption=c, alias=value)

        elif key == "UUIDs":
            device = self.get(tree_iter, "device")["device"]
            has_objpush = self._has_objpush(device)
            self.set(tree_iter, objpush=has_objpush)

        elif key == "Connected":
            self.set(tree_iter, connected=value)

            if value:
                self._monitor_power_levels(tree_iter, self.get(tree_iter, "device")["device"])
            else:
                self._disable_power_levels(tree_iter)
        elif key == "Name":
            self.set(tree_iter, no_name=False)
            self.filter.refilter()

        elif key == "Blocked":
            self.set(tree_iter, blocked=value)

    def _update_power_levels(self, tree_iter: Gtk.TreeIter, device: Device, cinfo: conn_info) -> None:
        row = self.get(tree_iter, "cell_fader", "battery", "rssi", "lq", "tpl")

        bars = {}

        obj_path = device.get_object_path()
        if obj_path in self._batteries:
            bars["battery"] = self._batteries[obj_path]["Percentage"]

        # cinfo init may fail for bluetooth devices version 4 and up
        # FIXME Workaround is horrible and we should show something better
        if cinfo.failed:
            bars.update({"rssi": 100.0, "tpl": 100.0, "lq": 100.0})
        else:
            try:
                bars["rssi"] = max(50 + float(cinfo.get_rssi()) / 127 * 50, 10)
            except ConnInfoReadError:
                bars["rssi"] = 50
            try:
                bars["lq"] = max(float(cinfo.get_lq()) / 255 * 100, 10)
            except ConnInfoReadError:
                bars["lq"] = 10
            try:
                bars["tpl"] = max(50 + float(cinfo.get_tpl()) / 127 * 50, 10)
            except ConnInfoReadError:
                bars["tpl"] = 50

        if row["battery"] == row["rssi"] == row["tpl"] == row["lq"] == 0:
            self._prepare_fader(row["cell_fader"]).animate(start=0.0, end=1.0, duration=400)

        w = 14 * self.get_scale_factor()
        h = 48 * self.get_scale_factor()

        for (name, perc) in bars.items():
            if round(row[name], -1) != round(perc, -1):
                icon_name = f"blueman-{name}-{int(round(perc, -1))}.png"
                icon = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(PIXMAP_PATH, icon_name), w, h, True)
                self.set(tree_iter, **{name: perc, f"{name}_pb": icon})

    def _disable_power_levels(self, tree_iter: Gtk.TreeIter) -> None:
        row = self.get(tree_iter, "cell_fader", "battery", "rssi", "lq", "tpl")
        if row["battery"] == row["rssi"] == row["tpl"] == row["lq"] == 0:
            return

        self.set(tree_iter, battery=0, rssi=0, lq=0, tpl=0)
        self._prepare_fader(row["cell_fader"], lambda: self.set(tree_iter, battery_pb=None, rssi_pb=None, lq_pb=None,
                                                                tpl_pb=None)).animate(start=1.0, end=0.0, duration=400)

    def _prepare_fader(self, fader: AnimBase, callback: Optional[Callable[[], None]] = None) -> AnimBase:
        def on_finished(finished_fader: AnimBase) -> None:
            finished_fader.disconnect(handler)
            finished_fader.freeze()
            if callback:
                callback()

        fader.thaw()
        handler = fader.connect("animation-finished", on_finished)
        return fader

    def tooltip_query(self, _tw: Gtk.Widget, x: int, y: int, _kb: bool, tooltip: Gtk.Tooltip) -> bool:
        path = self.get_path_at_pos(x, y)
        if path is None:
            return False

        if path[0] != self.tooltip_row or path[1] != self.tooltip_col:
            self.tooltip_row = path[0]
            self.tooltip_col = path[1]
            return False

        if path[1] == self.columns["device_surface"]:
            tree_iter = self.get_iter(path[0])
            assert tree_iter is not None

            row = self.get(tree_iter, "trusted", "paired", "blocked")
            trusted = row["trusted"]
            paired = row["paired"]
            blocked = row["blocked"]
            str_list = []
            if trusted:
                str_list.append(_("Trusted"))
            if paired:
                str_list.append(_("Paired"))
            if blocked:
                str_list.append(_("Blocked"))

            text = ", ".join(str_list)
            if text:
                tooltip.set_markup(f"<b>{text}</b>")
            else:
                return False

            self.tooltip_row = path[0]
            self.tooltip_col = path[1]
            return True

        elif path[1] == self.columns["battery_pb"] \
                or path[1] == self.columns["tpl_pb"] \
                or path[1] == self.columns["lq_pb"] \
                or path[1] == self.columns["rssi_pb"]:
            tree_iter = self.get_iter(path[0])
            assert tree_iter is not None

            dt = self.get(tree_iter, "connected")["connected"]
            if not dt:
                return False

            lines = [_("<b>Connected</b>")]

            battery = self.get(tree_iter, "battery")["battery"]
            rssi = self.get(tree_iter, "rssi")["rssi"]
            lq = self.get(tree_iter, "lq")["lq"]
            tpl = self.get(tree_iter, "tpl")["tpl"]

            if battery != 0:
                if path[1] == self.columns["battery_pb"]:
                    lines.append(f"<b>Battery: {int(battery)}%</b>")
                else:
                    lines.append(f"Battery: {int(battery)}%")

            if rssi != 0:
                if rssi < 30:
                    rssi_state = _("Poor")
                elif rssi < 40:
                    rssi_state = _("Sub-optimal")
                elif rssi < 60:
                    rssi_state = _("Optimal")
                elif rssi < 70:
                    rssi_state = _("Much")
                else:
                    rssi_state = _("Too much")

                if path[1] == self.columns["rssi_pb"]:
                    lines.append(_("<b>Received Signal Strength: %(rssi)u%%</b> <i>(%(rssi_state)s)</i>") %
                                 {"rssi": rssi, "rssi_state": rssi_state})
                else:
                    lines.append(_("Received Signal Strength: %(rssi)u%% <i>(%(rssi_state)s)</i>") %
                                 {"rssi": rssi, "rssi_state": rssi_state})

            if lq != 0:
                if path[1] == self.columns["lq_pb"]:
                    lines.append(_("<b>Link Quality: %(lq)u%%</b>") % {"lq": lq})
                else:
                    lines.append(_("Link Quality: %(lq)u%%") % {"lq": lq})

            if tpl != 0:
                if tpl < 30:
                    tpl_state = _("Low")
                elif tpl < 40:
                    tpl_state = _("Sub-optimal")
                elif tpl < 60:
                    tpl_state = _("Optimal")
                elif tpl < 70:
                    tpl_state = _("High")
                else:
                    tpl_state = _("Very High")

                if path[1] == self.columns["tpl_pb"]:
                    lines.append(_("<b>Transmit Power Level: %(tpl)u%%</b> <i>(%(tpl_state)s)</i>") %
                                 {"tpl": tpl, "tpl_state": tpl_state})
                else:
                    lines.append(_("Transmit Power Level: %(tpl)u%% <i>(%(tpl_state)s)</i>") %
                                 {"tpl": tpl, "tpl_state": tpl_state})

            tooltip.set_markup("\n".join(lines))
            self.tooltip_row = path[0]
            self.tooltip_col = path[1]
            return True
        return False

    def _has_objpush(self, device: Device) -> bool:
        if device is None:
            return False

        for uuid in device["UUIDs"]:
            if ServiceUUID(uuid).short_uuid == OBEX_OBJPUSH_SVCLASS_ID:
                return True
        return False

    def _set_cell_data(self, _col: Gtk.TreeViewColumn, cell: Gtk.CellRenderer, model: Gtk.TreeModelFilter,
                       tree_iter: Gtk.TreeIter, data: Optional[str]) -> None:
        tree_iter = model.convert_iter_to_child_iter(tree_iter)
        if data is None:
            row = self.get(tree_iter, "icon_info", "trusted", "paired", "blocked")
            surface = self.make_device_icon(row["icon_info"], row["paired"], row["trusted"], row["blocked"])
            cell.set_property("surface", surface)
        else:
            window = self.get_window()
            scale = self.get_scale_factor()
            pb = self.get(tree_iter, data + "_pb")[data + "_pb"]
            if pb:
                surface = Gdk.cairo_surface_create_from_pixbuf(pb, scale, window)
                cell.set_property("surface", surface)
            else:
                cell.set_property("surface", None)

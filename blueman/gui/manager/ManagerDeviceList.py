# coding=utf-8
from blueman.gui.DeviceList import DeviceList
from blueman.DeviceClass import get_minor_class, get_major_class
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Pango
from blueman.Constants import PIXMAP_PATH
from blueman.Functions import launch, composite_icon
from blueman.Sdp import ServiceUUID, OBEX_OBJPUSH_SVCLASS_ID
import html
import logging

from blueman.gui.GtkAnimation import TreeRowColorFade, TreeRowFade, CellFade
from blueman.main.Config import Config
from _blueman import ConnInfoReadError


class ManagerDeviceList(DeviceList):
    def __init__(self, adapter=None, inst=None):
        cr = Gtk.CellRendererText()
        cr.props.ellipsize = Pango.EllipsizeMode.END
        tabledata = [
            # device picture
            {"id": "device_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {"pixbuf": 0}},
            # device caption
            {"id": "caption", "type": str, "renderer": cr,
             "render_attrs": {"markup": 1}, "view_props": {"expand": True}},
            {"id": "rssi_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {"pixbuf": 2}, "view_props": {"spacing": 0}},
            {"id": "lq_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {"pixbuf": 3}, "view_props": {"spacing": 0}},
            {"id": "tpl_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {"pixbuf": 4}, "view_props": {"spacing": 0}},
            {"id": "alias", "type": str},  # used for quick access instead of device.GetProperties
            {"id": "connected", "type": bool},  # used for quick access instead of device.GetProperties
            {"id": "paired", "type": bool},  # used for quick access instead of device.GetProperties
            {"id": "trusted", "type": bool},  # used for quick access instead of device.GetProperties
            {"id": "objpush", "type": bool},  # used to set Send File button
            {"id": "rssi", "type": float},
            {"id": "lq", "type": float},
            {"id": "tpl", "type": float},
            {"id": "icon_info", "type": Gtk.IconInfo},
            {"id": "cell_fader", "type": GObject.TYPE_PYOBJECT},
            {"id": "row_fader", "type": GObject.TYPE_PYOBJECT},
            {"id": "levels_visible", "type": bool},
            {"id": "initial_anim", "type": bool},
        ]
        super(ManagerDeviceList, self).__init__(adapter, tabledata)
        self.set_name("ManagerDeviceList")
        self.set_headers_visible(False)
        self.props.has_tooltip = True
        self.Blueman = inst

        self.Config = Config("org.blueman.general")
        self.Config.connect('changed', self._on_settings_changed)
        # Set the correct sorting
        self._on_settings_changed(self.Config, "sort-by")
        self._on_settings_changed(self.Config, "sort-type")

        self.connect("query-tooltip", self.tooltip_query)
        self.tooltip_row = None
        self.tooltip_col = None

        self.connect("button_press_event", self.on_event_clicked)
        self.connect("button_release_event", self.on_event_clicked)

        self.menu = None

        self.connect("drag_data_received", self.drag_recv)
        self.connect("drag-motion", self.drag_motion)

        Gtk.Widget.drag_dest_set(self, Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY | Gdk.DragAction.DEFAULT)
        Gtk.Widget.drag_dest_add_uri_targets(self)

        self.set_search_equal_func(self.search_func, None)

    def _on_settings_changed(self, settings, key):
        if key in ('sort-by', 'sort-order'):
            sort_by = settings['sort-by']
            sort_order = settings['sort-order']

            if sort_order == 'ascending':
                sort_type = Gtk.SortType.ASCENDING
            else:
                sort_type = Gtk.SortType.DESCENDING

            column_id = self.ids.setdefault(sort_by, None)

            if column_id:
                self.liststore.set_sort_column_id(column_id, sort_type)

    def on_icon_theme_changed(self, widget):
        for row in self.liststore:
            device = self.get(row.iter, "device")["device"]
            self.row_setup_event(row.iter, device)

    def do_device_found(self, device):
        tree_iter = self.find_device(device)
        if tree_iter:
            anim = TreeRowColorFade(self, self.props.model.get_path(tree_iter), Gdk.RGBA(0, 0, 1, 1))
            anim.animate(start=0.8, end=1.0)

    def search_func(self, model, column, key, tree_iter):
        row = self.get(tree_iter, "caption")
        if key.lower() in row["caption"].lower():
            return False
        logging.info("%s %s %s %s" % (model, column, key, tree_iter))
        return True

    def drag_recv(self, widget, context, x, y, selection, target_type, time):

        uris = list(selection.get_uris())

        context.finish(True, False, time)

        path = self.get_path_at_pos(x, y)
        if path:
            tree_iter = self.get_iter(path[0])
            device = self.get(tree_iter, "device")["device"]
            command = "blueman-sendto --device=%s" % device['Address']

            launch(command, uris, False, "blueman", _("File Sender"))
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

        return True

    def drag_motion(self, widget, drag_context, x, y, timestamp):
        path = self.get_path_at_pos(x, y)
        if path is not None:
            if path[0] != self.selected():
                tree_iter = self.get_iter(path[0])
                device = self.get(tree_iter, "device")["device"]
                found = False
                for uuid in device['UUIDs']:
                    if ServiceUUID(uuid).short_uuid == OBEX_OBJPUSH_SVCLASS_ID:
                        found = True
                        break
                if found:
                    drag_context.drag_status(Gdk.DragAction.COPY, timestamp)
                    self.set_cursor(path[0])
                    return True
                else:
                    drag_context.drag_status(Gdk.DragAction.DEFAULT, timestamp)
                    return False
        else:
            drag_context.drag_status(Gdk.DragAction.DEFAULT, timestamp)
            return False

    def on_event_clicked(self, widget, event):

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            path = self.get_path_at_pos(int(event.x), int(event.y))
            if path is not None:
                row = self.get(path[0], "device")

                if row:
                    if self.Blueman is not None:
                        if self.menu is None:
                            self.menu = ManagerDeviceMenu(self.Blueman)

                        self.menu.popup(None, None, None, None, event.button, event.time)

    def get_icon_info(self, icon_names, size=48, fallback=True):
        logging.debug("Looking up icon(s) %s" % icon_names)
        icon_name = None

        for name in icon_names:
            if self.icon_theme.has_icon(name):
                icon_name = name
                break

        if icon_name is None and not fallback:
            return None
        elif icon_name is None and fallback:
            icon_name = "image-missing"

        icon_info = self.icon_theme.lookup_icon(icon_name, size, Gtk.IconLookupFlags.FORCE_SIZE)

        return icon_info

    def make_device_icon(self, icon_info, is_paired=False, is_trusted=False):
        target = icon_info.load_icon()
        sources = []
        if is_paired:
            icon_info = self.get_icon_info(["dialog-password"], 16, False)
            sources.append((icon_info.load_icon(), 0, 0, 200))

        if is_trusted:
            icon_info = self.get_icon_info(["blueman-trust"], 16, False)
            sources.append((icon_info.load_icon(), 0, 32, 200))

        return composite_icon(target, sources)

    def device_remove_event(self, device, tree_iter):
        row_fader = self.get(tree_iter, "row_fader")["row_fader"]

        def on_finished(fader):

            fader.disconnect(signal)
            fader.freeze()
            super(ManagerDeviceList, self).device_remove_event(device, tree_iter)

        signal = row_fader.connect("animation-finished", on_finished)
        row_fader.thaw()
        self.emit("device-selected", None, None)
        row_fader.animate(start=row_fader.get_state(), end=0.0, duration=400)

    def device_add_event(self, device):
        self.add_device(device)

    def make_caption(self, name, klass, address):
        return "<span size='x-large'>%(0)s</span>\n<span size='small'>%(1)s</span>\n<i>%(2)s</i>" % {"0": html.escape(name), "1": klass.capitalize(), "2": address}

    def get_device_class(self, device):
        klass = get_minor_class(device['Class'])
        if klass != "uncategorized":
            return get_minor_class(device['Class'], True)
        else:
            return get_major_class(device['Class'])

    def row_setup_event(self, tree_iter, device):
        if not self.get(tree_iter, "initial_anim")["initial_anim"]:
            cell_fader = CellFade(self, self.props.model.get_path(tree_iter), [2, 3, 4])
            row_fader = TreeRowFade(self, self.props.model.get_path(tree_iter))

            has_objpush = self._has_objpush(device)

            self.set(tree_iter, row_fader=row_fader, cell_fader=cell_fader, levels_visible=False, objpush=has_objpush)

            cell_fader.freeze()

            def on_finished(fader):
                fader.disconnect(signal)
                fader.freeze()

            signal = row_fader.connect("animation-finished", on_finished)
            row_fader.set_state(0.0)
            row_fader.animate(start=0.0, end=1.0, duration=500)

            self.set(tree_iter, initial_anim=True)

        klass = get_minor_class(device['Class'])
        if klass != "uncategorized":
            icon_names = ["blueman-" + klass.replace(" ", "-").lower(), device["Icon"], "blueman"]
            icon_info = self.get_icon_info(icon_names, 48, False)
            # get translated version
            klass = get_minor_class(device['Class'], True)
        else:
            icon_names = [device["Icon"], "blueman"]
            icon_info = self.get_icon_info(icon_names, 48, False)
            klass = get_major_class(device['Class'])

        name = device['Alias']
        address = device['Address']

        caption = self.make_caption(name, klass, address)

        self.set(tree_iter, caption=caption, icon_info=icon_info, alias=name)

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

    def row_update_event(self, tree_iter, key, value):
        logging.info("%s %s" % (key, value))

        if key == "Trusted":
            row = self.get(tree_iter, "paired", "icon_info")
            if value:
                icon = self.make_device_icon(row["icon_info"], row["paired"], True)
                self.set(tree_iter, device_pb=icon, trusted=True)
            else:
                icon = self.make_device_icon(row["icon_info"], row["paired"], False)
                self.set(tree_iter, device_pb=icon, trusted=False)

        elif key == "Paired":
            row = self.get(tree_iter, "trusted", "icon_info")
            if value:
                icon = self.make_device_icon(row["icon_info"], True, row["trusted"])
                self.set(tree_iter, device_pb=icon, paired=True)
            else:
                icon = self.make_device_icon(row["icon_info"], False, row["trusted"])
                self.set(tree_iter, device_pb=icon, paired=False)

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

    def level_setup_event(self, row_ref, device, cinfo):
        def rnd(value):
            return int(round(value, -1))

        if not row_ref.valid():
            return

        tree_iter = self.get_iter(row_ref.get_path())
        if True:
            if cinfo is not None:
                try:
                    rssi = float(cinfo.get_rssi())
                except ConnInfoReadError:
                    rssi = 0
                try:
                    lq = float(cinfo.get_lq())
                except ConnInfoReadError:
                    lq = 0

                try:
                    tpl = float(cinfo.get_tpl())
                except ConnInfoReadError:
                    tpl = 0

                rssi_perc = 50 + (rssi / 127 / 2 * 100)
                tpl_perc = 50 + (tpl / 127 / 2 * 100)
                lq_perc = lq / 255 * 100

                if lq_perc < 10:
                    lq_perc = 10
                if rssi_perc < 10:
                    rssi_perc = 10
                if tpl_perc < 10:
                    tpl_perc = 10

                row = self.get(tree_iter, "levels_visible", "cell_fader", "rssi", "lq", "tpl")
                if not row["levels_visible"]:
                    logging.info("animating up")
                    self.set(tree_iter, levels_visible=True)
                    fader = row["cell_fader"]
                    fader.thaw()
                    fader.set_state(0.0)
                    fader.animate(start=0.0, end=1.0, duration=400)

                    def on_finished(fader):
                        fader.freeze()
                        fader.disconnect(signal)

                    signal = fader.connect("animation-finished", on_finished)

                if rnd(row["rssi"]) != rnd(rssi_perc):
                    icon = GdkPixbuf.Pixbuf.new_from_file(PIXMAP_PATH + "/blueman-rssi-" + str(rnd(rssi_perc)) + ".png")
                    self.set(tree_iter, rssi_pb=icon)

                if rnd(row["lq"]) != rnd(lq_perc):
                    icon = GdkPixbuf.Pixbuf.new_from_file(PIXMAP_PATH + "/blueman-lq-" + str(rnd(lq_perc)) + ".png")
                    self.set(tree_iter, lq_pb=icon)

                if rnd(row["tpl"]) != rnd(tpl_perc):
                    icon = GdkPixbuf.Pixbuf.new_from_file(PIXMAP_PATH + "/blueman-tpl-" + str(rnd(tpl_perc)) + ".png")
                    self.set(tree_iter, tpl_pb=icon)

                self.set(tree_iter,
                         rssi=rssi_perc,
                         lq=lq_perc,
                         tpl=tpl_perc)
            else:

                row = self.get(tree_iter, "levels_visible", "cell_fader")
                if row["levels_visible"]:
                    logging.info("animating down")
                    self.set(tree_iter, levels_visible=False,
                             rssi=-1,
                             lq=-1,
                             tpl=-1)
                    fader = row["cell_fader"]
                    fader.thaw()
                    fader.set_state(1.0)
                    fader.animate(start=fader.get_state(), end=0.0, duration=400)

                    def on_finished(fader):
                        fader.disconnect(signal)
                        fader.freeze()
                        if row_ref.valid():
                            self.set(tree_iter, rssi_pb=None, lq_pb=None, tpl_pb=None)

                    signal = fader.connect("animation-finished", on_finished)

        else:
            logging.info("invisible")

    def tooltip_query(self, tw, x, y, kb, tooltip):
        path = self.get_path_at_pos(x, y)

        if path is not None:
            if path[0] != self.tooltip_row or path[1] != self.tooltip_col:
                self.tooltip_row = path[0]
                self.tooltip_col = path[1]
                return False

            if path[1] == self.columns["device_pb"]:
                tree_iter = self.get_iter(path[0])

                row = self.get(tree_iter, "trusted", "paired")
                trusted = row["trusted"]
                paired = row["paired"]
                if trusted and paired:
                    tooltip.set_markup(_("<b>Trusted and Paired</b>"))
                elif paired:
                    tooltip.set_markup(_("<b>Paired</b>"))
                elif trusted:
                    tooltip.set_markup(_("<b>Trusted</b>"))
                else:
                    return False

                self.tooltip_row = path[0]
                self.tooltip_col = path[1]
                return True

            if path[1] == self.columns["tpl_pb"] or path[1] == self.columns["lq_pb"] or path[1] == self.columns["rssi_pb"]:
                tree_iter = self.get_iter(path[0])

                dt = self.get(tree_iter, "connected")["connected"]
                if dt:
                    rssi = self.get(tree_iter, "rssi")["rssi"]
                    lq = self.get(tree_iter, "lq")["lq"]
                    tpl = self.get(tree_iter, "tpl")["tpl"]

                    if rssi < 30:
                        rssi_state = _("Poor")

                    if 40 > rssi > 30:
                        rssi_state = _("Sub-optimal")

                    elif 40 < rssi < 60:
                        rssi_state = _("Optimal")

                    elif rssi > 60:
                        rssi_state = _("Much")

                    elif rssi > 70:
                        rssi_state = _("Too much")

                    if tpl < 30:
                        tpl_state = _("Low")

                    if 40 > tpl > 30:
                        tpl_state = _("Sub-optimal")

                    elif tpl > 40 and rssi < 60:
                        tpl_state = _("Optimal")

                    elif tpl > 60:
                        tpl_state = _("High")

                    elif tpl > 70:
                        tpl_state = _("Very High")

                    if path[1] == self.columns["tpl_pb"]:
                        tooltip.set_markup(_("<b>Connected</b>\nReceived Signal Strength: %(rssi)u%% <i>(%(rssi_state)s)</i>\nLink Quality: %(lq)u%%\n<b>Transmit Power Level: %(tpl)u%%</b> <i>(%(tpl_state)s)</i>") % {"rssi_state": rssi_state, "rssi": rssi, "lq": lq, "tpl": tpl, "tpl_state": tpl_state})
                    elif path[1] == self.columns["lq_pb"]:
                        tooltip.set_markup(_("<b>Connected</b>\nReceived Signal Strength: %(rssi)u%% <i>(%(rssi_state)s)</i>\n<b>Link Quality: %(lq)u%%</b>\nTransmit Power Level: %(tpl)u%% <i>(%(tpl_state)s)</i>") % {"rssi_state": rssi_state, "rssi": rssi, "lq": lq, "tpl": tpl, "tpl_state": tpl_state})
                    elif path[1] == self.columns["rssi_pb"]:
                        tooltip.set_markup(_("<b>Connected</b>\n<b>Received Signal Strength: %(rssi)u%%</b> <i>(%(rssi_state)s)</i>\nLink Quality: %(lq)u%%\nTransmit Power Level: %(tpl)u%% <i>(%(tpl_state)s)</i>") % {"rssi_state": rssi_state, "rssi": rssi, "lq": lq, "tpl": tpl, "tpl_state": tpl_state})

                    self.tooltip_row = path[0]
                    self.tooltip_col = path[1]
                    return True
        return False

    def _has_objpush(self, device):
        if device is None:
            return False

        for uuid in device["UUIDs"]:
            if ServiceUUID(uuid).short_uuid == OBEX_OBJPUSH_SVCLASS_ID:
                return True
        return False

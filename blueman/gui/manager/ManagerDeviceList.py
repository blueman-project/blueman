from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.gui.DeviceList import DeviceList
from blueman.DeviceClass import get_minor_class, get_major_class
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.Sdp import *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Pango
from blueman.Constants import *
from blueman.Functions import *
import cgi

from blueman.gui.GtkAnimation import TreeRowColorFade, TreeRowFade, CellFade


class ManagerDeviceList(DeviceList):
    def __init__(self, adapter=None, inst=None):
        cr = Gtk.CellRendererText()
        cr.props.ellipsize = Pango.EllipsizeMode.END
        data = [
            # device picture
            ["device_pb", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 0}, None],
            # device caption
            ["caption", str, cr, {"markup": 1}, None, {"expand": True}],


            ["rssi_pb", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 2}, None, {"spacing": 0}],
            ["lq_pb", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 3}, None, {"spacing": 0}],
            ["tpl_pb", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 4}, None, {"spacing": 0}],
            # trusted/bonded icons
            # ["tb_icons", 'PyObject', CellRendererPixbufTable(), {"pixbuffs":5}, None],

            ["connected", bool], # used for quick access instead of device.GetProperties
            ["bonded", bool], # used for quick access instead of device.GetProperties
            ["trusted", bool], # used for quick access instead of device.GetProperties
            ["fake", bool], # used for quick access instead of device.GetProperties,
            # fake determines whether device is "discovered" or a real bluez device

            ["rssi", float],
            ["lq", float],
            ["tpl", float],
            ["orig_icon", GdkPixbuf.Pixbuf],
            ["cell_fader", GObject.TYPE_PYOBJECT],
            ["row_fader", GObject.TYPE_PYOBJECT],
            ["levels_visible", bool],
            ["initial_anim", bool],
        ]
        DeviceList.__init__(self, adapter, data)
        self.set_headers_visible(False)
        self.props.has_tooltip = True
        self.Blueman = inst

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

    def do_device_found(self, device):
        iter = self.find_device(device)
        if iter:
            anim = TreeRowColorFade(self, self.props.model.get_path(iter), Gdk.RGBA(0,0,1,1))
            anim.animate(start=0.8, end=1.0)


    def search_func(self, model, column, key, iter):
        row = self.get(iter, "caption")
        if key.lower() in row["caption"].lower():
            return False
        print(model, column, key, iter)
        return True

    def drag_recv(self, widget, context, x, y, selection, target_type, time):

        uris = list(selection.get_uris())

        context.finish(True, False, time)

        path = self.get_path_at_pos(x, y)
        if path:
            iter = self.get_iter(path[0])
            device = self.get(iter, "device")["device"]
            command = "blueman-sendto --device=%s" % device.Address

            launch(command, uris, False, "blueman", _("File Sender"))
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

        return True


    def drag_motion(self, widget, drag_context, x, y, timestamp):
        path = self.get_path_at_pos(x, y)
        if path != None:
            if path[0] != self.selected():
                iter = self.get_iter(path[0])
                device = self.get(iter, "device")["device"]
                if not device.Fake:
                    found = False
                    for uuid in device.UUIDs:
                        uuid16 = uuid128_to_uuid16(uuid)
                        if uuid16 == OBEX_OBJPUSH_SVCLASS_ID:
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
                    drag_context.drag_status(Gdk.DragAction.COPY, timestamp)
                    self.set_cursor(path[0])
                    return True
        else:
            drag_context.drag_status(Gdk.DragAction.DEFAULT, timestamp)
            return False


    def on_event_clicked(self, widget, event):

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            path = self.get_path_at_pos(int(event.x), int(event.y))
            if path != None:
                row = self.get(path[0], "device")

                if row:
                    device = row["device"]
                    if self.Blueman != None:
                        if self.menu == None:
                            self.menu = ManagerDeviceMenu(self.Blueman)

                        self.menu.popup(None, None, None, None, event.button, event.time)


    def get_device_icon(self, klass):
        return get_icon("blueman-" + klass.replace(" ", "-").lower(), 48, "blueman")


    def make_device_icon(self, target, is_bonded=False, is_trusted=False, is_discovered=False, opacity=255):
        if opacity != 255:
            target = opacify_pixbuf(target, opacity)

        sources = []
        if is_bonded:
            sources.append((get_icon("dialog-password", 16), 0, 0, 200))

        if is_trusted:
            sources.append((get_icon("blueman-trust", 16), 0, 32, 200))

        if is_discovered:
            sources.append((get_icon("edit-find", 24), 24, 0, 255))

        return composite_icon(target, sources)


    def device_remove_event(self, device, iter):
        if device.Temp:
            DeviceList.device_remove_event(self, device, iter)
        else:
            row_fader = self.get(iter, "row_fader")["row_fader"]

            def on_finished(fader):

                fader.disconnect(signal)
                fader.freeze()
                DeviceList.device_remove_event(self, device, iter)

            signal = row_fader.connect("animation-finished", on_finished)
            row_fader.thaw()
            self.emit("device-selected", None, None)
            row_fader.animate(start=row_fader.get_state(), end=0.0, duration=400)

    def device_add_event(self, device):
        if device.Fake:
            self.PrependDevice(device)
            GObject.idle_add(self.props.vadjustment.set_value, 0)
            return

        if self.Blueman.Config["latest-last"]:
            self.AppendDevice(device)
        else:
            self.PrependDevice(device)

    def make_caption(self, name, klass, address):
        return "<span size='x-large'>%(0)s</span>\n<span size='small'>%(1)s</span>\n<i>%(2)s</i>" % {"0": cgi.escape(name), "1": klass.capitalize(), "2": address}

    def get_device_class(self, device):
        klass = get_minor_class(device.Class)
        if klass != "uncategorized":
            return get_minor_class(device.Class, True)
        else:
            return get_major_class(device.Class)

    def row_setup_event(self, iter, device):
        if not self.get(iter, "initial_anim")["initial_anim"]:
            cell_fader = CellFade(self, self.props.model.get_path(iter), [2, 3, 4])
            row_fader = TreeRowFade(self, self.props.model.get_path(iter))

            self.set(iter, row_fader=row_fader, cell_fader=cell_fader, levels_visible=False)

            cell_fader.freeze()

            def on_finished(fader):
                fader.disconnect(signal)
                fader.freeze()

            signal = row_fader.connect("animation-finished", on_finished)
            row_fader.set_state(0.0)
            row_fader.animate(start=0.0, end=1.0, duration=500)

            self.set(iter, initial_anim=True)

        klass = get_minor_class(device.Class)
        if klass != "uncategorized":
            icon = self.get_device_icon(klass)
            # get translated version
            klass = get_minor_class(device.Class, True)
        else:
            icon = get_icon(device.Icon, 48, "blueman")
            klass = get_major_class(device.Class)

        name = device.Alias
        address = device.Address

        caption = self.make_caption(name, klass, address)

        # caption = "<span size='x-large'>%(0)s</span>\n<span size='small'>%(1)s</span>\n<i>%(2)s</i>" % {"0":name, "1":klass.capitalize(), "2":address}
        self.set(iter, caption=caption, orig_icon=icon)

        self.row_update_event(iter, "Fake", device.Fake)

        try:
            self.row_update_event(iter, "Trusted", device.Trusted)
        except:
            pass
        try:
            self.row_update_event(iter, "Paired", device.Paired)
        except:
            pass


    def row_update_event(self, iter, key, value):
        dprint("row update event", key, value)

        # this property is only emitted when device is fake
        if key == "RSSI":
            row = self.get(iter, "orig_icon")

            #minimum opacity 90
            #maximum opacity 255
            #rssi at minimum opacity -100
            #rssi at maximum opacity -45
            # y = kx + b
            #solve linear system
            #{ 90 = k * -100 + b
            #{ 255 = k * -45 + b
            # k = 3
            # b = 390
            #and we have a formula for opacity based on rssi :)
            opacity = int(3 * value + 390)
            if opacity > 255:
                opacity = 255
            if opacity < 90:
                opacity = 90
            print("opacity", opacity)
            icon = self.make_device_icon(row["orig_icon"], is_discovered=True, opacity=opacity)
            self.set(iter, device_pb=icon)

        elif key == "Trusted":
            row = self.get(iter, "bonded", "orig_icon")
            if value:
                icon = self.make_device_icon(row["orig_icon"], row["bonded"], True, False)
                self.set(iter, device_pb=icon, trusted=True)
            else:
                icon = self.make_device_icon(row["orig_icon"], row["bonded"], False, False)
                self.set(iter, device_pb=icon, trusted=False)


        elif key == "Paired":
            row = self.get(iter, "trusted", "orig_icon")
            if value:
                icon = self.make_device_icon(row["orig_icon"], True, row["trusted"], False)
                self.set(iter, device_pb=icon, bonded=True)
            else:
                icon = self.make_device_icon(row["orig_icon"], False, row["trusted"], False)
                self.set(iter, device_pb=icon, bonded=False)

        elif key == "Fake":
            row = self.get(iter, "bonded", "trusted", "orig_icon")
            if value:
                icon = self.make_device_icon(row["orig_icon"], False, False, True)
                self.set(iter, device_pb=icon, fake=True)
            else:
                icon = self.make_device_icon(row["orig_icon"], row["bonded"], row["trusted"], False)
                self.set(iter, device_pb=icon, fake=False)

        elif key == "Alias":
            device = self.get(iter, "device")["device"]
            c = self.make_caption(value, self.get_device_class(device), device.Address)
            self.set(iter, caption=c)


    def level_setup_event(self, row_ref, device, cinfo):
        def rnd(value):
            return int(round(value, -1))

        if not row_ref.valid():
            return

        iter = self.get_iter(row_ref.get_path())
        if True:
            if cinfo != None:
                try:
                    rssi = float(cinfo.get_rssi())
                except:
                    rssi = 0
                try:
                    lq = float(cinfo.get_lq())
                except:
                    lq = 0

                try:
                    tpl = float(cinfo.get_tpl())
                except:
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

                row = self.get(iter, "levels_visible", "cell_fader", "rssi", "lq", "tpl")
                if not row["levels_visible"]:
                    dprint("animating up")
                    self.set(iter, levels_visible=True)
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
                    self.set(iter, rssi_pb=icon)

                if rnd(row["lq"]) != rnd(lq_perc):
                    icon = GdkPixbuf.Pixbuf.new_from_file(PIXMAP_PATH + "/blueman-lq-" + str(rnd(lq_perc)) + ".png")
                    self.set(iter, lq_pb=icon)

                if rnd(row["tpl"]) != rnd(tpl_perc):
                    icon = GdkPixbuf.Pixbuf.new_from_file(PIXMAP_PATH + "/blueman-tpl-" + str(rnd(tpl_perc)) + ".png")
                    self.set(iter, tpl_pb=icon)

                self.set(iter,
                         rssi=rssi_perc,
                         lq=lq_perc,
                         tpl=tpl_perc,
                         connected=True)
            else:

                row = self.get(iter, "levels_visible", "cell_fader")
                if row["levels_visible"]:
                    dprint("animating down")
                    self.set(iter, levels_visible=False,
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
                            self.set(iter, rssi_pb=None, lq_pb=None, tpl_pb=None, connected=False)

                    signal = fader.connect("animation-finished", on_finished)


        else:
            dprint("invisible")


    def tooltip_query(self, tw, x, y, kb, tooltip):

        # print args
        #args[4].set_text("test"+str(args[1]))

        path = self.get_path_at_pos(x, y)

        if path is not None:
            if path[0] != self.tooltip_row or path[1] != self.tooltip_col:
                self.tooltip_row = path[0]
                self.tooltip_col = path[1]
                return False

            if path[1] == self.columns["device_pb"]:
                iter = self.get_iter(path[0])

                row = self.get(iter, "trusted", "bonded")
                trusted = row["trusted"]
                bonded = row["bonded"]
                if trusted and bonded:
                    tooltip.set_markup(_("<b>Trusted and Bonded</b>"))
                elif bonded:
                    tooltip.set_markup(_("<b>Bonded</b>"))
                elif trusted:
                    tooltip.set_markup(_("<b>Trusted</b>"))
                else:
                    return False

                self.tooltip_row = path[0]
                self.tooltip_col = path[1]
                return True

            if path[1] == self.columns["tpl_pb"] or path[1] == self.columns["lq_pb"] or path[1] == self.columns["rssi_pb"]:
                iter = self.get_iter(path[0])

                dt = self.get(iter, "connected")["connected"]
                #print dt
                if dt:
                    rssi = self.get(iter, "rssi")["rssi"]
                    lq = self.get(iter, "lq")["lq"]
                    tpl = self.get(iter, "tpl")["tpl"]

                    if rssi < 30:
                        rssi_state = _("Poor")

                    if rssi < 40 and rssi > 30:
                        rssi_state = _("Sub-optimal")

                    elif rssi > 40 and rssi < 60:
                        rssi_state = _("Optimal")

                    elif rssi > 60:
                        rssi_state = _("Much")

                    elif rssi > 70:
                        rssi_state = _("Too much")

                    if tpl < 30:
                        tpl_state = _("Low")

                    if tpl < 40 and tpl > 30:
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

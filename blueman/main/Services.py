# coding=utf-8
import os
import logging
from blueman.gui.GenericList import GenericList
from blueman.Functions import check_single_instance
import blueman.plugins.services
from blueman.plugins.ServicePlugin import ServicePlugin
from blueman.main.Config import Config

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class BluemanServices(Gtk.Dialog):
    def __init__(self):
        super(BluemanServices, self).__init__(title=_("Local Services"))
        self.resize(520, 420)
        self.set_name("BluemanServices")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.props.border_width = 5
        self.props.icon_name = "blueman"

        self.b_apply = self.add_button("_Apply", Gtk.ResponseType.APPLY)
        self.b_apply.props.receives_default = True
        self.b_apply.props.sensitive = False
        self.b_apply.props.use_underline = True

        self.b_close = self.add_button("_Close", Gtk.ResponseType.CLOSE)
        self.b_close.props.use_underline = True

        self.content_area = self.get_content_area()

        self.box = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        self.box.props.vexpand = True
        self.box.props.visible = True

        self.viewport = Gtk.Viewport()
        self.viewport.props.visible = True
        self.viewport.props.width_request = 120

        self.box.add(self.viewport)
        self.content_area.add(self.box)

        self.connect("delete-event", Gtk.main_quit)

        self.Config = Config("org.blueman.general")

        check_single_instance("blueman-services", lambda time: self.Dialog.present_with_time(time))

        data = [
            {"id": "icon_name", "type": str, "renderer": Gtk.CellRendererPixbuf(stock_size=Gtk.IconSize.DND),
             "render_attrs": {"icon_name": 0}},
            {"id": "caption", "type": str, "renderer": Gtk.CellRendererText(), "render_attrs": {"markup": 1},
             "view_props": {"expand": True}},
            {"id": "id", "type": str},
        ]

        ls = GenericList(data)
        ls.props.headers_visible = False

        ls.selection.connect("changed", self.on_selection_changed)
        self.List = ls

        self.viewport.add(ls)
        ls.show()

        self.load_plugins()

        try:
            ls.selection.select_path(self.Config["services-last-item"])
        except:
            ls.selection.select_path(0)

        self.b_apply.connect("clicked", self.on_apply_clicked)
        self.b_close.connect("clicked", Gtk.main_quit)

        self.show()

    def option_changed(self):
        rets = self.plugin_exec("on_query_apply_state")
        show_apply = False
        for ret in rets:
            if ret == -1:
                show_apply = False
                break
            show_apply = show_apply or ret

        self.b_apply.props.sensitive = show_apply

    def load_plugins(self):
        path = os.path.dirname(blueman.plugins.services.__file__)
        plugins = []
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".py") and not (f.endswith(".pyc") or f.endswith("_.py")):
                    plugins.append(f[0:-3])
        plugins.sort()
        logging.info(plugins)
        for plugin in plugins:
            try:
                __import__("blueman.plugins.services.%s" % plugin, None, None, [])
            except ImportError:
                logging.error("Unable to load %s plugin" % plugin, exc_info=True)

        for cls in ServicePlugin.__subclasses__():
            try:
                inst = cls(self)
            except:
                continue
            if not cls.__plugin_info__:
                logging.warning("Invalid plugin info in %s" % plugin)
            else:
                (name, icon) = cls.__plugin_info__
                self.setup_list_item(inst, name, icon)

    def setup_list_item(self, inst, name, icon):
        self.List.append(icon_name=icon, caption=name, id=inst.__class__.__name__)

    # executes a function on all plugin instances
    def plugin_exec(self, func, *args, **kwargs):
        rets = []
        for inst in ServicePlugin.instances:
            if inst._is_loaded:
                ret = getattr(inst, func)(*args, **kwargs)
                rets.append(ret)

        return rets

    def on_apply_clicked(self, button):
        self.plugin_exec("on_apply")
        self.option_changed()

    def set_page(self, pageid):
        logging.info("Set page %s" % pageid)

        if len(ServicePlugin.instances) == 0:
            return
        # set the first item
        if pageid is None:
            pageid = ServicePlugin.instances[0].__class__.__name__
        for inst in ServicePlugin.instances:
            if inst.__class__.__name__ == pageid:
                if not inst._is_loaded:
                    inst.on_load(self.box)
                    inst._is_loaded = True

                inst._on_enter()
            else:
                inst._on_leave()

    def on_selection_changed(self, selection):
        tree_iter = self.List.selected()
        if self.List.get_cursor()[0]:
            # GtkTreePath returns row when used as string
            self.Config["services-last-item"] = int(str(self.List.get_cursor()[0]))
        row = self.List.get(tree_iter, "id")
        rowid = row["id"]

        self.set_page(rowid)

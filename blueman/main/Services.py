from gettext import gettext as _
import os
import logging
import importlib
import signal
from typing import List, Optional

from blueman.gui.GenericList import GenericList, ListDataDict
import blueman.plugins.services
from blueman.plugins.ServicePlugin import ServicePlugin
from blueman.main.Config import Config

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class BluemanServices(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="org.blueman.Services")
        self.window: Optional[Gtk.Window] = None

        def do_quit(_: object) -> bool:
            self.quit()
            return False

        s = GLib.unix_signal_source_new(signal.SIGINT)
        s.set_callback(do_quit)
        s.attach()

    def do_activate(self) -> None:
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self, title=_("Local Services"), icon_name="blueman",
                                                border_width=10)

            self.window.set_position(Gtk.WindowPosition.CENTER)

            grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, visible=True, row_spacing=10)
            self.window.add(grid)

            self.box = Gtk.Box(vexpand=True, visible=True)
            grid.add(self.box)

            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.END, visible=True)
            grid.add(button_box)

            self.b_apply = Gtk.Button(label=_("_Apply"), receives_default=True, use_underline=True,
                                      sensitive=False, visible=True, width_request=80)
            button_box.add(self.b_apply)

            self.viewport = Gtk.Viewport(visible=True, width_request=120)

            self.box.add(self.viewport)

            self.Config = Config("org.blueman.general")

            data: List[ListDataDict] = [
                {"id": "icon_name", "type": str, "renderer": Gtk.CellRendererPixbuf(stock_size=Gtk.IconSize.DND),
                 "render_attrs": {"icon_name": 0}},
                {"id": "caption", "type": str, "renderer": Gtk.CellRendererText(), "render_attrs": {"markup": 1},
                 "view_props": {"expand": True}},
                {"id": "id", "type": str},
            ]

            self.List = ls = GenericList(data, headers_visible=False, visible=True)

            ls.selection.connect("changed", self.on_selection_changed)

            self.viewport.add(ls)

            self.load_plugins()

            ls.selection.select_path(self.Config["services-last-item"])

            self.b_apply.connect("clicked", self.on_apply_clicked)

        self.window.present_with_time(Gtk.get_current_event_time())

    def option_changed(self) -> None:
        rets = [plugin.on_query_apply_state() for plugin in ServicePlugin.instances if plugin._is_loaded]
        show_apply = False
        for ret in rets:
            if ret == -1:
                show_apply = False
                break
            assert isinstance(ret, bool)
            show_apply = show_apply or ret

        self.b_apply.props.sensitive = show_apply

    def load_plugins(self) -> None:
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
                importlib.import_module(f"blueman.plugins.services.{plugin}")
            except ImportError:
                logging.error(f"Unable to load {plugin} plugin", exc_info=True)

        for cls in ServicePlugin.__subclasses__():
            # FIXME this should not fail, if it does its a bug in the plugin
            try:
                inst = cls(self)
            except:  # noqa: E722
                logging.error(f"Failed to create instance of {cls}", exc_info=True)
                continue
            if not cls.__plugin_info__:
                logging.warning(f"Invalid plugin info in {cls}")
            else:
                (name, icon) = cls.__plugin_info__
                self.setup_list_item(inst, name, icon)

    def setup_list_item(self, inst: ServicePlugin, name: str, icon: str) -> None:
        self.List.append(icon_name=icon, caption=name, id=inst.__class__.__name__)

    def on_apply_clicked(self, _button: Gtk.Button) -> None:
        for plugin in ServicePlugin.instances:
            if plugin._is_loaded:
                plugin.on_apply()
        self.option_changed()

    def set_page(self, pageid: str) -> None:
        logging.info(f"Set page {pageid}")

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

    def on_selection_changed(self, _selection: Gtk.TreeSelection) -> None:
        tree_iter = self.List.selected()
        assert tree_iter
        if self.List.get_cursor()[0]:
            # GtkTreePath returns row when used as string
            self.Config["services-last-item"] = int(str(self.List.get_cursor()[0]))
        row = self.List.get(tree_iter, "id")
        rowid = row["id"]

        self.set_page(rowid)

from gettext import gettext as _
import logging
from typing import TYPE_CHECKING, List, Type, Dict

from blueman.gui.GenericList import GenericList, ListDataDict
from blueman.main.Builder import Builder
from blueman.main.PluginManager import PluginManager
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.BasePlugin import Option

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

if TYPE_CHECKING:
    from blueman.main.Applet import BluemanApplet


class SettingsWidget(Gtk.Box):
    def __init__(self, inst: AppletPlugin, orientation: Gtk.Orientation = Gtk.Orientation.VERTICAL) -> None:
        super().__init__(
            name="SettingsWidget",
            orientation=orientation,
            spacing=2
        )
        self.inst = inst

        self.construct_settings()
        self.show_all()

    def construct_settings(self) -> None:
        for k, v in self.inst.__class__.__options__.items():
            if len(v) > 2:

                label = Gtk.Label(label=v["name"])
                label.props.xalign = 0.0

                w = self.get_control_widget(k, v)

                self.pack_start(w, False, False, 0)

                label = Gtk.Label(label="<i >" + v["desc"] + "</i>", wrap=True, use_markup=True, xalign=0.0)
                self.pack_start(label, False, False, 0)

    def handle_change(self, widget: Gtk.Widget, opt: str, params: "Option", prop: str) -> None:
        val = params["type"](getattr(widget.props, prop))
        logging.debug(f"changed {opt} {val}")

        self.inst.set_option(opt, val)

    def get_control_widget(self, opt: str, params: "Option") -> Gtk.Widget:
        if params["type"] == bool:
            c = Gtk.CheckButton(label=params["name"])

            c.props.active = self.inst.get_option(opt)
            c.connect("toggled", self.handle_change, opt, params, "active")
            return c

        elif params["type"] == int:
            b = Gtk.Box(spacing=6)
            label = Gtk.Label(label=params["name"])
            b.pack_start(label, False, False, 0)

            r = Gtk.SpinButton(numeric=True)
            b.pack_start(r, False, False, 6)

            r.set_increments(1, 3)
            r.set_range(params["range"][0], params["range"][1])

            r.props.value = self.inst.get_option(opt)
            r.connect("value-changed", self.handle_change, opt, params, "value")

            return b

        elif params["type"] == str:
            b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            label = Gtk.Label(label=params["name"])
            b.pack_start(label, False, False, 0)

            e = Gtk.Entry()
            b.pack_start(e, False, False, 6)

            e.props.text = self.inst.get_option(opt)
            e.connect("changed", self.handle_change, opt, params, "text")

            return b
        raise ValueError()


class PluginDialog(Gtk.Window):
    def __init__(self, applet: "BluemanApplet") -> None:
        super().__init__(
            title=_("Plugins"),
            icon_name="blueman",
            name="PluginDialog",
            border_width=10,
            default_width=490,
            default_height=380,
            resizable=False,
            visible=False
        )

        self.set_position(Gtk.WindowPosition.CENTER)

        self.applet = applet

        builder = Builder("applet-plugins-widget.ui")

        self.description = builder.get_widget("description", Gtk.Label)

        self.icon = builder.get_widget("icon", Gtk.Image)
        self.author_txt = builder.get_widget("author_txt", Gtk.Label)
        self.depends_hdr = builder.get_widget("depends_hdr", Gtk.Widget)
        self.depends_txt = builder.get_widget("depends_txt", Gtk.Label)
        self.conflicts_hdr = builder.get_widget("conflicts_hdr", Gtk.Widget)
        self.conflicts_txt = builder.get_widget("conflicts_txt", Gtk.Label)
        self.plugin_name = builder.get_widget("name", Gtk.Label)

        self.main_container = builder.get_widget("main_container", Gtk.Bin)
        self.content_grid = builder.get_widget("content", Gtk.Widget)

        self.b_prefs = builder.get_widget("b_prefs", Gtk.ToggleButton)
        self.b_prefs.connect("toggled", self.on_prefs_toggled)

        self.add(builder.get_widget("all", Gtk.Container))

        cr = Gtk.CellRendererToggle()
        cr.connect("toggled", self.on_toggled)

        data: List[ListDataDict] = [
            {"id": "active", "type": bool, "renderer": cr, "render_attrs": {"active": 0, "activatable": 1,
                                                                            "visible": 1}},
            {"id": "activatable", "type": bool},
            {"id": "icon", "type": str, "renderer": Gtk.CellRendererPixbuf(), "render_attrs": {"icon-name": 2}},
            # device caption
            {"id": "desc", "type": str, "renderer": Gtk.CellRendererText(), "render_attrs": {"markup": 3},
             "view_props": {"expand": True}},
            {"id": "name", "type": str},
        ]

        self.list = GenericList(data, headers_visible=False, visible=True)
        self.list.liststore.set_sort_column_id(3, Gtk.SortType.ASCENDING)
        self.list.liststore.set_sort_func(3, self.list_compare_func)

        self.list.selection.connect("changed", self.on_selection_changed)

        plugin_list = builder.get_widget("plugin_list", Gtk.ScrolledWindow)
        plugin_info = builder.get_widget("main_scrolled_window", Gtk.ScrolledWindow)
        plugin_list.add(self.list)

        # Disable overlay scrolling
        if Gtk.get_minor_version() >= 16:
            plugin_list.props.overlay_scrolling = False
            plugin_info.props.overlay_scrolling = False

        self.populate()

        self.sig_a: int = self.applet.Plugins.connect("plugin-loaded", self.plugin_state_changed, True)
        self.sig_b: int = self.applet.Plugins.connect("plugin-unloaded", self.plugin_state_changed, False)
        self.connect("delete-event", self._on_close)

        self.list.set_cursor(0)

    def list_compare_func(self, _treemodel: Gtk.TreeModel, iter1: Gtk.TreeIter, iter2: Gtk.TreeIter, _user_data: object
                          ) -> int:
        a = self.list.get(iter1, "activatable", "name")
        b = self.list.get(iter2, "activatable", "name")

        if (a["activatable"] and b["activatable"]) or (not a["activatable"] and not b["activatable"]):
            if a["name"] == b["name"]:
                return 0
            if a["name"] < b["name"]:
                return -1
            else:
                return 1

        else:
            if a["activatable"] and not b["activatable"]:
                return -1
            elif not a["activatable"] and b["activatable"]:
                return 1
            else:
                return 0

    def _on_close(self, _widget: Gtk.Widget, _event: Gdk.Event) -> bool:
        self.applet.Plugins.disconnect(self.sig_a)
        self.applet.Plugins.disconnect(self.sig_b)
        return False

    def on_selection_changed(self, _selection: Gtk.TreeSelection) -> None:
        tree_iter = self.list.selected()
        assert tree_iter is not None

        name = self.list.get(tree_iter, "name")["name"]
        cls: Type[AppletPlugin] = self.applet.Plugins.get_classes()[name]
        self.plugin_name.props.label = "<b>" + name + "</b>"
        self.icon.props.icon_name = cls.__icon__
        self.author_txt.props.label = cls.__author__
        self.description.props.label = cls.__description__

        if cls.__depends__:
            self.depends_hdr.props.visible = True
            self.depends_txt.props.visible = True
            self.depends_txt.props.label = ", ".join(cls.__depends__)
        else:
            self.depends_hdr.props.visible = False
            self.depends_txt.props.visible = False

        if cls.__conflicts__:
            self.conflicts_hdr.props.visible = True
            self.conflicts_txt.props.visible = True
            self.conflicts_txt.props.label = ", ".join(cls.__conflicts__)
        else:
            self.conflicts_hdr.props.visible = False
            self.conflicts_txt.props.visible = False

        if cls.is_configurable() and name in self.applet.Plugins.get_loaded():
            self.b_prefs.props.sensitive = True
        else:
            self.b_prefs.props.sensitive = False

        self.update_config_widget(cls)

    def on_prefs_toggled(self, _button: Gtk.ToggleButton) -> None:
        tree_iter = self.list.selected()
        assert tree_iter is not None
        name = self.list.get(tree_iter, "name")["name"]
        cls: Type[AppletPlugin] = self.applet.Plugins.get_classes()[name]

        self.update_config_widget(cls)

    def update_config_widget(self, cls: Type[AppletPlugin]) -> None:
        if self.b_prefs.props.active:
            if not cls.is_configurable():
                self.b_prefs.props.active = False
                return

            inst = cls.get_instance()
            if not inst:
                self.b_prefs.props.active = False
            else:
                c = self.main_container.get_child()
                assert c is not None
                self.main_container.remove(c)
                if isinstance(c, SettingsWidget):
                    c.destroy()

                self.main_container.add(SettingsWidget(inst))

        else:
            c = self.main_container.get_child()
            assert c is not None
            self.main_container.remove(c)
            if isinstance(c, SettingsWidget):
                c.destroy()
            self.main_container.add(self.content_grid)

    def populate(self) -> None:
        classes: Dict[str, Type[AppletPlugin]] = self.applet.Plugins.get_classes()
        loaded = self.applet.Plugins.get_loaded()
        for name, cls in classes.items():
            if cls.is_configurable():
                desc = f"<span weight=\"bold\">{name}</span>"
            else:
                desc = name
            self.list.append(active=(name in loaded), icon=cls.__icon__, activatable=cls.__unloadable__, name=name,
                             desc=desc)

    def plugin_state_changed(self, _plugins: PluginManager, name: str, loaded: bool) -> None:
        row = self.list.get_conditional(name=name)
        self.list.set(row[0], active=loaded)

        cls: Type[AppletPlugin] = self.applet.Plugins.get_classes()[name]
        if not loaded:
            self.update_config_widget(cls)
            self.b_prefs.props.sensitive = False
        elif cls.is_configurable():
            self.b_prefs.props.sensitive = True

    def on_toggled(self, _toggle: Gtk.CellRendererToggle, path: str) -> None:
        name = self.list.get(path, "name")["name"]

        deps = self.applet.Plugins.get_dependencies()[name]
        loaded = self.applet.Plugins.get_loaded()
        to_unload = []
        for dep in deps:
            if dep in loaded:
                to_unload.append(dep)

        if to_unload:
            dialog = Gtk.MessageDialog(parent=self, type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
            dialog.props.secondary_use_markup = True
            dialog.props.icon_name = "blueman"
            dialog.props.text = _("Dependency issue")
            dialog.props.secondary_text = \
                _("Plugin <b>\"%(0)s\"</b> depends on <b>%(1)s</b>. Unloading <b>%(1)s</b> will also unload <b>"
                  "\"%(0)s\"</b>.\nProceed?") % {"0": ", ".join(to_unload), "1": name}

            resp = dialog.run()
            if resp != Gtk.ResponseType.YES:
                dialog.destroy()
                return

            dialog.destroy()

        conflicts = self.applet.Plugins.get_conflicts()[name]
        to_unload = []
        for conf in conflicts:
            if conf in loaded:
                to_unload.append(conf)

        if to_unload:
            dialog = Gtk.MessageDialog(parent=self, type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
            dialog.props.secondary_use_markup = True
            dialog.props.icon_name = "blueman"
            dialog.props.text = _("Dependency issue")
            dialog.props.secondary_text = \
                _("Plugin <b>%(0)s</b> conflicts with <b>%(1)s</b>. Loading <b>%(1)s</b> will unload <b>%(0)s</b>."
                  "\nProceed?") % {"0": ", ".join(to_unload), "1": name}

            resp = dialog.run()
            if resp != Gtk.ResponseType.YES:
                dialog.destroy()
                return

            dialog.destroy()

            for p in to_unload:
                self.applet.Plugins.set_config(p, False)

        self.applet.Plugins.set_config(name, name not in self.applet.Plugins.get_loaded())

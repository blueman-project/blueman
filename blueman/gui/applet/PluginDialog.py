from gettext import gettext as _
import logging
from typing import TYPE_CHECKING, cast, TypeVar

from blueman.main.Builder import Builder
from blueman.main.PluginManager import PluginManager
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.BasePlugin import Option, BasePlugin

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GLib, GObject


if TYPE_CHECKING:
    from blueman.main.Applet import BluemanApplet


class PluginItem(GObject.Object):
    __gtype_name__ = "PluginItem"

    class _Props:
        icon_name: str
        plugin_name: str
        description: str
        enabled: bool
        activatable: bool

    props: _Props

    icon_name = GObject.Property(type=str)
    plugin_name = GObject.Property(type=str)
    description = GObject.Property(type=str)
    enabled = GObject.Property(type=bool, default=False)
    activatable = GObject.Property(type=bool, default=False)

    def __init__(self, icon_name: str, plugin_name: str, description: str, enabled: bool, activatable: bool):
        super().__init__()
        self.props.icon_name = icon_name
        self.props.plugin_name = plugin_name
        self.props.description = description
        self.props.enabled = enabled
        self.props.activatable = activatable


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

    def handle_change(self, widget: Gtk.Widget, opt: str, params: Option, prop: str) -> None:
        val = params["type"](getattr(widget.props, prop))
        logging.debug(f"changed {opt} {val}")

        self.inst.set_option(opt, val)

    def get_control_widget(self, opt: str, params: Option) -> Gtk.Widget:
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


class PluginDialog(Gtk.ApplicationWindow):
    def __init__(self, applet: "BluemanApplet") -> None:
        super().__init__(
            application=applet,
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
        self.depends_txt = builder.get_widget("depends_txt", Gtk.Label)
        self.conflicts_txt = builder.get_widget("conflicts_txt", Gtk.Label)
        self.plugin_name = builder.get_widget("name", Gtk.Label)

        self.main_container = builder.get_widget("main_container", Gtk.Bin)
        self.content_grid = builder.get_widget("content", Gtk.Widget)

        self.b_prefs = builder.get_widget("b_prefs", Gtk.ToggleButton)
        self.b_prefs.connect("toggled", self.on_prefs_toggled)

        self.add(builder.get_widget("all", Gtk.Container))

        self.model = Gio.ListStore.new(PluginItem.__gtype__)
        self.listbox = builder.get_widget("plugin_listbox", Gtk.ListBox)
        self.listbox.bind_model(self.model, self._widget_factory)
        self.listbox.connect("row-selected", self._on_row_selected)

        plugin_list = builder.get_widget("plugin_list", Gtk.ScrolledWindow)
        plugin_info = builder.get_widget("main_scrolled_window", Gtk.ScrolledWindow)

        # Disable overlay scrolling
        if Gtk.get_minor_version() >= 16:
            plugin_list.props.overlay_scrolling = False
            plugin_info.props.overlay_scrolling = False

        self.populate()

        self.sig_a: int = self.applet.Plugins.connect("plugin-loaded", self.plugin_state_changed, True)
        self.sig_b: int = self.applet.Plugins.connect("plugin-unloaded", self.plugin_state_changed, False)
        self.connect("delete-event", self._on_close)

        close_action = Gio.SimpleAction.new("close", None)
        close_action.connect("activate", lambda x, y: self.close())

        self.add_action(close_action)

    def _add_plugin_action(self, name: str, state: bool, activatable: bool) -> None:
        logging.debug(f"adding action: {name}")
        action = Gio.SimpleAction.new_stateful(
            name, None, GLib.Variant.new_boolean(state)
        )
        action.set_property("enabled", activatable)
        self.add_action(action)
        action.connect("change-state", self._on_plugin_toggle)

    def _widget_factory(self, item: GObject.Object, _data: object | None = None) -> Gtk.Widget:
        assert isinstance(item, PluginItem)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5, visible=True)

        checkbutton = Gtk.CheckButton(visible=True, sensitive=item.props.activatable)
        box.add(checkbutton)
        checkbutton.set_action_name(f"win.{item.props.plugin_name}")

        self._add_plugin_action(item.props.plugin_name, item.props.enabled, item.props.activatable)
        # Set active after adding action
        checkbutton.set_active(item.props.enabled)

        plugin_im = Gtk.Image(icon_name=item.props.icon_name, visible=True)
        box.add(plugin_im)

        label = Gtk.Label(label=item.props.description, use_markup=True, visible=True)
        box.add(label)
        return box

    def _model_sort_func(self, item1: object | None, item2: object | None, _data: object | None = None) -> int:
        assert isinstance(item1, PluginItem)
        assert isinstance(item2, PluginItem)

        if item1.props.activatable and not item2.props.activatable:
            return -1
        elif not item1.props.activatable and item2.props.activatable:
            return 1

        if item1.props.plugin_name < item2.props.plugin_name:
            return -1
        elif item1.props.plugin_name > item2.props.plugin_name:
            return 1

        return 0

    def _on_plugin_toggle(self, action: Gio.SimpleAction, state: GLib.Variant) -> None:
        action.set_state(state)
        plugin_name = action.get_name()

        deps = self.applet.Plugins.get_dependencies()[plugin_name]
        loaded = self.applet.Plugins.get_loaded()
        to_unload = [dep for dep in deps if dep in loaded]

        if to_unload:
            if not self._ask_unload(
                _("Plugin <b>\"%(0)s\"</b> depends on <b>%(1)s</b>. Unloading <b>%(1)s</b> will also unload <b>"
                  "\"%(0)s\"</b>.\nProceed?") % {"0": ", ".join(to_unload), "1": plugin_name}
            ):
                action.set_state(GLib.Variant.new_boolean(not state))
                return
        else:
            conflicts = self.applet.Plugins.get_conflicts()[plugin_name]
            to_unload = [conf for conf in conflicts if conf in loaded]

            if to_unload and not self._ask_unload(
                _("Plugin <b>%(0)s</b> conflicts with <b>%(1)s</b>. Loading <b>%(1)s</b> will unload <b>%(0)s</b>."
                  "\nProceed?") % {"0": ", ".join(to_unload), "1": plugin_name}
            ):
                action.set_state(GLib.Variant.new_boolean(not state))
                return

        for p in to_unload:
            logging.debug(f"unloading {p}")
            self.applet.Plugins.set_config(p, False)

        self.applet.Plugins.set_config(plugin_name, plugin_name not in self.applet.Plugins.get_loaded())

    def _on_row_selected(self, _lb: Gtk.ListBox, lbrow: Gtk.ListBoxRow) -> None:
        pos = lbrow.get_index()
        item = self.model.get_item(pos)
        assert isinstance(item, PluginItem)

        cls: type[AppletPlugin] = self.applet.Plugins.get_classes()[item.props.plugin_name]
        self.plugin_name.props.label = "<b>" + item.props.plugin_name + "</b>"
        self.icon.props.icon_name = cls.__icon__
        self.author_txt.props.label = cls.__author__
        self.description.props.label = cls.__description__

        if cls.__depends__:
            self.depends_txt.props.label = ", ".join(cls.__depends__)
        else:
            self.depends_txt.props.label = _("No dependencies")

        if cls.__conflicts__:
            self.conflicts_txt.props.label = ", ".join(cls.__conflicts__)
        else:
            self.conflicts_txt.props.label = _("No conflicts")

        if cls.is_configurable() and item.props.plugin_name in self.applet.Plugins.get_loaded():
            self.b_prefs.props.sensitive = True
        else:
            self.b_prefs.props.sensitive = False

        self.update_config_widget(cls)

    def _on_close(self, _widget: Gtk.Widget, _event: Gdk.Event) -> bool:
        self.applet.Plugins.disconnect(self.sig_a)
        self.applet.Plugins.disconnect(self.sig_b)
        return False

    def on_prefs_toggled(self, _button: Gtk.ToggleButton) -> None:
        row = self.listbox.get_selected_row()
        pos = row.get_index()
        item = cast(PluginItem, self.model.get_item(pos))
        cls: type[AppletPlugin] = self.applet.Plugins.get_classes()[item.props.plugin_name]

        self.update_config_widget(cls)

    def update_config_widget(self, cls: type[AppletPlugin]) -> None:
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
        classes: dict[str, type[AppletPlugin]] = self.applet.Plugins.get_classes()
        loaded = self.applet.Plugins.get_loaded()
        for name, cls in classes.items():
            if cls.is_configurable():
                desc = f"<span weight=\"bold\">{name}</span>"
            else:
                desc = name
            plugin_item = PluginItem(cls.__icon__, name, desc, name in loaded, activatable=cls.__unloadable__)
            self.model.insert_sorted(plugin_item, self._model_sort_func)
        self.listbox.select_row(self.listbox.get_row_at_index(0))

    _T = TypeVar("_T", bound=BasePlugin)

    def plugin_state_changed(self, _plugins: PluginManager[_T], name: str, loaded: bool) -> None:
        logging.debug(f"{name} {loaded}")
        action = self.lookup_action(name)
        assert isinstance(action, Gio.SimpleAction)
        action.set_state(GLib.Variant.new_boolean(loaded))

        cls: type[AppletPlugin] = self.applet.Plugins.get_classes()[name]
        if not loaded:
            self.update_config_widget(cls)
            self.b_prefs.props.sensitive = False
        elif cls.is_configurable():
            self.b_prefs.props.sensitive = True

    def _ask_unload(self, text: str) -> bool:
        dialog = Gtk.MessageDialog(parent=self, type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
        dialog.props.secondary_use_markup = True
        dialog.props.icon_name = "blueman"
        dialog.props.text = _("Dependency issue")
        dialog.props.secondary_text = text

        resp = dialog.run()
        dialog.destroy()
        return resp == Gtk.ResponseType.YES

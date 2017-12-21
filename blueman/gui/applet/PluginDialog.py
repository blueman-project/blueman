# coding=utf-8
import weakref
import logging
from locale import bind_textdomain_codeset

from blueman.Constants import *
from blueman.gui.GenericList import GenericList

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class SettingsWidget(Gtk.Box):
    def __init__(self, inst, orientation=Gtk.Orientation.VERTICAL):
        super(SettingsWidget, self).__init__(orientation=orientation)
        self.set_name("SettingsWidget")
        self.inst = inst
        self.props.spacing = 2

        self.construct_settings()
        self.show_all()

    def construct_settings(self):
        for k, v in self.inst.__class__.__options__.items():
            if len(v) > 2:

                label = Gtk.Label(label=v["name"])
                label.props.xalign = 0.0

                w = self.get_control_widget(k, v)
                if "decorator" in v:
                    v["decorator"](self.inst, w, k, v)

                self.pack_start(w, False, False, 0)

                label = Gtk.Label(label="<i >" + v["desc"] + "</i>")
                label.set_line_wrap(True)
                label.props.use_markup = True
                label.props.xalign = 0.0
                self.pack_start(label, False, False, 0)

    def handle_change(self, widget, opt, params, prop):
        val = params["type"](getattr(widget.props, prop))
        logging.debug("changed %s %s" % (opt, val))

        self.inst.set_option(opt, val)

    def get_control_widget(self, opt, params):
        if "widget" in params:
            return params["widget"](self.inst, opt, params)

        elif params["type"] == bool:
            c = Gtk.CheckButton(params["name"])

            c.props.active = self.inst.get_option(opt)
            c.connect("toggled", self.handle_change, opt, params, "active")
            return c

        elif params["type"] == int:
            b = Gtk.Box(Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label(label=params["name"])
            b.pack_start(label, False, False, 0)

            r = Gtk.SpinButton()
            b.pack_start(r, False, False, 6)
            b.props.spacing = 6

            r.set_numeric(True)
            r.set_increments(1, 3)
            r.set_range(params["range"][0], params["range"][1])

            r.props.value = self.inst.get_option(opt)
            r.connect("value-changed", self.handle_change, opt, params, "value")

            return b

        elif params["type"] == str:
            b = Gtk.Box(Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label(label=params["name"])
            b.pack_start(label, False, False, 0)

            e = Gtk.Entry()
            b.pack_start(e, False, False, 6)
            b.props.spacing = 6

            e.props.text = self.inst.get_option(opt)
            e.connect("changed", self.handle_change, opt, params, "text")

            return b


class PluginDialog(Gtk.Dialog):
    def __init__(self, applet):
        super(PluginDialog, self).__init__(buttons=("_Close", Gtk.ResponseType.CLOSE))

        self.set_name("PluginDialog")
        self.applet = applet

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")
        self.Builder.add_from_file(UI_PATH + "/applet-plugins-widget.ui")

        self.set_title(_("Plugins"))
        self.props.icon_name = "blueman"

        self.description = self.Builder.get_object("description")
        self.description.props.wrap = True

        self.icon = self.Builder.get_object("icon")
        self.author_txt = self.Builder.get_object("author_txt")
        self.depends_hdr = self.Builder.get_object("depends_hdr")
        self.depends_txt = self.Builder.get_object("depends_txt")
        self.conflicts_hdr = self.Builder.get_object("conflicts_hdr")
        self.conflicts_txt = self.Builder.get_object("conflicts_txt")
        self.plugin_name = self.Builder.get_object("name")

        self.main_container = self.Builder.get_object("main_container")
        self.content_grid = self.Builder.get_object("content")

        self.b_prefs = self.Builder.get_object("b_prefs")
        self.b_prefs.connect("toggled", self.on_prefs_toggled)

        widget = self.Builder.get_object("all")

        ref = weakref.ref(self)

        self.vbox.pack_start(widget, True, True, 0)

        cr = Gtk.CellRendererToggle()
        cr.connect("toggled", lambda *args: ref() and ref().on_toggled(*args))

        data = [
            {"id": "active", "type": bool, "renderer": cr, "render_attrs": {"active": 0, "activatable": 1, "visible": 1}},
            {"id": "activatable", "type": bool},
            {"id": "icon", "type": str, "renderer": Gtk.CellRendererPixbuf(), "render_attrs": {"icon-name": 2}},
            # device caption
            {"id": "desc", "type": str, "renderer": Gtk.CellRendererText(), "render_attrs": {"markup": 3},
             "view_props": {"expand": True}},
            {"id": "name", "type": str},
        ]

        self.list = GenericList(data)
        # self.sorted = Gtk.TreeModelSort(self.list.liststore)
        self.list.liststore.set_sort_column_id(3, Gtk.SortType.ASCENDING)
        self.list.liststore.set_sort_func(3, self.list_compare_func)

        self.list.selection.connect("changed", lambda *args: ref() and ref().on_selection_changed(*args))

        self.list.props.headers_visible = False
        self.list.show()

        self.props.border_width = 6
        self.resize(490, 380)

        viewport = self.Builder.get_object("viewport")
        viewport.add(self.list)

        sw = self.Builder.get_object("main_scrolled_window")

        # Disable overlay scrolling
        if Gtk.get_minor_version() >= 16:
            viewport.props.overlay_scrolling = False
            sw.props.overlay_scrolling = False

        self.populate()

        self.sig_a = self.applet.Plugins.connect("plugin-loaded", self.plugin_state_changed, True)
        self.sig_b = self.applet.Plugins.connect("plugin-unloaded", self.plugin_state_changed, False)
        self.connect("response", self.on_response)

        self.list.set_cursor(0)

    def list_compare_func(self, treemodel, iter1, iter2, user_data):
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

    def on_response(self, dialog, resp):
        self.applet.Plugins.disconnect(self.sig_a)
        self.applet.Plugins.disconnect(self.sig_b)

    def on_selection_changed(self, selection):
        model, tree_iter = selection.get_selected()

        name = self.list.get(tree_iter, "name")["name"]
        cls = self.applet.Plugins.GetClasses()[name]
        self.plugin_name.props.label = "<b>" + name + "</b>"
        self.icon.props.icon_name = cls.__icon__
        self.author_txt.props.label = cls.__author__ or _("Unspecified")
        self.description.props.label = cls.__description__ or _("Unspecified")

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

        if cls.is_configurable() and name in self.applet.Plugins.GetLoaded():
            self.b_prefs.props.sensitive = True
        else:
            self.b_prefs.props.sensitive = False

        self.update_config_widget(cls)

    def on_prefs_toggled(self, button):
        model, tree_iter = self.list.selection.get_selected()
        name = self.list.get(tree_iter, "name")["name"]
        cls = self.applet.Plugins.GetClasses()[name]

        self.update_config_widget(cls)

    def update_config_widget(self, cls):
        if self.b_prefs.props.active:
            if not cls.is_configurable():
                self.b_prefs.props.active = False
                return

            if not cls.__instance__:
                self.b_prefs.props.active = False
            else:
                c = self.main_container.get_child()
                self.main_container.remove(c)
                if isinstance(c, SettingsWidget):
                    c.destroy()

                self.main_container.add(SettingsWidget(cls.__instance__))

        else:
            c = self.main_container.get_child()
            self.main_container.remove(c)
            if isinstance(c, SettingsWidget):
                c.destroy()
            self.main_container.add(self.content_grid)

    def populate(self):
        classes = self.applet.Plugins.GetClasses()
        loaded = self.applet.Plugins.GetLoaded()
        for name, cls in classes.items():
            if cls.is_configurable():
                desc = "<span weight=\"bold\">%s</span>" % name
            else:
                desc = name
            self.list.append(active=(name in loaded), icon=cls.__icon__, activatable=(cls.__unloadable__), name=name,
                             desc=desc)

    def plugin_state_changed(self, plugins, name, loaded):
        row = self.list.get_conditional(name=name)
        self.list.set(row[0], active=loaded)

        cls = self.applet.Plugins.GetClasses()[name]
        if not loaded:
            self.update_config_widget(cls)
            self.b_prefs.props.sensitive = False
        elif cls.is_configurable():
            self.b_prefs.props.sensitive = True

    def on_toggled(self, cellrenderer, path):
        name = self.list.get(path, "name")["name"]

        deps = self.applet.Plugins.GetDependencies()[name]
        loaded = self.applet.Plugins.GetLoaded()
        to_unload = []
        for dep in deps:
            if dep in loaded:
                to_unload.append(dep)

        if to_unload:
            dialog = Gtk.MessageDialog(self, type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
            dialog.props.secondary_use_markup = True
            dialog.props.icon_name = "blueman"
            dialog.props.text = _("Dependency issue")
            dialog.props.secondary_text = _(
                "Plugin <b>\"%(0)s\"</b> depends on <b>%(1)s</b>. Unloading <b>%(1)s</b> will also unload <b>\"%(0)s\"</b>.\nProceed?") % {
                                          "0": ", ".join(to_unload), "1": name}

            resp = dialog.run()
            if resp != Gtk.ResponseType.YES:
                dialog.destroy()
                return

            dialog.destroy()

        conflicts = self.applet.Plugins.GetConflicts()[name]
        to_unload = []
        for conf in conflicts:
            if conf in loaded:
                to_unload.append(conf)

        if to_unload:
            dialog = Gtk.MessageDialog(self, type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
            dialog.props.secondary_use_markup = True
            dialog.props.icon_name = "blueman"
            dialog.props.text = _("Dependency issue")
            dialog.props.secondary_text = _(
                "Plugin <b>%(0)s</b> conflicts with <b>%(1)s</b>. Loading <b>%(1)s</b> will unload <b>%(0)s</b>.\nProceed?") % {
                                          "0": ", ".join(to_unload), "1": name}

            resp = dialog.run()
            if resp != Gtk.ResponseType.YES:
                dialog.destroy()
                return

            dialog.destroy()

            for p in to_unload:
                self.applet.Plugins.SetConfig(p, False)

        loaded = name in self.applet.Plugins.GetLoaded()
        self.applet.Plugins.SetConfig(name, not loaded)

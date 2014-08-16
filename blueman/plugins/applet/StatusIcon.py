from blueman.main.PluginManager import StopException
from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import Gtk
from gi.repository import GObject


class StatusIcon(AppletPlugin, Gtk.StatusIcon):
    __unloadable__ = False
    __icon__ = "blueman"

    def on_entry_changed(self, entry, ic, image):

        if ic.has_icon(self.get_option("icon")):
            icon = Gtk.STOCK_APPLY
        else:
            icon = Gtk.STOCK_CANCEL

        image.set_from_stock(icon, Gtk.IconSize.LARGE_TOOLBAR)

        if self.timeout:
            GObject.source_remove(self.timeout)

        self.timeout = GObject.timeout_add(1000, lambda: self.IconShouldChange())

    def widget_decorator(self, widget, name, options):
        entry = widget.get_children()[1]
        image = Gtk.Image()

        completion = Gtk.EntryCompletion()
        entry.set_completion(completion)

        liststore = Gtk.ListStore(GObject.TYPE_STRING)

        completion.set_model(liststore)

        completion.set_text_column(0)

        ic = Gtk.IconTheme.get_default()
        icons = ic.list_icons("Applications")
        for i in icons:
            liststore.append([i])

        if ic.has_icon(self.get_option("icon")):
            icon = Gtk.STOCK_APPLY
        else:
            icon = Gtk.STOCK_CANCEL

        image.set_from_stock(icon, Gtk.IconSize.LARGE_TOOLBAR)
        image.show()
        widget.pack_start(image, True, 0, 0)
        entry.connect("changed", self.on_entry_changed, ic, image)

    __options__ = {"icon": {"type": str,
                            "default": "blueman",
                            "name": _("Icon Name"),
                            "desc": _("Custom icon to use for the notification area"),
                            "decorator": widget_decorator
    }
    }

    FORCE_SHOW = 2
    SHOW = 1
    FORCE_HIDE = 0

    def on_load(self, applet):
        GObject.GObject.__init__(self)
        self.lines = {}
        self.pixbuf = None
        self.timeout = None

        #self.connect("size-changed", self.on_status_icon_resized)

        self.SetTextLine(0, _("Bluetooth Enabled"))

        AppletPlugin.add_method(self.on_query_status_icon_visibility)
        AppletPlugin.add_method(self.on_status_icon_query_icon)

        ic = Gtk.IconTheme.get_default()
        ic.connect("changed", self.on_icon_theme_changed)

        self.on_status_icon_resized()

    def on_icon_theme_changed(self, icon_theme):
        self.IconShouldChange()

    def on_power_state_changed(self, manager, state):
        if state:
            self.SetTextLine(0, _("Bluetooth Enabled"))
        else:
            self.SetTextLine(0, _("Bluetooth Disabled"))

        self.QueryVisibility()

    def QueryVisibility(self):

        rets = self.Applet.Plugins.Run("on_query_status_icon_visibility")
        if not StatusIcon.FORCE_HIDE in rets:
            if StatusIcon.FORCE_SHOW in rets:
                self.set_visible(True)
            else:
                if not self.Applet.Manager:
                    self.set_visible(False)
                    return

                try:
                    self.set_visible(self.Applet.Manager.list_adapters())
                except:
                    self.set_visible(False)
        else:
            self.set_visible(False)

    def set_visible(self, visible):
        self.props.visible = visible

    def SetTextLine(self, id, text):
        if text:
            self.lines[id] = text
        else:
            try:
                del self.lines[id]
            except:
                pass

        self.update_tooltip()


    def update_tooltip(self):
        s = ""
        keys = self.lines.keys()
        keys.sort()
        for k in keys:
            s += self.lines[k] + "\n"

        self.props.tooltip_markup = s[:-1]

    def IconShouldChange(self):
        self.on_status_icon_resized()

    def on_adapter_added(self, path):
        self.QueryVisibility()

    def on_adapter_removed(self, path):
        self.QueryVisibility()

    def on_manager_state_changed(self, state):
        self.QueryVisibility()

    def on_status_icon_resized(self):
        self.icon = "blueman"

        #p = GdkPixbuf.Pixbuf(GdkPixbuf.Colorspace.RGB, True, 8, 22, 22)
        #p.fill(0)


        #self.pixbuf.copy_area(0, 0, self.pixbuf.props.width, self.pixbuf.props.height, p, 5, 0)

        #self.pixbuf = p
        ic = Gtk.IconTheme.get_default()

        def callback(inst, ret):
            if ret != None:
                for i in ret:
                    if ic.has_icon(i):
                        self.icon = i
                        raise StopException

        self.Applet.Plugins.RunEx("on_status_icon_query_icon", callback)
        self.props.icon_name = self.icon

        return True

    def on_query_status_icon_visibility(self):
        return StatusIcon.SHOW

    def on_status_icon_query_icon(self):
        return None


from blueman.Functions import dprint
import gtk
import os
from blueman.bluez.Adapter import Adapter
from blueman.Constants import *
from blueman.gui.DeviceSelectorList import DeviceSelectorList


class DeviceSelectorWidget(gtk.VBox):
    def __init__(self, adapter=None):

        gtk.VBox.__init__(self)

        self.props.spacing = 1
        self.set_size_request(360, 340)

        sw = gtk.ScrolledWindow()
        self.List = devlist = DeviceSelectorList(adapter)
        if self.List.Adapter != None:
            self.List.DisplayKnownDevices()

        sw.add(devlist)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_IN)

        self.Builder = gtk.Builder()
        self.Builder.add_from_file(UI_PATH + "/device-list-widget.ui")

        sitem = self.Builder.get_object("search")

        self.cb_adapters = self.Builder.get_object("adapters")

        cell = gtk.CellRendererText()

        self.cb_adapters.pack_start(cell, True)
        self.cb_adapters.connect("changed", self.on_adapter_selected)
        self.cb_adapters.add_attribute(cell, 'text', 0)

        button = self.Builder.get_object("b_search")
        button.connect("clicked", self.on_search_clicked)

        self.pbar = self.Builder.get_object("progressbar1")

        self.List.connect("discovery-progress", self.on_discovery_progress)

        self.pack_start(sw, True)
        self.pack_start(sitem, False)

        sitem.show()

        sw.show_all()

        self.List.connect("adapter-changed", self.on_adapter_changed)
        self.List.connect("adapter-added", self.on_adapter_added)
        self.List.connect("adapter-removed", self.on_adapter_removed)
        self.List.connect("adapter-property-changed", self.on_adapter_prop_changed)

        self.update_adapters_list()

    def __del__(self):
        self.List.destroy()
        dprint("Deleting widget")

    def on_discovery_progress(self, devlist, fraction):
        self.pbar.props.fraction = fraction

    def on_search_clicked(self, button):
        self.List.DiscoverDevices()

    def on_adapter_prop_changed(self, devlist, adapter, (key, value)):
        if key == "Name":
            self.update_adapters_list()
        elif key == "Discovering":
            if not value:
                self.pbar.props.fraction = 0

    def on_adapter_added(self, devlist, adapter_path):
        self.update_adapters_list()

    def on_adapter_removed(self, devlist, adapter_path):
        self.update_adapters_list()

    def on_adapter_selected(self, cb_adapters):
        dprint("selected")
        iter = cb_adapters.get_active_iter()
        if iter:
            adapter_path = cb_adapters.get_model().get_value(iter, 1)
            if self.List.Adapter:
                if self.List.Adapter.GetObjectPath() != adapter_path:
                    self.List.SetAdapter(os.path.basename(adapter_path))

    def on_adapter_changed(self, devlist, adapter_path):
        dprint("changed")
        if adapter_path is None:
            self.update_adapters_list()
        else:
            if self.List.Adapter:
                self.List.DisplayKnownDevices()

    def update_adapters_list(self):

        self.cb_adapters.get_model().clear()
        adapters = self.List.Manager.ListAdapters()
        num = len(adapters)
        if num == 0:
            self.cb_adapters.props.visible = False
            self.List.props.sensitive = False
        elif num == 1:
            self.cb_adapters.props.visible = False
            self.List.props.sensitive = True
        elif num > 1:
            self.List.props.sensitive = True
            self.cb_adapters.props.visible = True
            for adapter in adapters:
                props = adapter.GetProperties()
                name = props["Name"]

                iter = self.cb_adapters.get_model().append([name, adapter.GetObjectPath()])
                if adapter.GetObjectPath() == self.List.Adapter.GetObjectPath():
                    self.cb_adapters.set_active_iter(iter)
		
		
		
		
		

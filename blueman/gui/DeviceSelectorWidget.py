# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os
import logging
from blueman.gui.DeviceSelectorList import DeviceSelectorList


class DeviceSelectorWidget(Gtk.Box):
    def __init__(self, adapter=None, orientation=Gtk.Orientation.VERTICAL):

        super(DeviceSelectorWidget, self).__init__(orientation=orientation, spacing=1, vexpand=True,
                                                   width_request=360, height_request=340,
                                                   name="DeviceSelectorWidget")

        self.List = DeviceSelectorList(adapter)
        if self.List.Adapter is not None:
            self.List.DisplayKnownDevices()

        sw = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER,
                                vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                                shadow_type=Gtk.ShadowType.IN)
        sw.add(self.List)
        self.pack_start(sw, True, True, 0)

        # Disable overlay scrolling
        if Gtk.get_minor_version() >= 16:
            sw.props.overlay_scrolling = False

        self.pbar = Gtk.ProgressBar(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.pbar)

        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, height_request=8)
        self.add(search_box)

        search_btn = Gtk.Button.new_from_icon_name("edit-find", Gtk.IconSize.BUTTON)
        search_btn.set_tooltip_text(_("Search for devices"))
        search_box.add(search_btn)

        model = Gtk.ListStore(str, str)
        cell = Gtk.CellRendererText()
        self.cb_adapters = Gtk.ComboBox(model=model, visible=True)
        self.cb_adapters.set_tooltip_text(_("Adapter selection"))
        self.cb_adapters.pack_start(cell, True)
        self.cb_adapters.add_attribute(cell, 'text', 0)
        search_box.add(self.cb_adapters)

        self.cb_adapters.connect("changed", self.on_adapter_selected)

        search_btn.connect("clicked", self.on_search_clicked)

        self.List.connect("discovery-progress", self.on_discovery_progress)

        self.List.connect("adapter-changed", self.on_adapter_changed)
        self.List.connect("adapter-added", self.on_adapter_added)
        self.List.connect("adapter-removed", self.on_adapter_removed)
        self.List.connect("adapter-property-changed", self.on_adapter_prop_changed)

        self.update_adapters_list()
        self.show_all()

    def __del__(self):
        self.List.destroy()
        logging.debug("Deleting widget")

    def on_discovery_progress(self, devlist, fraction):
        self.pbar.props.fraction = fraction

    def on_search_clicked(self, button):
        self.List.DiscoverDevices()

    def on_adapter_prop_changed(self, devlist, adapter, key_value):
        key, value = key_value
        if key == "Name" or key == "Alias":
            self.update_adapters_list()
        elif key == "Discovering":
            if not value:
                self.pbar.props.fraction = 0

    def on_adapter_added(self, devlist, adapter_path):
        self.update_adapters_list()

    def on_adapter_removed(self, devlist, adapter_path):
        self.update_adapters_list()

    def on_adapter_selected(self, cb_adapters):
        logging.info("selected")
        tree_iter = cb_adapters.get_active_iter()
        if tree_iter:
            adapter_path = cb_adapters.get_model().get_value(tree_iter, 1)
            if self.List.Adapter:
                if self.List.Adapter.get_object_path() != adapter_path:
                    self.List.SetAdapter(os.path.basename(adapter_path))

    def on_adapter_changed(self, devlist, adapter_path):
        logging.info("changed")
        if adapter_path is None:
            self.update_adapters_list()
        else:
            if self.List.Adapter:
                self.List.DisplayKnownDevices()

    def update_adapters_list(self):

        self.cb_adapters.get_model().clear()
        adapters = self.List.manager.get_adapters()
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
                tree_iter = self.cb_adapters.get_model().append([adapter.get_name(), adapter.get_object_path()])
                if adapter.get_object_path() == self.List.Adapter.get_object_path():
                    self.cb_adapters.set_active_iter(tree_iter)

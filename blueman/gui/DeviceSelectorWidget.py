from gettext import gettext as _
import os
import logging
from typing import Optional, Tuple

from blueman.bluez.Adapter import Adapter
from blueman.gui.DeviceSelectorList import DeviceSelectorList

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceSelectorWidget(Gtk.Box):
    def __init__(self, adapter_name: Optional[str] = None, orientation: Gtk.Orientation = Gtk.Orientation.VERTICAL,
                 visible: bool = False) -> None:

        super().__init__(orientation=orientation, spacing=1, vexpand=True,
                         width_request=360, height_request=340,
                         name="DeviceSelectorWidget", visible=visible)

        self.List = DeviceSelectorList(adapter_name)
        if self.List.Adapter is not None:
            self.List.populate_devices()

        sw = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER,
                                vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                                shadow_type=Gtk.ShadowType.IN)
        sw.add(self.List)
        self.pack_start(sw, True, True, 0)

        # Disable overlay scrolling
        if Gtk.get_minor_version() >= 16:
            sw.props.overlay_scrolling = False

        model = Gtk.ListStore(str, str)
        cell = Gtk.CellRendererText()
        self.cb_adapters = Gtk.ComboBox(model=model, visible=True)
        self.cb_adapters.set_tooltip_text(_("Adapter selection"))
        self.cb_adapters.pack_start(cell, True)
        self.cb_adapters.add_attribute(cell, 'text', 0)

        spinner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, height_request=8)
        self.spinner = Gtk.Spinner(halign=Gtk.Align.START, hexpand=True, has_tooltip=True,
                                   tooltip_text=_("Discovering…"), margin=6)

        spinner_box.add(self.cb_adapters)
        spinner_box.add(self.spinner)
        self.add(spinner_box)

        self.cb_adapters.connect("changed", self.on_adapter_selected)

        self.List.connect("adapter-changed", self.on_adapter_changed)
        self.List.connect("adapter-added", self.on_adapter_added)
        self.List.connect("adapter-removed", self.on_adapter_removed)
        self.List.connect("adapter-property-changed", self.on_adapter_prop_changed)

        self.update_adapters_list()
        self.show_all()

    def __del__(self) -> None:
        self.List.destroy()
        logging.debug("Deleting widget")

    def on_adapter_prop_changed(self, _devlist: DeviceSelectorList, adapter: Adapter, key_value: Tuple[str, object]
                                ) -> None:
        key, value = key_value
        if key == "Name" or key == "Alias":
            self.update_adapters_list()
        elif key == "Discovering":
            if not value:
                self.spinner.stop()
            else:
                self.spinner.start()

    def on_adapter_added(self, _devlist: DeviceSelectorList, _adapter_path: str) -> None:
        self.update_adapters_list()

    def on_adapter_removed(self, _devlist: DeviceSelectorList, _adapter_path: str) -> None:
        self.update_adapters_list()

    def on_adapter_selected(self, cb_adapters: Gtk.ComboBox) -> None:
        logging.info("selected")
        tree_iter = cb_adapters.get_active_iter()
        if tree_iter:
            adapter_path = cb_adapters.get_model().get_value(tree_iter, 1)
            if self.List.Adapter:
                if self.List.Adapter.get_object_path() != adapter_path:
                    # Stop discovering on previous adapter
                    self.List.Adapter.stop_discovery()
                    self.List.set_adapter(os.path.basename(adapter_path))
                    # Start discovery on selected adapter
                    self.List.Adapter.start_discovery()

    def on_adapter_changed(self, _devlist: DeviceSelectorList, adapter_path: str) -> None:
        logging.info("changed")
        if adapter_path is None:
            self.update_adapters_list()
        else:
            if self.List.Adapter:
                self.List.populate_devices()

    def update_adapters_list(self) -> None:
        model = self.cb_adapters.get_model()
        assert isinstance(model, Gtk.ListStore)
        model.clear()
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
                tree_iter = model.append([adapter.get_name(), adapter.get_object_path()])
                if self.List.Adapter and adapter.get_object_path() == self.List.Adapter.get_object_path():
                    self.cb_adapters.set_active_iter(tree_iter)

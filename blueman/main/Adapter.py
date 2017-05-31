# coding=utf-8
import os.path
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk
from gi.repository import Pango
import logging

from blueman.Functions import *
import blueman.bluez as Bluez


class BluemanAdapters(Gtk.Dialog):
    def __init__(self, selected_hci_dev, socket_id):
        super(BluemanAdapters, self).__init__(
            title=_("Bluetooth Adapters"),
            border_width=5,
            icon_name="blueman-device",
            window_position=Gtk.WindowPosition.CENTER,
            name="BluemanAdapters"
        )

        self.connect("response", self.on_dialog_response)

        close_button = self.add_button("_Close", Gtk.ResponseType.CLOSE)
        close_button.props.receives_default = True
        close_button.props.use_underline = True

        self.notebook = Gtk.Notebook()
        if socket_id:
            plug = Gtk.Plug.new(socket_id)
            plug.connect('delete-event', lambda _plug, _event: Gtk.main_quit())
            plug.add(self.notebook)
            plug.show()
        else:
            self.get_content_area().add(self.notebook)
            self.show()
        self.tabs = {}
        self._adapters = {}

        setup_icon_path()
        Bluez.Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)

        check_single_instance("blueman-adapters", lambda time: self.present_with_time(time))

        check_bluetooth_status(_("Bluetooth needs to be turned on for the adapter manager to work"), lambda: exit())

        try:
            self.manager = Bluez.Manager()
        except Exception as e:
            logging.exception(e)
            self.manager = None
        #fixme: show error dialog and exit

        self.manager.connect_signal('adapter-added', self.on_adapter_added)
        self.manager.connect_signal('adapter-removed', self.on_adapter_removed)
        for adapter in self.manager.get_adapters():
            path = adapter.get_object_path()
            hci_dev = os.path.basename(path)
            self._adapters[hci_dev] = adapter
            self.on_adapter_added(self.manager, path)

        #activate a particular tab according to command line option
        if selected_hci_dev is not None:
            if selected_hci_dev in self.tabs:
                hci_dev_num = int(selected_hci_dev[3:])
                self.notebook.set_current_page(hci_dev_num)
            else:
                logging.error('Error: the selected adapter does not exist')
        self.notebook.show_all()

    def on_dialog_response(self, dialog, response_id):
        Gtk.main_quit()

    def on_property_changed(self, adapter, name, value, path):
        hci_dev = os.path.basename(path)
        if name == "Discoverable" and value == 0:
            self.tabs[hci_dev]["hidden_radio"].set_active(True)
        elif name == "Alias":
            self.tabs[hci_dev]["label"].set_text(value)

    def on_adapter_added(self, _manager, adapter_path):
        hci_dev = os.path.basename(adapter_path)
        if not hci_dev in self._adapters:
            self._adapters[hci_dev] = Bluez.Adapter(adapter_path)

        self._adapters[hci_dev].connect_signal("property-changed", self.on_property_changed)
        self.add_to_notebook(self._adapters[hci_dev])

    def on_adapter_removed(self, _manager, adapter_path):
        hci_dev = os.path.basename(adapter_path)
        self.remove_from_notebook(self._adapters[hci_dev])

    def _on_dbus_name_appeared(self, _connection, name, owner):
        logging.info("%s %s" % (name, owner))

    def _on_dbus_name_vanished(self, _connection, name):
        logging.info(name)
        self.manager = None
        # FIXME: show error dialog and exit

    def build_adapter_tab(self, adapter):
        def on_toggle(radio, radio_id):
            if not radio.props.active:
                return

            if radio_id == "hidden":
                adapter['DiscoverableTimeout'] = 0
                adapter['Discoverable'] = False
                hscale.set_sensitive(False)

            if radio_id == "always":
                adapter['DiscoverableTimeout'] = 0
                adapter['Discoverable'] = True
                hscale.set_sensitive(False)

            if radio_id == "temporary":
                adapter['Discoverable'] = True
                hscale.set_sensitive(True)
                hscale.set_value(3)

        def on_scale_format_value(scale, value):
            if value == 0:
                if adapter['Discoverable']:
                    return _("Always")
                else:
                    return _("Hidden")
            else:
                return gettext.ngettext("%d Minute", "%d Minutes", value) % (value)

        def on_scale_value_changed(scale):
            val = scale.get_value()
            logging.info('value: %s' % val)
            if val == 0 and adapter['Discoverable']:
                always_radio.props.active = True
            timeout = int(val * 60)
            adapter['DiscoverableTimeout'] = timeout

        def on_name_changed(entry):
            adapter['Alias'] = entry.get_text()

        ui = {}

        grid = Gtk.Grid(row_spacing=2, margin=12, orientation=Gtk.Orientation.VERTICAL)

        visibility_label = Gtk.Label("<b>Visibility Settings</b>", halign=Gtk.Align.START,
                                     use_markup=True)
        grid.add(visibility_label)

        hidden_radio = Gtk.RadioButton.new_with_label(None, "Hidden")
        grid.add(hidden_radio)
        always_radio = Gtk.RadioButton.new_with_label_from_widget(hidden_radio, "Always visible")
        grid.add(always_radio)
        temporary_radio = Gtk.RadioButton.new_with_label_from_widget(hidden_radio, "Temporary")
        grid.add(temporary_radio)

        hscale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, digits=0)
        grid.add(hscale)
        hscale.connect("format-value", on_scale_format_value)
        hscale.connect("value-changed", on_scale_value_changed)
        hscale.set_range(0, 30)
        hscale.set_increments(1, 1)

        if adapter['Discoverable'] and adapter['DiscoverableTimeout'] > 0:
            temporary_radio.set_active(True)
            hscale.set_value(adapter['DiscoverableTimeout'])
            hscale.set_sensitive(True)
        elif adapter['Discoverable'] and adapter['DiscoverableTimeout'] == 0:
            always_radio.set_active(True)
        else:
            hidden_radio.set_active(True)

        label_friendly = Gtk.Label("<b>Friendly name</b>", halign=Gtk.Align.START,
                                   use_markup=True)
        grid.add(label_friendly)
        name_entry = Gtk.Entry(max_length=248, width_request=280)
        grid.add(name_entry)
        name_entry.set_text(adapter.get_name())

        hidden_radio.connect("toggled", on_toggle, "hidden")
        always_radio.connect("toggled", on_toggle, "always")
        temporary_radio.connect("toggled", on_toggle, "temporary")
        name_entry.connect("changed", on_name_changed)

        ui['grid'] = grid
        ui["hidden_radio"] = hidden_radio
        ui["always_radio"] = always_radio
        ui["temparary_radio"] = temporary_radio
        return ui

    def add_to_notebook(self, adapter):
        hci_dev = os.path.basename(adapter.get_object_path())
        hci_dev_num = int(hci_dev[3:])

        if hci_dev not in self.tabs:
            self.tabs[hci_dev] = self.build_adapter_tab(adapter)
        else:
            if self.tabs[hci_dev]['visible']:
                return
            #might need to update settings at this point
        ui = self.tabs[hci_dev]
        ui['visible'] = True
        name = adapter["Alias"]
        label = Gtk.Label(label=name)
        ui['label'] = label
        label.set_max_width_chars(20)
        label.props.hexpand = True
        label.set_ellipsize(Pango.EllipsizeMode.END)
        self.notebook.insert_page(ui['grid'], label, hci_dev_num)

    def remove_from_notebook(self, adapter):
        hci_dev = os.path.basename(adapter.get_object_path())
        hci_dev_num = int(hci_dev[3:])

        self.tabs[hci_dev]['visible'] = False
        self.notebook.remove_page(hci_dev_num)

    #leave actual tab contents intact in case adapter becomes present once again

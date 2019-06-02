# coding=utf-8
import os.path
import logging
import gettext

from blueman.Constants import UI_PATH
from blueman.Functions import *
import blueman.bluez as bluez

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk
from gi.repository import Pango


class BluemanAdapters(Gtk.Window):
    def __init__(self, selected_hci_dev, socket_id):
        super().__init__(
            title=_("Bluetooth Adapters"),
            border_width=5,
            resizable=False,
            icon_name="blueman-device",
            name="BluemanAdapters"
        )
        self.connect("delete-event", self._on_close)

        self.notebook = Gtk.Notebook(visible=True)

        if socket_id:
            plug = Gtk.Plug.new(socket_id)
            plug.show()
            plug.connect('delete-event', self._on_close)
            plug.add(self.notebook)
        else:
            self.add(self.notebook)
            self.connect("delete-event", self._on_close)
            self.show()

        self.tabs = {}
        self._adapters = {}

        setup_icon_path()
        bluez.Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)
        self.manager = bluez.Manager()

        check_single_instance("blueman-adapters", lambda time: self.present_with_time(time))

        check_bluetooth_status(_("Bluetooth needs to be turned on for the adapter manager to work"), lambda: exit())

        adapters = self.manager.get_adapters()
        if not adapters:
            logging.error('No adapter(s) found')
            exit(1)

        self.manager.connect_signal('adapter-added', self.on_adapter_added)
        self.manager.connect_signal('adapter-removed', self.on_adapter_removed)
        for adapter in adapters:
            path = adapter.get_object_path()
            hci_dev = os.path.basename(path)
            self._adapters[hci_dev] = adapter
            self.on_adapter_added(self.manager, path)

        # activate a particular tab according to command line option
        if selected_hci_dev is not None:
            if selected_hci_dev in self.tabs:
                hci_dev_num = int(selected_hci_dev[3:])
                self.notebook.set_current_page(hci_dev_num)
            else:
                logging.error('Error: the selected adapter does not exist')
        self.notebook.show_all()

    def _on_close(self, *args, **kwargs):
        Gtk.main_quit()

    def on_property_changed(self, adapter, name, value, path):
        hci_dev = os.path.basename(path)
        if name == "Discoverable" and value == 0:
            self.tabs[hci_dev]["hidden_radio"].set_active(True)
        elif name == "Alias":
            self.tabs[hci_dev]["label"].set_text(value)

    def on_adapter_added(self, _manager, adapter_path):
        hci_dev = os.path.basename(adapter_path)
        if hci_dev not in self._adapters:
            self._adapters[hci_dev] = bluez.Adapter(adapter_path)

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
        def on_hidden_toggle(radio):
            if not radio.props.active:
                return
            adapter['DiscoverableTimeout'] = 0
            adapter['Discoverable'] = False
            hscale.set_sensitive(False)

        def on_always_toggle(radio):
            if not radio.props.active:
                return
            adapter['DiscoverableTimeout'] = 0
            adapter['Discoverable'] = True
            hscale.set_sensitive(False)

        def on_temporary_toggle(radio):
            if not radio.props.active:
                return
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
                return gettext.ngettext("%d Minute", "%d Minutes", value) % value

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

        builder = Gtk.Builder()
        builder.set_translation_domain("blueman")
        builder.add_from_file(UI_PATH + "/adapters-tab.ui")

        hscale = builder.get_object("hscale")
        hscale.connect("format-value", on_scale_format_value)
        hscale.connect("value-changed", on_scale_value_changed)
        hscale.set_range(0, 30)
        hscale.set_increments(1, 1)

        hidden_radio = builder.get_object("hidden")
        always_radio = builder.get_object("always")
        temporary_radio = builder.get_object("temporary")

        if adapter['Discoverable'] and adapter['DiscoverableTimeout'] > 0:
            temporary_radio.set_active(True)
            hscale.set_value(adapter['DiscoverableTimeout'])
            hscale.set_sensitive(True)
        elif adapter['Discoverable'] and adapter['DiscoverableTimeout'] == 0:
            always_radio.set_active(True)
        else:
            hidden_radio.set_active(True)

        name_entry = builder.get_object("name_entry")
        name_entry.set_text(adapter.get_name())

        hidden_radio.connect("toggled", on_hidden_toggle)
        always_radio.connect("toggled", on_always_toggle)
        temporary_radio.connect("toggled", on_temporary_toggle)
        name_entry.connect("changed", on_name_changed)

        ui['grid'] = builder.get_object("grid")
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
                # might need to update settings at this point
        ui = self.tabs[hci_dev]
        ui['visible'] = True
        name = adapter.get_name()
        if name == '':
            name = _('Adapter') + ' %d' % (hci_dev_num + 1)
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

        # leave actual tab contents intact in case adapter becomes present once again

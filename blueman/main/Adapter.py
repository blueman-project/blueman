from gettext import gettext as _
import os.path
import logging
import gettext
from typing import Dict, TYPE_CHECKING, Optional, Any

from blueman.Functions import *
from blueman.bluez.Manager import Manager
from blueman.bluez.Adapter import Adapter
from blueman.main.Builder import Builder

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Gio, Gdk
from gi.repository import Pango


if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class Tab(TypedDict):
        grid: Gtk.Grid
        hidden_radio: Gtk.RadioButton
        always_radio: Gtk.RadioButton
        temparary_radio: Gtk.RadioButton
        visible: bool
        label: Gtk.Label


class BluemanAdapters(Gtk.Application):
    def __init__(self, selected_hci_dev: Optional[str], socket_id: Optional[int]) -> None:
        super().__init__(application_id="org.blueman.Adapters")

        self.socket_id = socket_id
        self.selected_hci_dev = selected_hci_dev

        self.notebook = Gtk.Notebook(visible=True)

        self.window: Optional[Gtk.ApplicationWindow] = None

        self.tabs: Dict[str, "Tab"] = {}
        self._adapters: Dict[str, Adapter] = {}

        setup_icon_path()
        Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)
        self.manager = Manager()

        check_bluetooth_status(_("Bluetooth needs to be turned on for the adapter manager to work"), bmexit)

        adapters = self.manager.get_adapters()
        if not adapters:
            logging.error('No adapter(s) found')
            bmexit()

        self.manager.connect_signal('adapter-added', self.on_adapter_added)
        self.manager.connect_signal('adapter-removed', self.on_adapter_removed)
        for adapter in adapters:
            path = adapter.get_object_path()
            self.on_adapter_added(self.manager, path)

        # activate a particular tab according to command line option
        if selected_hci_dev is not None:
            if selected_hci_dev in self.tabs:
                hci_dev_num = int(selected_hci_dev[3:])
                self.notebook.set_current_page(hci_dev_num)
            else:
                logging.error('Error: the selected adapter does not exist')
        self.notebook.show_all()

    def do_activate(self) -> None:
        def app_release(_plug: Gtk.Plug, _event: Gdk.Event) -> bool:
            self.release()
            return False

        if self.socket_id:
            self.hold()
            plug = Gtk.Plug.new(self.socket_id)
            plug.show()
            plug.connect('delete-event', app_release)
            plug.add(self.notebook)
            return

        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self, title=_("Bluetooth Adapters"), border_width=5,
                                                resizable=False, icon_name="blueman-device", name="BluemanAdapters")
            self.window.add(self.notebook)

        self.window.present_with_time(Gtk.get_current_event_time())

    def on_property_changed(self, _adapter: Adapter, name: str, value: Any, path: str) -> None:
        hci_dev = os.path.basename(path)
        if name == "Discoverable" and value == 0:
            self.tabs[hci_dev]["hidden_radio"].set_active(True)
        elif name == "Alias":
            self.tabs[hci_dev]["label"].set_text(value)

    def on_adapter_added(self, _manager: Manager, adapter_path: str) -> None:
        hci_dev = os.path.basename(adapter_path)
        if hci_dev not in self._adapters:
            self._adapters[hci_dev] = Adapter(obj_path=adapter_path)

        self._adapters[hci_dev].connect_signal("property-changed", self.on_property_changed)
        self.add_to_notebook(self._adapters[hci_dev])

    def on_adapter_removed(self, _manager: Manager, adapter_path: str) -> None:
        hci_dev = os.path.basename(adapter_path)
        self.remove_from_notebook(self._adapters[hci_dev])

    def _on_dbus_name_appeared(self, _connection: Gio.DBusConnection, name: str, owner: str) -> None:
        logging.info(f"{name} {owner}")

    def _on_dbus_name_vanished(self, _connection: Gio.DBusConnection, name: str) -> None:
        logging.info(name)
        # FIXME: show error dialog and exit

    def build_adapter_tab(self, adapter: Adapter) -> "Tab":
        def on_hidden_toggle(radio: Gtk.RadioButton) -> None:
            if not radio.props.active:
                return
            adapter['DiscoverableTimeout'] = 0
            adapter['Discoverable'] = False
            hscale.set_sensitive(False)

        def on_always_toggle(radio: Gtk.RadioButton) -> None:
            if not radio.props.active:
                return
            adapter['DiscoverableTimeout'] = 0
            adapter['Discoverable'] = True
            hscale.set_sensitive(False)

        def on_temporary_toggle(radio: Gtk.RadioButton) -> None:
            if not radio.props.active:
                return
            adapter['Discoverable'] = True
            hscale.set_sensitive(True)
            hscale.set_value(3)

        def on_scale_format_value(_scale: Gtk.Scale, value: float) -> str:
            if value == 0:
                if adapter['Discoverable']:
                    return _("Always")
                else:
                    return _("Hidden")
            else:
                return gettext.ngettext("%(minutes)d Minute", "%(minutes)d Minutes", int(value)) % {"minutes": value}

        def on_scale_value_changed(scale: Gtk.Scale) -> None:
            val = scale.get_value()
            logging.info(f"value: {val}")
            if val == 0 and adapter['Discoverable']:
                always_radio.props.active = True
            timeout = int(val * 60)
            adapter['DiscoverableTimeout'] = timeout

        def on_name_changed(entry: Gtk.Entry) -> None:
            adapter['Alias'] = entry.get_text()

        builder = Builder("adapters-tab.ui")

        hscale = builder.get_widget("hscale", Gtk.Scale)
        hscale.connect("format-value", on_scale_format_value)
        hscale.connect("value-changed", on_scale_value_changed)
        hscale.set_range(0, 30)
        hscale.set_increments(1, 1)

        hidden_radio = builder.get_widget("hidden", Gtk.RadioButton)
        always_radio = builder.get_widget("always", Gtk.RadioButton)
        temporary_radio = builder.get_widget("temporary", Gtk.RadioButton)

        if adapter['Discoverable'] and adapter['DiscoverableTimeout'] > 0:
            temporary_radio.set_active(True)
            hscale.set_value(adapter['DiscoverableTimeout'])
            hscale.set_sensitive(True)
        elif adapter['Discoverable'] and adapter['DiscoverableTimeout'] == 0:
            always_radio.set_active(True)
        else:
            hidden_radio.set_active(True)

        name_entry = builder.get_widget("name_entry", Gtk.Entry)
        name_entry.set_text(adapter.get_name())

        hidden_radio.connect("toggled", on_hidden_toggle)
        always_radio.connect("toggled", on_always_toggle)
        temporary_radio.connect("toggled", on_temporary_toggle)
        name_entry.connect("changed", on_name_changed)

        return {
            "grid": builder.get_widget("grid", Gtk.Grid),
            "hidden_radio": hidden_radio,
            "always_radio": always_radio,
            "temparary_radio": temporary_radio,
            "visible": False,
            "label": Gtk.Label()
        }

    def add_to_notebook(self, adapter: Adapter) -> None:
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

    def remove_from_notebook(self, adapter: Adapter) -> None:
        hci_dev = os.path.basename(adapter.get_object_path())
        hci_dev_num = int(hci_dev[3:])

        self.tabs[hci_dev]['visible'] = False
        self.notebook.remove_page(hci_dev_num)

        # leave actual tab contents intact in case adapter becomes present once again

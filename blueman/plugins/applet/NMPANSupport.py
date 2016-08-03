# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gio, GLib, GObject
from blueman.Functions import dprint
from blueman.plugins.AppletPlugin import AppletPlugin
from uuid import uuid4

devtypes = {1: "Ethernet",
            2: "Wi-Fi",
            5: "Bluetooth",
            6: "OLPC",
            7: "WiMAX",
            8: "Modem",
            9: "InfiniBand",
            10: "Bond",
            11: "VLAN",
            12: "ADSL",
            13: "Bridge",
            14: "Generic",
            15: "Team",
            16: "TUN",
            17: "IPTunnel",
            18: "MACVLAN",
            19: "VXLAN",
            20: "Veth"
            }

states = {0: "Unknown",
          10: "Unmanaged",
          20: "Unavailable",
          30: "Disconnected",
          40: "Prepare",
          50: "Config",
          60: "Need Auth",
          70: "IP Config",
          80: "IP Check",
          90: "Secondaries",
          100: "Activated",
          110: "Deactivating",
          120: "Failed"}

reasons = {0: "No reason given",
           1: "Unknown error",
           2: "Device is now managed",
           3: "Device is now unmanaged",
           4: "The device could not be readied for configuration",
           5: "IP configuration could not be reserved (no available address, timeout, etc)",
           6: "The IP config is no longer valid",
           7: "Secrets were required, but not provided",
           8: "802.1x supplicant disconnected",
           9: "802.1x supplicant configuration failed",
           10: "802.1x supplicant failed",
           11: "802.1x supplicant took too long to authenticate",
           12: "PPP service failed to start",
           13: "PPP service disconnected",
           14: "PPP failed",
           15: "DHCP client failed to start",
           16: "DHCP client error",
           17: "DHCP client failed",
           18: "Shared connection service failed to start",
           19: "Shared connection service failed",
           20: "AutoIP service failed to start",
           21: "AutoIP service error",
           22: "AutoIP service failed",
           23: "The line is busy",
           24: "No dial tone",
           25: "No carrier could be established",
           26: "The dialing request timed out",
           27: "The dialing attempt failed",
           28: "Modem initialization failed",
           29: "Failed to select the specified APN",
           30: "Not searching for networks",
           31: "Network registration denied",
           32: "Network registration timed out",
           33: "Failed to register with the requested network",
           34: "PIN check failed",
           35: "Necessary firmware for the device may be missing",
           36: "The device was removed",
           37: "NetworkManager went to sleep",
           38: "The device's active connection disappeared",
           39: "Device disconnected by user or client",
           40: "Carrier/link changed",
           41: "The device's existing connection was assumed",
           42: "The supplicant is now available",
           43: "The modem could not be found",
           44: "The Bluetooth connection failed or timed out",
           45: "GSM Modem's SIM Card not inserted",
           46: "GSM Modem's SIM Pin required",
           47: "GSM Modem's SIM Puk required",
           48: "GSM Modem's SIM wrong",
           49: "InfiniBand device does not support connected mode",
           50: "A dependency of the connection failed",
           51: "Problem with the RFC 2684 Ethernet over ADSL bridge",
           52: "ModemManager not running",
           53: "The WiFi network could not be found",
           54: "A secondary connection of the base connection failed",
           55: "DCB or FCoE setup failed",
           56: "teamd control failed",
           57: "Modem failed or no longer available",
           58: "Modem now ready and available",
           59: "SIM PIN was incorrect",
           60: "New connection activation was enqueued",
           61: "the device's parent changed",
           62: "the device parent's management changed"}

class NMDevice(Gio.DBusProxy):
    __gsignals__ = { str('state-changed'): (GObject.SignalFlags.NO_HOOKS,
                                            None,
                                            (GObject.TYPE_PYOBJECT,
                                             GObject.TYPE_PYOBJECT,
                                             GObject.TYPE_PYOBJECT)) }

    def __init__(self, object_path, *args, **kwargs):
        self._name = 'org.freedesktop.NetworkManager'
        self._bt_interface_name = 'org.freedesktop.NetworkManager.Device.Bluetooth'
        self._interface_name = 'org.freedesktop.NetworkManager.Device'
        self._object_path = object_path

        super(NMDevice, self).__init__(
            g_name=self._name,
            g_interface_name=self._interface_name,
            g_object_path=self._object_path,
            g_bus_type=Gio.BusType.SYSTEM,
            g_flags=Gio.DBusProxyFlags.NONE,
            *args, **kwargs)

        self.error_handler = None
        self.reply_handler = None
        self.signal_id = 0

        self.init()

    def do_g_signal(self, sender, signal_name, params):
        if signal_name == 'StateChanged':
            if params:
                state, old_state, reason = params.unpack()
                self.emit('state-changed', state, old_state, reason)

    @property
    def interface(self):
        iface = self.get_cached_property('Interface').unpack()
        return iface

    def get_pan_connection(self):
        # We always pick the first connection
        conns = self.get_cached_property('AvailableConnections')
        return conns.unpack()[0]

    def get_active_connection(self):
        conn = self.get_cached_property('ActiveConnection').unpack()
        return conn

    def is_pan_device(self):
        device_type = self.get_cached_property('DeviceType').unpack()
        if device_type != 5:
            return False

        btdevice = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SYSTEM,
            Gio.DBusProxyFlags.NONE,
            None,
            self._name,
            self._object_path,
            self._bt_interface_name,
            None)

        caps = btdevice.get_cached_property('BtCapabilities').unpack()
        if caps == 2:
            return True
        else:
            return False

    def is_connected(self):
        active_connection = self.get_cached_property('ActiveConnection').unpack()
        if active_connection == '/':
            return False
        else:
            return True


class NMPANSupport(AppletPlugin):
    __depends__ = ["DBusService"]
    __conflicts__ = ["DhcpClient"]
    __icon__ = "network"
    __author__ = "infirit"
    __description__ = _("Provides support for Personal Area Networking (PAN) introduced in NetworkManager 0.8")
    __priority__ = 2

    def on_load(self, applet):
        self.nm_manager = None
        self.nm_settings = None
        self.watch_id = None
        self.pan_devices = {}

        self.watch_id = Gio.bus_watch_name(Gio.BusType.SYSTEM,
                                           'org.freedesktop.NetworkManager',
                                           Gio.BusNameWatcherFlags.AUTO_START,
                                           self._on_nm_dbus_name_appeared,
                                           self._on_nm_dbus_name_vanished)

        self.nm_name = 'org.freedesktop.NetworkManager'
        self.nm_interface = 'org.freedesktop.NetworkManager'
        self.nm_path = '/org/freedesktop/NetworkManager'

        self.settings_interface = 'org.freedesktop.NetworkManager.Settings'
        self.settings_path = "/org/freedesktop/NetworkManager/Settings"

        self.connection_settings_interface = 'org.freedesktop.NetworkManager.Settings.Connection'

        self.nm_device_interface = 'org.freedesktop.NetworkManager.Device'
        self.nm_bt_device_interface = 'org.freedesktop.NetworkManager.Device.Bluetooth'

    def on_unload(self):
        Gio.bus_unwatch_name(self.watch_id)

    def _on_nm_dbus_name_appeared(self, _connection, _name, owner):
        dprint(owner)
        self.nm_manager = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM, Gio.DBusProxyFlags.NONE, None,
                                                         self.nm_name, self.nm_path, self.nm_interface)

        self.nm_settings = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM, Gio.DBusProxyFlags.NONE, None,
                                                          self.nm_name, self.settings_path, self.settings_interface)

        self.nm_manager_sig = self.nm_manager.connect("g-signal", self.on_manager_signal)
        self.get_all_pan_devices()

    def _on_nm_dbus_name_vanished(self, _connection, owner):
        dprint(owner)
        for key in self.pan_devices:
            proxy, sig = self.pan_devices.pop(key)
            proxy.disconnect(sig)

        self.nm_manager.disconnect(self.nm_manager_sig)

        self.nm_manager = None
        self.nm_settings = None
        self.nm_manager_sig = None
        self.pan_devices = {}

    def on_manager_signal(self, proxy, sender, signal_name, params):
        if signal_name == 'DeviceAdded':
            dev_obj_path = params.unpack()[0]
            dprint(dev_obj_path)

            dev_proxy = NMDevice(dev_obj_path)
            if dev_proxy.is_pan_device:
                self.pan_devices[dev_obj_path] = dev_proxy
        elif signal_name == 'DeviceRemoved':
            dev_obj_path = params.unpack()[0]
            dprint(dev_obj_path)

            if dev_obj_path in self.pan_devices:
                bt_device = self.pan_devices.pop(dev_obj_path)
                if bt_device.signal_id:
                    bt_device.disconnect(bt_device.signal_id)
        elif signal_name in ('PropertiesChanged', 'StateChanged', 'CheckPermissions'):
            pass  # we do not care
        else:
            dprint("Warning: unhandled signal: ", signal_name)

    def on_device_state_changed(self, proxy, state, old_state, reason):
        state_change_msg = 'state: %s (%s) old state: %i (%s) reason: %i (%s)'
        print(state_change_msg % (state, states[state], old_state, states[old_state], reason, reasons[reason]))

        if (state <= 30 or state == 110) and 30 < old_state <= 100:
            if proxy.error_handler:
                proxy.error_handler(GLib.Error(reasons[reason]))

        elif state == 120:
            if proxy.error_handler:
                proxy.error_handler(GLib.Error(reasons[reason]))

        elif state == 100:
            if proxy.reply_handler:
                proxy.reply_handler()

        if state == 30:
            # Disconnect the signal when disconnected
            proxy.disconnect(proxy.signal_id)
            proxy.signal_id = 0

    def find_device(self, bdaddr):
        for obj_path, dev in self.pan_devices.items():
            if dev.interface == bdaddr:
                return dev

    def create_pan_connection(self, service):
        addr_bytes = bytearray.fromhex(service.device['Address'].replace(':', ' '))
        self.nm_settings.AddConnection({
            'connection': {'id': '%s Network' % service.device['Alias'], 'uuid': str(uuid4()),
                           'autoconnect': False, 'type': 'bluetooth'},
            'bluetooth': {'bdaddr': addr_bytes, 'type': 'panu'},
            'ipv4': {'method': 'auto'},
            'ipv6': {'method': 'auto'}
        })

    def get_all_pan_devices(self):
        devices = self.nm_manager.get_cached_property('Devices')
        if not devices:
            return None

        for obj_path in devices:
            dev_proxy = NMDevice(obj_path)

            if dev_proxy.is_pan_device():
                self.pan_devices[obj_path] = dev_proxy

    def service_connect_handler(self, service, ok, err):
        if service.group != 'network':
            return

        pan_device = self.find_device(service.device['Address'])

        if pan_device.is_connected():
            err(GLib.Error(_("Already connected")))
        else:
            object_path = pan_device.get_object_path()
            connection_path = pan_device.get_pan_connection()
            sig = pan_device.connect('state-changed', self.on_device_state_changed)
            pan_device.signal_id = sig

            self.nm_manager.ActivateConnection(str('(ooo)'), connection_path, object_path, connection_path)

    def service_disconnect_handler(self, service, ok, err):
        if service.group != 'network':
            return

        pan_device = self.find_device(service.device['Address'])
        active_conn_path = pan_device.get_active_connection()

        if  not pan_device.is_connected():
            return
        else:
            if pan_device.signal_id:
                pan_device.disconnect(pan_device.signal_id)
                pan_device.signal_id = 0

            self.nm_manager.DeactivateConnection(str('(o)'), active_conn_path)

        ok()
        return True

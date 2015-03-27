from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from gi.repository import GObject
import dbus
from blueman.plugins.AppletPlugin import AppletPlugin
from uuid import uuid1
from blueman.main.SignalTracker import SignalTracker


class NewConnectionBuilder:
    DEVICE_STATE_DISCONNECTED = 30
    DEVICE_STATE_ACTIVATED = 100
    DEVICE_STATE_DEACTIVATING = 110
    DEVICE_STATE_FAILED = 120

    def __init__(self, parent, service, ok_cb, err_cb):
        self.parent = parent
        self.ok_cb = ok_cb
        self.err_cb = err_cb

        self.signals = SignalTracker()

        self.device = None
        self.connection = None

        self.signals.Handle("dbus", parent.bus, self.on_nm_device_added, "DeviceAdded",
                            "org.freedesktop.NetworkManager")
        self.signals.Handle("dbus", parent.bus, self.on_nma_new_connection, "NewConnection",
                            self.parent.settings_interface)

        self.device = self.parent.find_device(service.device.Address)

        self.connection = self.parent.find_connection(service.device.Address, "panu")
        if not self.connection:
            # This is for compatibility with network-manager < 0.9.8.6. Newer versions that support BlueZ 5 add a
            # default connection automatically
            addr_bytes = bytearray.fromhex(str.replace(str(service.device.Address), ':', ' '))
            parent.nma.AddConnection({
                'connection':   {'id': '%s on %s' % (service.name, service.device.Alias), 'uuid': str(uuid1()),
                                 'autoconnect': False, 'type': 'bluetooth'},
                'bluetooth':    {'bdaddr': dbus.ByteArray(addr_bytes), 'type': 'panu'},
                'ipv4':         {'method': 'auto'},
                'ipv6':         {'method': 'auto'}
            })
            GObject.timeout_add(1000, self.signal_wait_timeout)
        else:
            self.init_connection()

    def cleanup(self):
        self.signals.DisconnectAll()

    def signal_wait_timeout(self):
        if not self.device or not self.connection:
            self.err_cb(dbus.DBusException("Network Manager did not support the connection"))
            if self.connection:
                self.remove_connection()
            self.cleanup()

    def on_nm_device_added(self, path):
        dprint(path)
        self.device = path
        if self.device and self.connection:
            self.init_connection()

    def on_nma_new_connection(self, path):
        dprint(path)
        self.connection = path
        if self.device and self.connection:
            self.init_connection()

    def init_connection(self):
        self.cleanup()
        dprint("activating", self.connection, self.device)
        if not self.device or not self.connection:
            self.err_cb(dbus.DBusException("Network Manager did not support the connection"))
            if self.connection:
                self.remove_connection()
            self.cleanup()
        else:
            self.signals.Handle("dbus", self.parent.bus, self.on_device_state, "StateChanged",
                                "org.freedesktop.NetworkManager.Device", path=self.device)

            args = [self.connection, self.device, self.connection]

            if self.parent.legacy:
                args.insert(0, self.parent.settings_bus)

            self.parent.nm.ActivateConnection(*args)

    def remove_connection(self):
        self.parent.remove_connection(self.connection)

    def on_device_state(self, state, oldstate, reason):
        dprint("state=", state, "oldstate=", oldstate, "reason=", reason)
        if (state <= self.DEVICE_STATE_DISCONNECTED or state == self.DEVICE_STATE_DEACTIVATING) and \
                                self.DEVICE_STATE_DISCONNECTED < oldstate <= self.DEVICE_STATE_ACTIVATED:
            if self.err_cb:
                self.err_cb(dbus.DBusException("Connection was interrupted"))

            self.remove_connection()
            self.cleanup()

        elif state == self.DEVICE_STATE_FAILED:
            self.err_cb(dbus.DBusException("Network Manager Failed to activate the connection"))
            self.remove_connection()
            self.cleanup()

        elif state == self.DEVICE_STATE_ACTIVATED:
            self.ok_cb()
            self.err_cb = None
            self.ok_cb = None


class NMPANSupport(AppletPlugin):
    __depends__ = ["DBusService"]
    __conflicts__ = ["DhcpClient"]
    __icon__ = "network"
    __author__ = "Walmis"
    __description__ = _("Provides support for Personal Area Networking (PAN) introduced in NetworkManager 0.8")
    __priority__ = 2

    def on_load(self, applet):
        self.bus = dbus.SystemBus()
        self.nma = None
        self.nm = None
        self.nm_signals = SignalTracker()
        self.nma_signals = SignalTracker()

        self.watches = [self.bus.watch_name_owner("org.freedesktop.NetworkManager", self.on_nm_owner_changed)]

        self.legacy = self.bus.name_has_owner('org.freedesktop.NetworkManagerUserSettings')

        if self.legacy:
            self.watches.append(self.bus.watch_name_owner("org.freedesktop.NetworkManagerUserSettings",
                                                          self.on_nma_owner_changed))
            self.settings_bus = 'org.freedesktop.NetworkManagerUserSettings'
            self.settings_interface = 'org.freedesktop.NetworkManagerSettings'
            self.connection_settings_interface = 'org.freedesktop.NetworkManagerSettings.Connection'
            self.settings_path = "/org/freedesktop/NetworkManagerSettings"
            NewConnectionBuilder.DEVICE_STATE_DISCONNECTED = 3
            NewConnectionBuilder.DEVICE_STATE_ACTIVATED = 8
            NewConnectionBuilder.DEVICE_STATE_FAILED = 9
        else:
            self.settings_bus = 'org.freedesktop.NetworkManager'
            self.settings_interface = 'org.freedesktop.NetworkManager.Settings'
            self.connection_settings_interface = 'org.freedesktop.NetworkManager.Settings.Connection'
            self.settings_path = "/org/freedesktop/NetworkManager/Settings"

    def remove_connection(self, path):
        self.bus.call_blocking(self.settings_bus, path, self.connection_settings_interface, "Delete", "", [])

    @staticmethod
    def format_bdaddr(addr):
        return "%02X:%02X:%02X:%02X:%02X:%02X" % (addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])

    def find_device(self, bdaddr):
        devices = self.nm.GetDevices()
        for dev in devices:
            try:
                d = self.bus.call_blocking("org.freedesktop.NetworkManager", dev, "org.freedesktop.DBus.Properties",
                                           "GetAll", "s", ["org.freedesktop.NetworkManager.Device.Bluetooth"])
                if d["HwAddress"] == bdaddr:
                    dprint(d["HwAddress"])
                    return dev

            except dbus.DBusException:
                pass

    def find_connection(self, address, t):
        conns = self.nma.ListConnections()
        for conn in conns:
            c = self.bus.call_blocking(self.settings_bus, conn, self.connection_settings_interface, "GetSettings", "",
                                       [])
            try:
                if (self.format_bdaddr(c["bluetooth"]["bdaddr"]) == address) and c["bluetooth"]["type"] == t:
                    return conn
            except:
                pass

    def find_active_connection(self, address, type):
        props = self.bus.call_blocking("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager",
                                       "org.freedesktop.DBus.Properties", "GetAll", "s",
                                       ["org.freedesktop.NetworkManager"])

        nma_connection = self.find_connection(address, type)
        if nma_connection:
            active_conns = props["ActiveConnections"]
            for conn in active_conns:
                conn_props = self.bus.call_blocking("org.freedesktop.NetworkManager",
                                                    conn,
                                                    "org.freedesktop.DBus.Properties",
                                                    "GetAll",
                                                    "s",
                                                    ["org.freedesktop.NetworkManager.Connection.Active"])

                if conn_props["Connection"] == nma_connection:
                    return conn

    def on_nma_owner_changed(self, owner):
        if owner == "":
            self.nma = None
        else:
            service = self.bus.get_object(self.settings_bus, self.settings_path)
            self.nma = dbus.proxies.Interface(service, self.settings_interface)

    def on_nm_owner_changed(self, owner):
        if owner == "":
            self.nm = None
            self.nm_signals.DisconnectAll()
        else:
            service = self.bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
            self.nm = dbus.proxies.Interface(service, "org.freedesktop.NetworkManager")
            if not self.legacy:
                self.on_nma_owner_changed(owner)


    def on_unload(self):
        self.nm_signals.DisconnectAll()
        self.nma_signals.DisconnectAll()

        for watch in self.watches:
            watch.cancel()

    def service_connect_handler(self, service, ok, err):
        if service.group != 'network':
            return

        if self.find_active_connection(service.device.Address, "panu"):
            err(dbus.DBusException(_("Already connected")))
        else:
            NewConnectionBuilder(self, service, ok, err)

        return True

    def service_disconnect_handler(self, service, ok, err):
        if service.group != 'network':
            return

        d = service.device
        active_conn_path = self.find_active_connection(d.Address, "panu")

        if not active_conn_path:
            return

        self.bus.call_blocking("org.freedesktop.NetworkManager",
                               "/org/freedesktop/NetworkManager",
                               "org.freedesktop.NetworkManager",
                               "DeactivateConnection",
                               "o",
                               [active_conn_path])
        ok()
        return True

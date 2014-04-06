from blueman.Functions import dprint
from gi.repository import GObject
import dbus
from blueman.Sdp import *
from blueman.plugins.AppletPlugin import AppletPlugin
from uuid import uuid1
from gi.repository import GConf
import os
from blueman.main.SignalTracker import SignalTracker
from blueman.main.Device import Device
from blueman.bluez.Network import Network


class NMDeviceState:
    UNKNOWN = 0

    #/* Initial state of all devices and the only state for devices not
    # * managed by NetworkManager.
    # *
    # * Allowed next states:
    # *   UNAVAILABLE:  the device is now managed by NetworkManager
    # */
    UNMANAGED = 1

    #/* Indicates the device is not yet ready for use, but is managed by
    # * NetworkManager.  For Ethernet devices, the device may not have an
    # * active carrier.  For WiFi devices, the device may not have it's radio
    # * enabled.
    # *
    # * Allowed next states:
    # *   UNMANAGED:  the device is no longer managed by NetworkManager
    # *   DISCONNECTED:  the device is now ready for use
    # */
    UNAVAILABLE = 2

    #/* Indicates the device does not have an activate connection to anything.
    # *
    # * Allowed next states:
    # *   UNMANAGED:  the device is no longer managed by NetworkManager
    # *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
    # *   PREPARE:  the device has started activation
    # */
    DISCONNECTED = 3

    #/* Indicate states in device activation.
    # *
    # * Allowed next states:
    # *   UNMANAGED:  the device is no longer managed by NetworkManager
    # *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
    # *   FAILED:  an error ocurred during activation
    # *   NEED_AUTH:  authentication/secrets are needed
    # *   ACTIVATED:  (IP_CONFIG only) activation was successful
    # *   DISCONNECTED:  the device's connection is no longer valid, or NetworkManager went to sleep
    # */
    PREPARE = 4
    CONFIG = 5
    NEED_AUTH = 6
    IP_CONFIG = 7

    #/* Indicates the device is part of an active network connection.
    # *
    # * Allowed next states:
    # *   UNMANAGED:  the device is no longer managed by NetworkManager
    # *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
    # *   FAILED:  a DHCP lease was not renewed, or another error
    # *   DISCONNECTED:  the device's connection is no longer valid, or NetworkManager went to sleep
    # */
    ACTIVATED = 8

    #/* Indicates the device's activation failed.
    # *
    # * Allowed next states:
    # *   UNMANAGED:  the device is no longer managed by NetworkManager
    # *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
    # *   DISCONNECTED:  the device's connection is ready for activation, or NetworkManager went to sleep
    # */
    FAILED = 9


class NewConnectionBuilder:
    def __init__(self, parent, params, ok_cb, err_cb):
        self.parent = parent
        self.params = params
        self.ok_cb = ok_cb
        self.err_cb = err_cb

        self.signals = SignalTracker()

        self.device = None
        self.connection = None

        self.signals.Handle("dbus", parent.bus, self.on_nm_device_added, "DeviceAdded",
                            "org.freedesktop.NetworkManager")
        self.signals.Handle("dbus", parent.bus, self.on_nma_new_connection, "NewConnection",
                            "org.freedesktop.NetworkManagerSettings")

        self.device = self.parent.find_device(params["bluetooth"]["bdaddr"])

        self.connection = self.parent.find_connection(params["bluetooth"]["bdaddr"], "panu")
        if not self.connection:
            parent.add_connection(params)
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

            self.parent.nm.ActivateConnection("org.freedesktop.NetworkManagerUserSettings", self.connection,
                                              self.device, self.connection)

    def remove_connection(self):
        self.parent.remove_connection(self.connection)

    def on_device_state(self, state, oldstate, reason):
        dprint("state=", state, "oldstate=", oldstate, "reason=", reason)
        if state <= NMDeviceState.DISCONNECTED and NMDeviceState.DISCONNECTED < oldstate <= NMDeviceState.ACTIVATED:
            if self.err_cb:
                self.err_cb(dbus.DBusException("Connection was interrupted"))

            self.remove_connection()
            self.cleanup()

        elif state == NMDeviceState.FAILED:
            self.err_cb(dbus.DBusException("Network Manager Failed to activate the connection"))
            self.remove_connection()
            self.cleanup()

        elif state == NMDeviceState.ACTIVATED:
            self.ok_cb()
            self.err_cb = None
            self.ok_cb = None


class NMPANSupport(AppletPlugin):
    __depends__ = ["DBusService"]
    __conflicts__ = ["DhcpClient", "NMIntegration"]
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

        self.watch1 = self.bus.watch_name_owner("org.freedesktop.NetworkManagerUserSettings", self.on_nma_owner_changed)
        self.watch2 = self.bus.watch_name_owner("org.freedesktop.NetworkManager", self.on_nm_owner_changed)

        self.client = GConf.Client.get_default()

    def set_gconf(self, key, value):
        func = None

        if type(value) == str or type(value) == unicode:
            func = self.client.set_string
        elif type(value) == int:
            func = self.client.set_int
        elif type(value) == bool:
            func = self.client.set_bool
        elif type(value) == float:
            func = self.client.set_float
        elif type(value) == list:
            def x(key, val):
                self.client.set_list(key, gconf.ValueType.STRING, val)

            func = x

        elif type(value) == dbus.Array:
            if value.signature == "i":
                def x(key, val):
                    self.client.set_list(key, gconf.ValueType.INT, val)

                func = x
            elif value.signature == "s":
                def x(key, val):
                    self.client.set_list(key, gconf.ValueType.STRING, val)

                func = x
            else:
                raise AttributeError("Cant set this type in gconf")

        else:
            raise AttributeError("Cant set %s in gconf" % type(value))

        func(key, value)

    def find_free_gconf_slot(self):
        dirs = list(self.client.all_dirs("/system/networking/connections"))
        dirs.sort()

        i = 1
        for d in dirs:
            try:
                d = int(os.path.basename(d))
            except:
                continue
            if d != i:
                return i

            i += 1

        return i

    def add_connection(self, params):
        slot = self.find_free_gconf_slot()

        base_path = "/system/networking/connections/%d" % slot

        for group, settings in params.items():
            path = base_path + "/%s" % group
            for k, v in settings.items():
                key = path + "/%s" % k
                self.set_gconf(key, v)

    def remove_connection(self, path):
        self.bus.call_blocking("org.freedesktop.NetworkManagerUserSettings", path,
                               "org.freedesktop.NetworkManagerSettings.Connection", "Delete", "", [])

    def format_bdaddr(self, addr):
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
            c = self.bus.call_blocking("org.freedesktop.NetworkManagerUserSettings", conn,
                                       "org.freedesktop.NetworkManagerSettings.Connection", "GetSettings", "", [])
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
            service = self.bus.get_object("org.freedesktop.NetworkManagerUserSettings",
                                          "/org/freedesktop/NetworkManagerSettings")
            self.nma = dbus.proxies.Interface(service, "org.freedesktop.NetworkManagerSettings")

    def on_nm_owner_changed(self, owner):
        if owner == "":
            self.nm = None
            self.nm_signals.DisconnectAll()
        else:
            service = self.bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
            self.nm = dbus.proxies.Interface(service, "org.freedesktop.NetworkManager")


    def on_unload(self):
        self.nm_signals.DisconnectAll()
        self.nma_signals.DisconnectAll()

        self.watch1.cancel()
        self.watch2.cancel()

    def service_connect_handler(self, interface, object_path, method, args, ok, err):
        if interface == Network().get_interface_name() and method == "Connect":
            uuid = args[0]
            name = uuid16_to_name(uuid128_to_uuid16(uuid))
            d = Device(object_path)

            conn = self.find_active_connection(d.Address, "panu")
            if conn:
                err(dbus.DBusException(_("Already connected")))
            else:
                params = {}
                params["bluetooth"] = {"name": "bluetooth", "bdaddr": str(d.Address), "type": "panu"}
                params["connection"] = {"autoconnect": False, "id": str("%s on %s") % (name, d.Alias),
                                        "uuid": str(uuid1()), "type": "bluetooth"}
                params['ipv4'] = {'addresses': dbus.Array([], dbus.Signature("i")),
                                  'dns': dbus.Array([], dbus.Signature("i")), "method": "auto",
                                  "routes": dbus.Array([], dbus.Signature("i"))}

                NewConnectionBuilder(self, params, ok, err)

            return True

        elif interface == Network().get_interface_name() and method == "Disconnect":
            d = Device(object_path)
            active_conn_path = self.find_active_connection(d.Address, "panu")
            if active_conn_path:
                self.bus.call_blocking("org.freedesktop.NetworkManager",
                                       "/org/freedesktop/NetworkManager",
                                       "org.freedesktop.NetworkManager",
                                       "DeactivateConnection",
                                       "o",
                                       [active_conn_path])
                ok()
                return True

# coding=utf-8
from gi.repository import Gio, GLib
from blueman.plugins.AppletPlugin import AppletPlugin
from uuid import uuid4
import logging


class NewConnectionBuilder:
    DEVICE_STATE_DISCONNECTED = 30
    DEVICE_STATE_ACTIVATED = 100
    DEVICE_STATE_DEACTIVATING = 110
    DEVICE_STATE_FAILED = 120

    def __init__(self, parent, service, ok_cb, err_cb):
        self.parent = parent
        self.ok_cb = ok_cb
        self.err_cb = err_cb

        self.device = None
        self.connection = None

        self.signal_subs = []

        nm_sub = parent._bus.signal_subscribe(self.parent.nm_manager_name,
                                              self.parent.nm_manager_interface,
                                              'DeviceAdded',
                                              None,
                                              None,
                                              Gio.DBusSignalFlags.NONE,
                                              self.on_nm_device_added)
        self.signal_subs.append(nm_sub)
        nms_sub = parent._bus.signal_subscribe(self.parent.nm_manager_name,
                                               self.parent.nm_settings_interface,
                                               'NewConnection',
                                               None,
                                               None,
                                               Gio.DBusSignalFlags.NONE,
                                               self.on_nma_new_connection)
        self.signal_subs.append(nms_sub)

        self.device = self.parent.find_device(service.device['Address'])

        self.connection = self.parent.find_connection(service.device['Address'], "panu")
        if not self.connection:
            # Newer versions that support BlueZ 5 add a default connection automatically
            # However users may have removed the connection and we error out
            addr_bytes = bytearray.fromhex(service.device['Address'].replace(':', ' '))
            parent.nm_settings.AddConnection('(a{sa{sv}})', {
                'connection': {'id': GLib.Variant.new_string('%s Network' % service.device['Alias']),
                               'uuid': GLib.Variant.new_string(str(uuid4())),
                               'autoconnect': GLib.Variant.new_boolean(False),
                               'type': GLib.Variant.new_string('bluetooth')},
                'bluetooth': {'bdaddr': GLib.Variant.new_bytestring_array(addr_bytes),
                              'type': GLib.Variant.new_string('panu')},
                'ipv4': {'method': GLib.Variant.new_string('auto')},
                'ipv6': {'method': GLib.Variant.new_string('auto')}
            })
            GLib.timeout_add(1000, self.signal_wait_timeout)
        else:
            self.init_connection()

    def cleanup(self):
        for sub in self.signal_subs:
            self.parent._bus.signal_unsubscribe(sub)
        self.signal_subs = []

    def signal_wait_timeout(self):
        if not self.device or not self.connection:
            self.err_cb(GLib.Error("Network Manager did not support the connection"))
            self.cleanup()

    def on_nm_device_added(self, connection, sender_name, object_path, interface_name, signal_name, param):
        logging.info(object_path)
        self.device = object_path
        if self.device and self.connection:
            self.init_connection()

    def on_nma_new_connection(self, connection, sender_name, object_path, interface_name, signal_name, param):
        logging.info(object_path)
        self.connection = object_path
        if self.device and self.connection:
            self.init_connection()

    def init_connection(self):
        self.cleanup()
        logging.info("activating %s %s" % (self.connection, self.device))
        if not self.device or not self.connection:
            self.err_cb(GLib.Error("Network Manager did not support the connection"))
            self.cleanup()
        else:
            sub = self.parent._bus.signal_subscribe(self.parent.nm_manager_name,
                                                    'org.freedesktop.NetworkManager.Device',
                                                    'StateChanged',
                                                    self.device,
                                                    None,
                                                    Gio.DBusSignalFlags.NONE,
                                                    self.on_device_state)

            self.signal_subs.append(sub)
            args = [self.connection, self.device, self.connection]

            self.parent.nm_manager.ActivateConnection('(ooo)', *args)

    def on_device_state(self, connection, sender_name, object_path, interface_name, signal_name, param):
        state, oldstate, reason = param.unpack()
        logging.info("state=%s oldstate=%s reason=%s" % (state, oldstate, reason))
        if (state <= self.DEVICE_STATE_DISCONNECTED or state == self.DEVICE_STATE_DEACTIVATING) and \
                self.DEVICE_STATE_DISCONNECTED < oldstate <= self.DEVICE_STATE_ACTIVATED:
            if self.err_cb:
                self.err_cb(GLib.Error("Connection was interrupted"))

            self.cleanup()

        elif state == self.DEVICE_STATE_FAILED:
            self.err_cb(GLib.Error("Network Manager Failed to activate the connection"))
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
        self.nm_manager = None
        self.nm_settings = None
        self.watch_id = None

        self.nm_manager_name = self.nm_manager_interface = 'org.freedesktop.NetworkManager'
        self.nm_manager_path = '/org/freedesktop/NetworkManager'
        self.nm_settings_interface = 'org.freedesktop.NetworkManager.Settings'
        self.connection_settings_interface = 'org.freedesktop.NetworkManager.Settings.Connection'
        self.nm_settings_path = "/org/freedesktop/NetworkManager/Settings"

        Gio.bus_get(Gio.BusType.SYSTEM, None, self.on_dbus_connection_finnish)

    def on_dbus_connection_finnish(self, cancellable, result):
        self._bus = Gio.bus_get_finish(result)
        watch = Gio.bus_watch_name(Gio.BusType.SYSTEM,
                                   self.nm_manager_name,
                                   Gio.BusNameWatcherFlags.NONE,
                                   self.on_name_appeared, self.on_name_vanished)
        self.watch_id = watch

    def on_name_appeared(self, connection, name, owner):
        Gio.DBusProxy.new(connection,
                          Gio.DBusProxyFlags.NONE,
                          None,
                          self.nm_manager_name,
                          self.nm_manager_path,
                          self.nm_manager_interface,
                          None,
                          self.on_proxy_finnish,
                          'nm-manager')

        Gio.DBusProxy.new(connection,
                          Gio.DBusProxyFlags.NONE,
                          None,
                          self.nm_manager_name,
                          self.nm_settings_path,
                          self.nm_settings_interface,
                          None,
                          self.on_proxy_finnish,
                          'nm-settings')

    def on_name_vanished(self, connection, name):
        self.nm_manager = None
        self.nm_settings = None

    def on_proxy_finnish(self, proxy, result, nm_name):
        nm_proxy = proxy.new_finish(result)
        if nm_name == 'nm-manager':
            self.nm_manager = nm_proxy
        elif nm_name == 'nm-settings':
            self.nm_settings = nm_proxy

    @staticmethod
    def format_bdaddr(addr):
        return "%02X:%02X:%02X:%02X:%02X:%02X" % (addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])

    def find_device(self, bdaddr):
        devices = self.nm_manager.GetDevices()
        for dev in devices:
            try:
                d = self._bus.call_sync(self.nm_manager_name, dev, "org.freedesktop.DBus.Properties", "GetAll",
                                        GLib.Variant("(s)", ("org.freedesktop.NetworkManager.Device.Bluetooth",)),
                                        None, Gio.DBusCallFlags.NONE, GLib.MAXINT, None).unpack()[0]

                if d["HwAddress"] == bdaddr:
                    logging.info(d["HwAddress"])
                    return dev

            except GLib.Error:
                pass

    def find_connection(self, address, t):
        conns = self.nm_settings.ListConnections()
        for conn in conns:
            c = self._bus.call_sync(self.nm_manager_name, conn, self.connection_settings_interface, "GetSettings",
                                    None, None, Gio.DBusCallFlags.NONE, GLib.MAXINT, None).unpack()[0]
            if "bluetooth" not in c:
                continue

            if (self.format_bdaddr(c["bluetooth"]["bdaddr"]) == address) and c["bluetooth"]["type"] == t:
                return conn

    def find_active_connection(self, address, conntype):
        props = self._bus.call_sync(self.nm_manager_name, self.nm_manager_path,
                                    "org.freedesktop.DBus.Properties", "GetAll",
                                    GLib.Variant("(s)", ("org.freedesktop.NetworkManager",)), None,
                                    Gio.DBusCallFlags.NONE, GLib.MAXINT, None).unpack()[0]

        nma_connection = self.find_connection(address, conntype)
        if nma_connection:
            active_conns = props["ActiveConnections"]
            for conn in active_conns:
                conn_props = self._bus.call_sync(self.nm_manager_name, conn,
                                                 "org.freedesktop.DBus.Properties", "GetAll",
                                                 GLib.Variant("(s)", ("org.freedesktop.NetworkManager.Connection.Active",)),
                                                 None, Gio.DBusCallFlags.NONE, GLib.MAXINT, None).unpack()[0]

                if conn_props["Connection"] == nma_connection:
                    return conn

    def on_unload(self):
        Gio.bus_unwatch_name(self.watch_id)

    def service_connect_handler(self, service, ok, err):
        if service.group != 'network':
            return

        if self.find_active_connection(service.device['Address'], "panu"):
            err(GLib.Error(_("Already connected")))
        else:
            NewConnectionBuilder(self, service, ok, err)

        return True

    def service_disconnect_handler(self, service, ok, err):
        if service.group != 'network':
            return

        d = service.device
        active_conn_path = self.find_active_connection(d['Address'], "panu")

        if not active_conn_path:
            return

        self.nm_manager.DeactivateConnection('(o)', active_conn_path)
        ok()
        return True

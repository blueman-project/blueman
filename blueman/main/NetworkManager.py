import gi
import uuid

try:
    gi.require_version('NM', '1.0')
except ValueError:
    raise ImportError('NM python bindings not found.')

from gi.repository import GLib, NM
from blueman.main.Config import Config
from blueman.Functions import dprint


class NMConnectionError(Exception):
    pass


class NMConnectionBase(object):
    conntype = None

    def __init__(self, service, reply_handler=None, error_handler=None):
        if self.conntype not in ('dun', 'panu'):
            self._raise_or_error_handler(
                NMConnectionError('Invalid connection type %s, should be panu or dun' % self.conntype)
            )
        self.device = service.device
        self.bdaddr = self.device.get_properties()['Address']
        self.error_handler = error_handler
        self.reply_handler = reply_handler
        self.connection = None
        self.active_connection = None
        self.client = NM.Client.new()
        self.Config = Config('org.blueman.gsmsetting', '/org/blueman/gsmsettings/%s/' % self.bdaddr)

        self.find_or_create_connection()

    def _return_or_reply_handler(self, msg):
        dprint(msg)
        if not self.reply_handler:
            return msg
        else:
            self.reply_handler(msg)
            return

    def _raise_or_error_handler(self, error):
        dprint(error)
        if not self.error_handler:
            raise error
        else:
            self.error_handler(error)
            return

    def _on_connection_added(self, client, result, conn_uuid):
        try:
            self.connection = client.add_connection_finish(result)
        except GLib.Error as e:
            self._raise_or_error_handler(e)

        self.store_uuid(conn_uuid)

    def _on_device_state_changed(self, device, new_state, old_state, reason):
        new = NM.DeviceState(new_state)
        old = NM.DeviceState(old_state)
        state_reason = NM.DeviceStateReason(reason)
        dprint('New: %s Old: %s Reason: %s' % (new.value_nick, old.value_nick, state_reason.value_nick))

        error_msg = None
        reply_msg = None

        if new == NM.DeviceState.FAILED:
            error_msg = 'Connection failed with reason: %s' % state_reason.value_nick
        elif new == NM.DeviceState.ACTIVATED:
            reply_msg = 'Connection sucesfully activated'
        elif (new <= NM.DeviceState.DISCONNECTED or new == NM.DeviceState.DEACTIVATING) and \
                (NM.DeviceState.DISCONNECTED < old <= NM.DeviceState.ACTIVATED):
            error_msg = 'Connection disconnected with reason %s' % state_reason.value_nick
        else:
            return  # Keep checking the state changes

        # We are done with state changes
        device.disconnect_by_func(self._on_device_state_changed)
        if error_msg is None:
            self._return_or_reply_handler(reply_msg)
        else:
            dprint(error_msg)
            self._raise_or_error_handler(NMConnectionError(error_msg))

    def activate(self):
        def on_connection_activate(client, result):
            try:
                self.active_connection = client.activate_connection_finish(result)
            except GLib.Error as e:
                self._raise_or_error_handler(e)

        device = self.client.get_device_by_iface(self.bdaddr)
        if not device:
            self._raise_or_error_handler(NMConnectionError('Could not find device %s' % self.bdaddr))
        elif device.get_state() == NM.DeviceState.ACTIVATED:
            self._raise_or_error_handler(NMConnectionError('Device %s already activated' % self.bdaddr))
        else:
            device.connect('state-changed', self._on_device_state_changed)
            self.client.activate_connection_async(self.connection, device, None, None, on_connection_activate)

    def deactivate(self):
        def on_connection_deactivate(client, result):
            try:
                client.deactivate_connection_finish(result)
                self._return_or_reply_handler('Device %s deactivated sucessfully' % self.bdaddr)
                self.active_connection = None
            except GLib.Error as e:
                self._raise_or_error_handler(e)

        self.client.deactivate_connection_async(self.active_connection, None, on_connection_deactivate)

    def find_or_create_connection(self):
        if not self.connection_uuid:
            self.create_connection()
        else:
            conn = self.client.get_connection_by_uuid(self.connection_uuid)
            if conn is None:
                self.create_connection()
            else:
                dprint('Found existing connection with uuid %s' % self.connection_uuid)
                self.connection = conn

                if self.conntype == 'dun':
                    settings_gsm = conn.get_setting_gsm()

                    if settings_gsm.props.apn != self.Config['apn']:
                        dprint('Updating apn on connection to %s' % self.Config['apn'])
                        settings_gsm.props.apn = self.Config['apn']
                    if settings_gsm.props.number != self.Config['number']:
                        dprint('Updating number on connection to %s' % self.Config['number'])
                        settings_gsm.props.number = self.Config['number']

                conn.commit_changes(True, None)

        # Try to find active connection
        for active_conn in self.client.get_active_connections():
            conn = active_conn.get_connection()
            if conn == self.connection:
                self.active_connection = active_conn

    @property
    def connected(self):
        if self.active_connection is None:
            return False

        state = self.active_connection.get_state()
        if state == NM.ActiveConnectionState.CONNECTED:
            return True
        else:
            return False

    def create_connection(self):
        raise NotImplementedError

    def store_uuid(self, conn_uuid):
        raise NotImplementedError

    @property
    def connection_uuid(self):
        raise NotImplementedError


class NMPANConnection(NMConnectionBase):
    conntype = 'panu'

    def store_uuid(self, conn_uuid):
        self.Config['nmpanuuid'] = conn_uuid

    @property
    def connection_uuid(self):
        # PANU connections are automatically created so attempt to find it
        # It appears the Name property is used not Alias!
        conn = self.client.get_connection_by_id('%s Network' % self.device.get_properties()['Name'])
        if conn is not None:
            conn_settings = conn.get_setting_connection()
            return conn_settings.get_uuid()
        else:
            return self.Config['nmpanuuid']

    def create_connection(self):
        conn = NM.SimpleConnection()
        conn_id = '%s Network' % self.device.get_properties()['Name']
        conn_uuid = str(uuid.uuid4())

        conn_sett = NM.SettingConnection(type='bluetooth', id=conn_id, uuid=conn_uuid, autoconnect=False)
        conn_sett_bt = NM.SettingBluetooth(type=self.conntype, bdaddr=self.bdaddr)
        conn.add_setting(conn_sett)
        conn.add_setting(conn_sett_bt)

        self.client.add_connection_async(conn, True, None, self._on_connection_added, conn_uuid)


class NMDUNConnection(NMConnectionBase):
    conntype = 'dun'

    def store_uuid(self, conn_uuid):
        self.Config['nmdunuuid'] = conn_uuid

    @property
    def connection_uuid(self):
        return self.Config['nmdunuuid']

    def create_connection(self):
        if not self.Config['apn']:
            self._raise_or_error_handler(NMConnectionError('No apn configured, make sure to configure dialup settings'))
            return

        conn = NM.SimpleConnection()
        conn_id = 'blueman dun for %s' % self.device.get_properties()['Alias']
        conn_uuid = str(uuid.uuid4())

        conn_sett = NM.SettingConnection(type='bluetooth', id=conn_id, uuid=conn_uuid, autoconnect=False)
        conn_sett_bt = NM.SettingBluetooth(type=self.conntype, bdaddr=self.bdaddr)
        conn_sett_gsm = NM.SettingGsm(apn=self.Config['apn'], number=self.Config['number'])
        conn.add_setting(conn_sett)
        conn.add_setting(conn_sett_bt)
        conn.add_setting(conn_sett_gsm)

        self.client.add_connection_async(conn, True, None, self._on_connection_added, conn_uuid)

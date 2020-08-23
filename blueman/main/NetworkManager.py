import gi
import logging
import uuid
from typing import Optional, Callable, Union

from blueman.Service import Service

try:
    gi.require_version('NM', '1.0')
except ValueError:
    raise ImportError('NM python bindings not found.')

from gi.repository import GLib, GObject, NM, Gio
from blueman.main.Config import Config


class NMConnectionError(Exception):
    pass


class NMConnectionBase:
    conntype: str

    def __init__(self, service: Service, reply_handler: Callable[[], None],
                 error_handler: Callable[[Union[NMConnectionError, GLib.Error]], None]):
        if self.conntype not in ('dun', 'panu'):
            error_handler(
                NMConnectionError(f"Invalid connection type {self.conntype}, should be panu or dun")
            )
        self.device = service.device
        self.bdaddr = self.device['Address']
        self.error_handler = error_handler
        self.reply_handler = reply_handler
        self.connection = None
        self.active_connection = None
        self.client = NM.Client.new()
        self.Config = Config("org.blueman.gsmsetting", f"/org/blueman/gsmsettings/{self.bdaddr}/")
        self._statehandler: Optional[int] = None

        self.find_or_create_connection()

    def _on_connection_added(self, client: NM.Client, result: Gio.AsyncResult, conn_uuid: str) -> None:
        try:
            self.connection = client.add_connection_finish(result)
        except GLib.Error as e:
            self.error_handler(e)

        self.store_uuid(conn_uuid)

    def _on_device_state_changed(self, device: NM.Device, new_state: int, old_state: int, reason: int) -> None:
        new = NM.DeviceState(new_state)
        old = NM.DeviceState(old_state)
        state_reason = NM.DeviceStateReason(reason)
        logging.debug(f"New: {new.value_nick} Old: {old.value_nick} Reason: {state_reason.value_nick}")

        error_msg = None

        if new == NM.DeviceState.FAILED:
            error_msg = f"Connection failed with reason: {state_reason.value_nick}"
        elif new == NM.DeviceState.ACTIVATED:
            logging.debug("Connection successfully activated")
        elif (new <= NM.DeviceState.DISCONNECTED or new == NM.DeviceState.DEACTIVATING) and \
                (NM.DeviceState.DISCONNECTED < old <= NM.DeviceState.ACTIVATED):
            error_msg = f"Connection disconnected with reason {state_reason.value_nick}"
        else:
            return  # Keep checking the state changes

        # We are done with state changes
        assert self._statehandler is not None
        GObject.signal_handler_disconnect(device, self._statehandler)
        if error_msg is None:
            self.reply_handler()
        else:
            logging.debug(error_msg)
            self.error_handler(NMConnectionError(error_msg))

    def activate(self) -> None:
        def on_connection_activate(client: NM.Client, result: Gio.AsyncResult) -> None:
            try:
                self.active_connection = client.activate_connection_finish(result)
            except GLib.Error as e:
                self.error_handler(e)

        device = self.client.get_device_by_iface(self.bdaddr)
        if not device:
            self.error_handler(NMConnectionError(f"Could not find device {self.bdaddr}"))
        elif device.get_state() == NM.DeviceState.ACTIVATED:
            self.error_handler(NMConnectionError(f"Device {self.bdaddr} already activated"))
        else:
            self._statehandler = device.connect('state-changed', self._on_device_state_changed)
            self.client.activate_connection_async(self.connection, device, None, None, on_connection_activate)

    def deactivate(self) -> None:
        def on_connection_deactivate(client: NM.Client, result: Gio.AsyncResult) -> None:
            try:
                client.deactivate_connection_finish(result)
                logging.debug(f"Device {self.bdaddr} deactivated sucessfully")
                self.reply_handler()
                self.active_connection = None
            except GLib.Error as e:
                self.error_handler(e)

        self.client.deactivate_connection_async(self.active_connection, None, on_connection_deactivate)

    def find_or_create_connection(self) -> None:
        if not self.connection_uuid:
            self.create_connection()
        else:
            conn = self.client.get_connection_by_uuid(self.connection_uuid)
            if conn is None:
                self.create_connection()
            else:
                logging.debug(f"Found existing connection with uuid {self.connection_uuid}")
                self.connection = conn

                if self.conntype == 'dun':
                    settings_gsm = conn.get_setting_gsm()

                    if settings_gsm.props.apn != self.Config['apn']:
                        logging.debug(f"Updating apn on connection to {self.Config['apn']}")
                        settings_gsm.props.apn = self.Config['apn']
                    if settings_gsm.props.number != self.Config['number']:
                        logging.debug(f"Updating number on connection to {self.Config['number']}")
                        settings_gsm.props.number = self.Config['number']

                conn.commit_changes(True, None)

        # Try to find active connection
        for active_conn in self.client.get_active_connections():
            conn = active_conn.get_connection()
            if conn == self.connection:
                self.active_connection = active_conn

    @property
    def connected(self) -> bool:
        if self.active_connection is None:
            return False

        state = self.active_connection.get_state()
        if state == NM.ActiveConnectionState.CONNECTED:
            return True
        else:
            return False

    def create_connection(self) -> None:
        raise NotImplementedError

    def store_uuid(self, conn_uuid: str) -> None:
        raise NotImplementedError

    @property
    def connection_uuid(self) -> str:
        raise NotImplementedError


class NMPANConnection(NMConnectionBase):
    conntype = 'panu'

    def store_uuid(self, conn_uuid: str) -> None:
        self.Config['nmpanuuid'] = conn_uuid

    @property
    def connection_uuid(self) -> str:
        # PANU connections are automatically created so attempt to find it
        # It appears the Name property is used not Alias!
        conn = self.client.get_connection_by_id(f"{self.device['Name']} Network")
        res: str
        if conn is not None:
            conn_settings = conn.get_setting_connection()
            res = conn_settings.get_uuid()
        else:
            res = self.Config['nmpanuuid']
        return res

    def create_connection(self) -> None:
        conn = NM.SimpleConnection()
        conn_id = f"{self.device['Name']} Network"
        conn_uuid = str(uuid.uuid4())

        conn_sett = NM.SettingConnection(type='bluetooth', id=conn_id, uuid=conn_uuid, autoconnect=False)
        conn_sett_bt = NM.SettingBluetooth(type=self.conntype, bdaddr=self.bdaddr)
        conn.add_setting(conn_sett)
        conn.add_setting(conn_sett_bt)

        self.client.add_connection_async(conn, True, None, self._on_connection_added, conn_uuid)


class NMDUNConnection(NMConnectionBase):
    conntype = 'dun'

    def store_uuid(self, conn_uuid: str) -> None:
        self.Config['nmdunuuid'] = conn_uuid

    @property
    def connection_uuid(self) -> str:
        res: str = self.Config['nmdunuuid']
        return res

    def create_connection(self) -> None:
        if not self.Config['apn']:
            self.error_handler(NMConnectionError('No apn configured, make sure to configure dialup settings'))
            return

        conn = NM.SimpleConnection()
        conn_id = f"blueman dun for {self.device['Alias']}"
        conn_uuid = str(uuid.uuid4())

        conn_sett = NM.SettingConnection(type='bluetooth', id=conn_id, uuid=conn_uuid, autoconnect=False)
        conn_sett_bt = NM.SettingBluetooth(type=self.conntype, bdaddr=self.bdaddr)
        conn_sett_gsm = NM.SettingGsm(apn=self.Config['apn'], number=self.Config['number'])
        conn.add_setting(conn_sett)
        conn.add_setting(conn_sett_bt)
        conn.add_setting(conn_sett_gsm)

        self.client.add_connection_async(conn, True, None, self._on_connection_added, conn_uuid)

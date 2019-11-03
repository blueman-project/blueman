from typing import List, Dict, Optional
from typing_extensions import TypedDict

ERR: Dict[int, str]
RFCOMM_HANGUP_NOW: int
RFCOMM_RELEASE_ONHUP: int
RFCOMM_REUSE_DLC: int
RFCOMM_STATES: List[str]
RFCOMM_TTY_ATTACHED: int

class _RfcommDev(TypedDict):
    id: int
    channel: int
    flags: int
    state: str
    src: str
    dst: str

class _HciInfo(TypedDict):
    acl_mtu: int
    acl_pkts: int
    bdaddr: str
    dev_id: int
    features: List[int]
    flags: int
    link_mode: int
    link_policy: int
    name: str
    pkt_type: int
    sco_mtu: int
    stat: Dict[str, int]
    type: int

class BridgeException(Exception):
    errno: int
    def __init__(self, errno: int) -> None: ...

class ConnInfoReadError(Exception): ...

class RFCOMMError(Exception): ...

class conn_info:
    failed: bool
    def __init__(self, addr: str, hci_name: str) -> None: ...
    def deinit(self) -> None: ...
    def get_lq(self) -> int: ...
    def get_rssi(self) -> int: ...
    def get_tpl(self) -> int: ...
    def init(self) -> None: ...

def create_bridge(name: str = "pan1") -> None: ...
def create_rfcomm_device(local_address: str, remote_address: str, channel: int) -> int: ...
def destroy_bridge(name: str = "pan1") -> None: ...
def device_info(hci_name: str = "hci0") -> _HciInfo: ...
def page_timeout(hci_name: str = "hci0") -> float: ...
def get_rfcomm_channel(uuid: int, bdaddr: str) -> Optional[int]: ...
def release_rfcomm_device(id: int) -> int: ...
def rfcomm_list() -> List[_RfcommDev]: ...

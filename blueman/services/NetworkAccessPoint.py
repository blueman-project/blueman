from blueman.services.meta import NetworkService
from blueman.Sdp import NAP_SVCLASS_ID


class NetworkAccessPoint(NetworkService):
    __svclass_id__ = NAP_SVCLASS_ID
    __icon__ = "network-wireless"
    __priority__ = 81

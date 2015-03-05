from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.services.meta import NetworkService
from blueman.Sdp import GN_SVCLASS_ID


class GroupNetwork(NetworkService):
    __group__ = 'network'
    __svclass_id__ = GN_SVCLASS_ID
    __icon__ = "network-wireless"
    __priority__ = 80

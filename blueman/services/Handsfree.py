from blueman.Service import Service
from blueman.Sdp import HANDSFREE_SVCLASS_ID


class Handsfree(Service):
    __group__ = 'audio'
    __svclass_id__ = HANDSFREE_SVCLASS_ID
    __icon__ = "blueman-handsfree"

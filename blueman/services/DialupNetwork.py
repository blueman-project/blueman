from gettext import gettext as _
from typing import Set

from blueman.Service import Action
from blueman.services.meta import SerialService
from blueman.Sdp import DIALUP_NET_SVCLASS_ID
from blueman.gui.GsmSettings import GsmSettings


class DialupNetwork(SerialService):
    __svclass_id__ = DIALUP_NET_SVCLASS_ID
    __icon__ = "modem"
    __priority__ = 50

    @property
    def common_actions(self) -> Set[Action]:
        def open_settings() -> None:
            d = GsmSettings(self.device['Address'])
            d.run()
            d.destroy()

        return {Action(
            _("Dialup Settings"),
            "preferences-other",
            {'PPPSupport', 'NMDUNSupport'},
            open_settings
        )}

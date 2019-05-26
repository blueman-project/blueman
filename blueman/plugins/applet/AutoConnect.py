from gi.repository import GLib

from blueman.Sdp import ServiceUUID
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin


class AutoConnect(AppletPlugin):
    __depends__ = ["DBusService"]

    __gsettings__ = {
        "schema": "org.blueman.plugins.autoconnect",
        "path": None
    }
    __options__ = {
        "services": {"type": list, "default": "[]"}
    }

    def __init__(self, parent):
        super().__init__(parent)
        GLib.timeout_add(60000, self._run)

    def on_manager_state_changed(self, state):
        if state:
            self._run()

    def _run(self):
        for address, uuid in self.get_option('services'):
            device = self.parent.Manager.find_device(address)
            if device is None or device.get("Connected"):
                continue

            def reply(*_args):
                Notification(_("Connected"), _("Automatically connected to %(service)s on %(device)s") %
                             {"service": ServiceUUID(uuid).name, "device": device["Alias"]},
                             icon_name=device["Icon"]).show()

            def err(_reason):
                pass

            self.parent.Plugins.DBusService.connect_service(device.get_object_path(), uuid, reply, err)

        return True

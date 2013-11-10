from blueman.main.SpeedCalc import SpeedCalc
from blueman.main.Config import Config
from blueman.ods.OdsManager import OdsManager
from blueman.main.Device import Device
from blueman.Functions import *
from blueman.Lib import get_special_dir, SpecialDirType
import os
from gi.repository import GObject
from blueman.gui.Notification import Notification
import weakref


class Transfer(OdsManager):
    def __init__(self, applet):
        OdsManager.__init__(self)
        self.Applet = applet
        try:
            self.status_icon = self.Applet.Plugins.StatusIcon
        except:
            self.status_icon = None

        self.GHandle("server-created", self.on_server_created)
        self.Config = Config("transfer")

        #check options
        if self.Config.props.opp_enabled == None:
            self.Config.props.opp_enabled = True

        if self.Config.props.ftp_enabled == None:
            self.Config.props.ftp_enabled = True

        self.create_server("opp")
        self.create_server("ftp")

        self.allowed_devices = []

    def create_server(self, pattern):

        if pattern == "opp":
            if self.Config.props.opp_enabled:
                OdsManager.create_server(self)
        elif pattern == "ftp":
            if self.Config.props.ftp_enabled:
                OdsManager.create_server(self, pattern="ftp", require_pairing=True)


    def start_server(self, pattern):
        server = self.get_server(pattern)
        if server != None:
            if self.Config.props.shared_path == None:
                d = get_special_dir(SpecialDirType.PUBLIC_SHARE)
                if d == None:
                    self.Config.props.shared_path = os.path.expanduser("~")
                else:
                    self.Config.props.shared_path = d

            if not os.path.isdir(self.Config.props.shared_path):
                raise Exception("Configured share directory %s does not exist" % self.Config.props.shared_path)

            if pattern == "opp":
                server.Start(self.Config.props.shared_path, True, False)
            elif pattern == "ftp":
                if self.Config.props.ftp_allow_write == None:
                    self.Config.props.ftp_allow_write = False

                server.Start(self.Config.props.shared_path, self.Config.props.ftp_allow_write, True)
            return True
        else:
            return False

    def on_server_created(self, inst, server, pattern):
        def on_started(server):
            dprint(pattern, "Started")

        server.GHandle("started", on_started)
        server.GHandle("session-created", self.on_session_created)
        server.pattern = pattern
        self.start_server(pattern)


    def on_session_created(self, server, session):
        dprint(server.pattern, "session created")
        if server.pattern != "opp":
            return

        session.GHandle("transfer-progress", self.transfer_progress)
        session.GHandle("cancelled", self.transfer_finished, "cancelled")
        session.GHandle("disconnected", self.transfer_finished, "disconnected")
        session.GHandle("transfer-completed", self.transfer_finished, "completed")
        session.GHandle("error-occurred", self.transfer_finished, "error")
        session.GHandle("transfer-started", self.on_transfer_started)

        session.transfer = {}
        session.transfer["notification"] = None
        session.transfer["silent_transfers"] = 0
        session.transfer["normal_transfers"] = 0

        session.server = server


    def on_transfer_started(self, session, filename, local_path, total_bytes):
        dprint("transfer started", filename)
        info = session.server.GetServerSessionInfo(session.object_path)
        trusted = False
        try:
            dev = self.Applet.Manager.get_adapter().find_device(info["BluetoothAddress"])
            dev = Device(dev)
            name = dev.Alias
            trusted = dev.Trusted
        except Exception as e:
            dprint(e)
            name = info["BluetoothAddress"]

        wsession = weakref.proxy(session)
        wself = weakref.proxy(self)

        icon = get_icon("blueman", 48)

        session.transfer["filename"] = filename
        session.transfer["filepath"] = local_path
        session.transfer["total"] = total_bytes
        session.transfer["finished"] = False
        session.transfer["failed"] = False
        session.transfer["waiting"] = True

        session.transfer["address"] = info["BluetoothAddress"]
        session.transfer["name"] = name

        session.transfer["transferred"] = 0

        def access_cb(n, action):
            dprint(action)

            if action == "closed":
                if wsession.transfer["waiting"]:
                    wsession.Reject()

            if wsession.transfer["waiting"]:
                if action == "accept":
                    wsession.Accept()
                    wself.allowed_devices.append(wsession.transfer["address"])
                    GObject.timeout_add(60000, wself.allowed_devices.remove, wsession.transfer["address"])
                else:
                    wsession.Reject()
                wsession.transfer["waiting"] = False

        if info["BluetoothAddress"] not in self.allowed_devices and not (self.Config.props.opp_accept and trusted):

            n = Notification(_("Incoming file over Bluetooth"),
                             _("Incoming file %(0)s from %(1)s") % {"0": "<b>" + os.path.basename(filename) + "</b>",
                                                                    "1": "<b>" + name + "</b>"},
                             30000, [["accept", _("Accept"), "gtk-yes"], ["reject", _("Reject"), "gtk-no"]], access_cb,
                             icon, self.status_icon)

            if total_bytes > 350000:
                session.transfer["normal_transfers"] += 1
            else:
                session.transfer["silent_transfers"] += 1
        else:
            if total_bytes > 350000:
                n = Notification(_("Receiving file"),
                                 _("Receiving file %(0)s from %(1)s") % {
                                 "0": "<b>" + os.path.basename(filename) + "</b>", "1": "<b>" + name + "</b>"},
                                 pixbuf=icon, status_icon=self.status_icon)

                session.transfer["normal_transfers"] += 1
            else:
                session.transfer["silent_transfers"] += 1
                n = None

            access_cb(n, "accept")

        session.transfer["notification"] = n

    def transfer_progress(self, session, bytes_transferred):
        session.transfer["transferred"] = bytes_transferred

    def add_open(self, n, name, path):
        if Notification.actions_supported():
            print("adding action")

            def on_open(*args):
                print("open")
                spawn(["xdg-open", path], True)

            n.add_action("open", name, on_open, None)
            n.show()


    def transfer_finished(self, session, *args):
        type = args[-1]
        dprint(args)
        try:
            if not session.transfer["finished"]:

                if type != "cancelled" and type != "error":
                    session.transfer["finished"] = True

                    if session.transfer["total"] > 350000:
                        icon = get_icon("blueman", 48)
                        n = Notification(_("File received"),
                                         _("File %(0)s from %(1)s successfully received") % {
                                         "0": "<b>" + session.transfer["filename"] + "</b>",
                                         "1": "<b>" + session.transfer["name"] + "</b>"},
                                         pixbuf=icon, status_icon=self.status_icon)
                        self.add_open(n, "Open", session.transfer["filepath"])
                else:
                    session.transfer["failed"] = True
                    session.transfer["finished"] = True

                    n = session.transfer["notification"]
                    if n:
                        n.close()

                    icon = get_icon("blueman", 48)

                    session.transfer["notification"] = Notification(_("Transfer failed"),
                                                                    _("Transfer of file %(0)s failed") % {
                                                                    "0": "<b>" + session.transfer["filename"] + "</b>",
                                                                    "1": "<b>" + session.transfer["name"] + "</b>"},
                                                                    pixbuf=icon, status_icon=self.status_icon)
                    if session.transfer["total"] > 350000:
                        session.transfer["normal_transfers"] -= 1
                    else:
                        session.transfer["silent_transfers"] -= 1

            if type == "disconnected":
                icon = get_icon("blueman", 48)

                if session.transfer["normal_transfers"] == 0 and session.transfer["silent_transfers"] == 1:
                    n = Notification(_("File received"),
                                     _("File %(0)s from %(1)s successfully received") % {
                                     "0": "<b>" + session.transfer["filename"] + "</b>",
                                     "1": "<b>" + session.transfer["name"] + "</b>"},
                                     pixbuf=icon, status_icon=self.status_icon)

                    self.add_open(n, "Open", session.transfer["filepath"])

                elif session.transfer["normal_transfers"] == 0 and session.transfer["silent_transfers"] > 0:
                    n = Notification(_("Files received"),
                                     ngettext("Received %d file in the background",
                                              "Received %d files in the background",
                                              session.transfer["silent_transfers"]) % session.transfer[
                                         "silent_transfers"],
                                     pixbuf=icon, status_icon=self.status_icon)

                    self.add_open(n, "Open Location", self.Config.props.shared_path)

                elif session.transfer["normal_transfers"] > 0 and session.transfer["silent_transfers"] > 0:

                    n = Notification(_("Files received"),
                                     ngettext("Received %d more file in the background",
                                              "Received %d more files in the background",
                                              session.transfer["silent_transfers"]) % session.transfer[
                                         "silent_transfers"],
                                     pixbuf=icon, status_icon=self.status_icon)
                    self.add_open(n, "Open Location", self.Config.props.shared_path)

                del session.transfer
                del session.server

        except KeyError:
            pass

    def on_server_destroyed(self, inst, server):
        pass

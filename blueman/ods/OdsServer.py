from gi.repository import GObject
from blueman.ods.OdsBase import OdsBase
from blueman.ods.OdsServerSession import OdsServerSession


class OdsServer(OdsBase):
    __gsignals__ = {
    'started': (GObject.SignalFlags.NO_HOOKS, None, ()),
    'stopped': (GObject.SignalFlags.NO_HOOKS, None, ()),
    'closed': (GObject.SignalFlags.NO_HOOKS, None, ()),
    'error-occured': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    'session-created': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    'session-removed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, obj_path):
        OdsBase.__init__(self, "org.openobex.Server", obj_path)

        self.Handle("Started", self.on_started)
        self.Handle("Stopped", self.on_stopped)
        self.Handle("Closed", self.on_closed)
        self.Handle("ErrorOccured", self.on_error)
        self.Handle("SessionCreated", self.on_session_created)
        self.Handle("SessionRemoved", self.on_session_removed)

        self.sessions = {}

    def __del__(self):
        dprint("deleting server object")

    def DisconnectAll(self, *args):
        for k, v in self.sessions.iteritems():
            v.DisconnectAll()
        self.sessions = {}
        OdsBase.DisconnectAll(self, *args)

    def on_started(self):
        self.emit("started")

    def on_stopped(self):
        self.emit("stopped")

    def on_closed(self):
        self.emit("closed")
        self.DisconnectAll()

    def on_error(self, err_name, err_message):
        self.emit("error-occured", err_name, err_message)
        self.DisconnectAll()

    def on_session_created(self, path):
        dprint(path)
        self.sessions[path] = OdsServerSession(path)
        self.emit("session-created", self.sessions[path])

    def on_session_removed(self, path):
        dprint(path)
        self.emit("session-removed", path)
        self.sessions[path].DisconnectAll()
        del self.sessions[path]

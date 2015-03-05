from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject
from blueman.ods.OdsBase import OdsBase


class OdsServerSession(OdsBase):
    __gsignals__ = {
        'cancelled': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'disconnected': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'transfer-started': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        'transfer-progress': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'transfer-completed': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'error-occurred': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, obj_path):
        OdsBase.__init__(self, "org.openobex.ServerSession", obj_path)

        self.Handle("Cancelled", self.on_cancelled)
        self.Handle("Disconnected", self.on_disconnected)
        self.Handle("TransferStarted", self.on_trans_started)
        self.Handle("TransferProgress", self.on_trans_progress)
        self.Handle("TransferCompleted", self.on_trans_complete)
        self.Handle("ErrorOccurred", self.on_error)

    def __del__(self):
        dprint("deleting session")

    def on_cancelled(self):
        self.emit("cancelled")

    # self.DisconnectAll()

    def on_disconnected(self):
        self.emit("disconnected")

    #self.DisconnectAll()

    def on_trans_started(self, filename, path, size):
        self.emit("transfer-started", filename, path, size)

    def on_trans_progress(self, bytes):
        self.emit("transfer-progress", bytes)

    def on_trans_complete(self):
        self.emit("transfer-completed")

    def on_error(self, name, msg):
        self.emit("error-occurred", name, msg)

    #self.DisconnectAll()

from blueman.Functions import dprint
from blueman.bluez.obex.Session import Session
from blueman.bluez.obex.Base import Base
from gi.repository import GObject


class Client(Base):
    __gsignals__ = {'session-created': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,))}

    def __init__(self):
        if self.__class__.get_interface_version()[0] < 5:
            super(Client, self).__init__('/', 'org.bluez.obex.client')
            self.__client_interface = self._get_interface('org.bluez.obex.Client')
        else:
            super(Client, self).__init__('/org/bluez/obex', 'org.bluez.obex')
            self.__client_interface = self._get_interface('org.bluez.obex.Client1')

    def create_session(self, dest_addr, source_addr="00:00:00:00:00:00", pattern="opp", error_handler=None):
        def reply(session_path):
            self.emit("session-created", Session(session_path))

        def err(*args):
            dprint("session err", args)

        if not error_handler:
            error_handler = err

        self.__client_interface.CreateSession(dest_addr, {"Source": source_addr, "Target": pattern},
                                              reply_handler=reply, error_handler=error_handler)

    def remove_session(self, session, reply_handler=None, error_handler=None):
        if not error_handler:
            def error_handler(*args):
                dprint("session err", args)
        self.__client_interface.RemoveSession(session.get_object_path(),
                                              reply_handler=reply_handler, error_handler=error_handler)

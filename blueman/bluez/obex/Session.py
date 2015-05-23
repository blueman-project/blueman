from blueman.bluez.obex.Base import Base


class Session(Base):
    def __init__(self, session_path):
        super(Session, self).__init__('org.freedesktop.DBus.Properties', session_path)

    @property
    def address(self):
        return self._call('Get', 'org.bluez.obex.Session1', 'Destination')

    @property
    def root(self):
        return self._call('Get', 'org.bluez.obex.Session1', 'Root')

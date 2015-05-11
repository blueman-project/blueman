from blueman.bluez.obex.Base import Base


class Session(Base):
    def __init__(self, session_path):
        if self.__class__.get_interface_version()[0] < 5:
            super(Session, self).__init__('org.bluez.obex.Session', session_path)
        else:
            super(Session, self).__init__('org.freedesktop.DBus.Properties', session_path)

    @property
    def address(self):
        if self.__class__.get_interface_version()[0] < 5:
            return self._interface.GetProperties()['Address']
        else:
            return self._interface.Get('org.bluez.obex.Session1', 'Destination')

    @property
    def root(self):
        if self.__class__.get_interface_version()[0] < 5:
            raise NotImplementedError()
        else:
            return self._interface.Get('org.bluez.obex.Session1', 'Root')

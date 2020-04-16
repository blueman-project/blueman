from blueman.bluez.Base import Base as BlueZBase
from gi.repository import Gio


class Base(BlueZBase):
    __bus_type = Gio.BusType.SESSION
    __name = 'org.bluez.obex'

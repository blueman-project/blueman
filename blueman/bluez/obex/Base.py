# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Base import Base as BlueZBase
from gi.repository import Gio


class Base(BlueZBase):
    __bus_type =Gio.BusType.SESSION
    __name = 'org.bluez.obex'

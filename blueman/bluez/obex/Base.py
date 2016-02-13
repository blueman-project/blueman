# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from blueman.bluez.Base import Base as BlueZBase


class Base(BlueZBase):
    __bus = dbus.SessionBus()
    __bus_name = 'org.bluez.obex'

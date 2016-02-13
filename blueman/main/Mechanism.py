# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import time
import dbus


class Mechanism(dbus.proxies.Interface):
    __inst__ = None

    def __new__(cls):
        if not Mechanism.__inst__:
            Mechanism.__inst__ = object.__new__(cls)

        return Mechanism.__inst__

    def __init__(self):
        self.bus = dbus.SystemBus()

        service = self.bus.get_object("org.blueman.Mechanism", "/", follow_name_owner_changes=True)
        super(Mechanism, self).__init__(service, "org.blueman.Mechanism")

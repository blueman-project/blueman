from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk


class Animation:
    def __init__(self, image, images, rate=1, rev=False):
        self.pixbuffs = []
        self.timer = None
        self.current = 0
        self.image = None

        self.image = image
        self.rate = 1000 / rate

        for i in range(len(images)):
            self.pixbuffs.append(images[i])

        if len(self.pixbuffs) > 2 and rev:
            ln = len(self.pixbuffs)
            for i in range(len(self.pixbuffs)):
                if i != 0 and i != ln - 1:
                    self.pixbuffs.append(self.pixbuffs[ln - 1 - i])


    def status(self):
        if self.timer:
            return True
        else:
            return False

    def get_rate(self):
        return self.rate * 1000

    def set_rate(self, rate):
        if not self.rate == (1000 / rate):
            self.rate = 1000 / rate
            self.stop()
            self.start()

    def start(self):
        self.timer = GObject.timeout_add(self.rate, self._animation)

    def stop(self):
        if self.timer:
            GObject.source_remove(self.timer)
            self.image.set_from_pixbuf(self.pixbuffs[0])
            self.timer = None

    def _animation(self):
        self.current += 1
        if self.current > (len(self.pixbuffs) - 1):
            self.current = 0
        if True:
            self.image.set_from_pixbuf(self.pixbuffs[self.current])
        # print "setting " + str(self.current)
        else:
            if self.current != 0:
                # self.image.set_from_pixbuf(self.pixbuffs[0])
                self.current = 0

        return 1


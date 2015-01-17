from gi.repository import Gtk
import math


class PixbufTable:
    def __init__(self, percol=2, spacingx=1, spacingy=1, size=24):
        self.percol = percol
        self.spacingx = spacingx
        self.spacingy = spacingy
        self.size = size

        self.cols = 0

        self.pixbuffs = {}

        self.recalc()


    def recalc(self):
        if len(self.pixbuffs) == 0:
            self.total_width = 0
            self.total_height = 0
            self.rows = 0
            self.cols = 0
            return

        self.cols = int(math.ceil(float(len(self.pixbuffs)) / self.percol))

        spacing_width = (self.cols - 1) * self.spacingx

        if len(self.pixbuffs) >= self.percol:
            self.rows = self.percol
        else:
            self.rows = len(self.pixbuffs)

        spacing_height = (self.rows - 1) * self.spacingy

        self.total_width = self.cols * self.size + spacing_width
        self.total_height = self.rows * self.size + spacing_height

    def get(self):
        return self.pixbuffs

    def set(self, name, pixbuf):
        if pixbuf != None:
            self.pixbuffs[name] = pixbuf
        else:
            if name in self.pixbuffs:
                del self.pixbuffs[name]
        self.recalc()



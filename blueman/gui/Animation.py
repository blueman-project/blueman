# coding=utf-8
from gi.repository import GLib


class Animation:
    def __init__(self, icon, icons, rate=1, rev=False):
        self.icon_names = []
        self.timer = None
        self.current = 0
        self.icon = icon
        self.rate = 1000 / rate

        for i in range(len(icons)):
            self.icon_names.append(icons[i])

        if len(self.icon_names) > 2 and rev:
            ln = len(self.icon_names)
            for i in range(len(self.icon_names)):
                if i != 0 and i != ln - 1:
                    self.icon_names.append(self.icon_names[ln - 1 - i])

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
        self.timer = GLib.timeout_add(self.rate, self._animation)

    def stop(self):
        if self.timer:
            GLib.source_remove(self.timer)
            self.icon.props.icon_name = self.icon_names[0]
            self.timer = None

    def _animation(self):
        self.current += 1
        if self.current > (len(self.icon_names) - 1):
            self.current = 0
        if True:
            self.icon.props.icon_name = self.icon_names[self.current]
        # print "setting " + str(self.current)
        else:
            if self.current != 0:
                # self.image.set_from_pixbuf(self.pixbuffs[0])
                self.current = 0

        return 1

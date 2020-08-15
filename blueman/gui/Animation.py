from gi.repository import GLib


class Animation:
    def __init__(self, icon, icons, rate=1):
        self.icon_names = list(icons)
        self.timer = None
        self.current = 0
        self.icon = icon
        self.rate = 1000 / rate

    def status(self):
        if self.timer:
            return True
        else:
            return False

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
        self.icon.props.icon_name = self.icon_names[self.current]

        return True

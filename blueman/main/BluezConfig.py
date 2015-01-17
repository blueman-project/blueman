from blueman.iniparse.compat import SafeConfigParser


class BluezConfig(SafeConfigParser):
    def __init__(self, filename):
        SafeConfigParser.__init__(self)

        self.filename = filename

        self.path = "/etc/bluetooth/%s" % filename

        self.read(self.path)

    def write(self):
        f = open(self.path, "wb")
        SafeConfigParser.write(self, f)

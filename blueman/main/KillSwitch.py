import dbus.proxies
import gobject
from blueman.main.HalManager import HalManager
from blueman.Functions import dprint


class WrongType(Exception):
    pass


class NotAKillSwitch(Exception):
    pass


class KillSwitch(dbus.proxies.Interface):
    class __Switch(dbus.proxies.Interface):
        def __init__(self, udi):
            bus = dbus.SystemBus()
            obj = bus.get_object('org.freedesktop.Hal', udi)
            dbus.proxies.Interface.__init__(self, obj, 'org.freedesktop.Hal.Device.KillSwitch')

    def __init__(self, udi):
        self.udi = udi
        bus = dbus.SystemBus()
        obj = bus.get_object('org.freedesktop.Hal', udi)
        dbus.proxies.Interface.__init__(self, obj, 'org.freedesktop.Hal.Device')
        if self.QueryCapability("killswitch"):
            t = self.GetPropertyString("killswitch.type")
            if t != "bluetooth":
                raise WrongType
        else:
            raise NotAKillSwitch

        self.__switch = KillSwitch.__Switch(udi)

        self.hard = 0
        self.idx = self.udi
        self.type = 2  # RfkillType.BLUETOOTH

    @property
    def soft(self):
        try:
            return not self.GetPower()
        except:
            return False

    def SetPower(self, state):
        try:
            self.__switch.SetPower(state)
        except dbus.DBusException:
            dprint("Failed to toggle killswitch")

    def GetPower(self):
        return self.__switch.GetPower()


class Manager(gobject.GObject):
    __inst = None
    __gsignals__ = {
    'switch-changed': (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    'switch-added': (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    'switch-removed': (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    def __new__(cls):
        if not Manager.__inst:
            return super(Manager, cls).__new__(cls)

        return Manager.__inst

    def __init__(self):
        if not Manager.__inst:
            gobject.GObject.__init__(self)
            Manager.__inst = self
            self.devices = []
            self.state = True
            self.HardBlocked = False
            dbus.SystemBus().watch_name_owner("org.freedesktop.Hal", self.hal_name_owner_changed)

    def hal_name_owner_changed(self, owner):
        for dev in self.devices:
            self.emit("switch-removed", dev)
        self.devices = []
        if owner != "":
            self.Hal = HalManager()
            self.__enumerate()
        else:
            self.Hal = None

    def __enumerate(self):
        self.state = True

        devs = self.Hal.FindDeviceByCapability("killswitch")
        for dev in devs:
            try:
                sw = KillSwitch(dev)
                self.devices.append(sw)
                self.state &= sw.GetPower()
                self.emit("switch-added", sw)
            except WrongType:
                pass

    def SetGlobalState(self, state, **kwargs):
        dprint("Setting killswitches to", state)

        for dev in self.devices:
            print("Setting", dev.udi, "to", state)
            dev.SetPower(state)
        if len(self.devices) == 0:
            self.state = True
        else:
            self.state = state

        if "reply_handler" in kwargs:
            kwargs["reply_handler"]()

    def GetGlobalState(self):
        try:
            self.state &= self.devices[0]
        except:
            return self.state
        else:
            return self.state



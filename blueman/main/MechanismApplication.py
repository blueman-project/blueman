import importlib
import logging
import os
from typing import Optional

import blueman.plugins.mechanism
from blueman.Constants import POLKIT
from gi.repository import GLib, Gio

from blueman.main.DbusService import DbusService, DbusError
from blueman.plugins.MechanismPlugin import MechanismPlugin


class Timer:
    def __init__(self, loop: GLib.MainLoop):
        self.time = 0
        self.stopped = False
        self._loop = loop
        GLib.timeout_add(1000, self.tick)

    def tick(self) -> bool:
        if not self.stopped:
            self.time += 1
            if self.time == (9999 if 'BLUEMAN_SOURCE' in os.environ else 30):
                logging.info("Exiting")
                self._loop.quit()

        return True

    def reset(self) -> None:
        self.time = 0

    def stop(self) -> None:
        self.stopped = True

    def resume(self) -> None:
        self.stopped = False
        self.reset()


class MechanismApplication(DbusService):
    def __init__(self, stoptimer: bool):
        super().__init__("org.blueman.Mechanism", "org.blueman.Mechanism", "/org/blueman/mechanism", Gio.BusType.SYSTEM)
        self._loop = GLib.MainLoop()
        self.timer = Timer(self._loop)
        if stoptimer:
            self.timer.stop()

        if POLKIT:
            try:
                self.pk: Optional[Gio.DBusProxy] = Gio.DBusProxy.new_for_bus_sync(
                    Gio.BusType.SYSTEM,
                    Gio.DBusProxyFlags.NONE,
                    None,
                    'org.freedesktop.PolicyKit1',
                    '/org/freedesktop/PolicyKit1/Authority',
                    'org.freedesktop.PolicyKit1.Authority')
            except Exception as e:
                logging.exception(e)
                self.pk = None
        else:
            self.pk = None

        path = os.path.dirname(blueman.plugins.mechanism.__file__)
        plugins = []
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".py") and not (f.endswith(".pyc") or f.endswith("_.py")):
                    plugins.append(f[0:-3])

        for plugin in plugins:
            try:
                importlib.import_module(f"blueman.plugins.mechanism.{plugin}")
            except ImportError:
                logging.error(f"Skipping plugin {plugin}", exc_info=True)

        classes = MechanismPlugin.__subclasses__()
        for cls in classes:
            logging.info(f"loading {cls.__name__}")
            cls(self)

        self.register()

    def run(self) -> None:
        self._loop.run()

    def confirm_authorization(self, subject: str, action_id: str) -> None:
        self.timer.reset()
        if not POLKIT:
            return
        else:
            if not self.pk:
                raise DbusError("Blueman was built with PolicyKit-1 support, but it's not available on the system")

        v_subject = GLib.Variant('s', subject)
        res = self.pk.CheckAuthorization('((sa{sv})sa{ss}us)', ("system-bus-name", {"name": v_subject}),
                                         action_id, {}, 1, "")

        logging.debug(str(res))
        (is_authorized, is_challenge, details) = res
        if not is_authorized:
            raise DbusError("Not authorized")

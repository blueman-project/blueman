from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config
from blueman.gui.Notification import Notification
from blueman.Sdp import *
from blueman.Lib import rfcomm_list
from blueman.main.SignalTracker import SignalTracker
from blueman.main.Device import Device
from subprocess import PIPE
import dbus
import atexit

import blueman.bluez as Bluez

from gi.repository import GObject
from gi.repository import Gtk


class SerialManager(AppletPlugin):
    __icon__ = "blueman-serial"
    __description__ = _("Standard SPP profile connection handler, allows executing custom actions")
    __author__ = "walmis"
    __options__ = {
    "script": {"type": str, "default": "",
               "name": _("Script to execute on connection"),
               "desc": _("<span size=\"small\">The following arguments will be passed:\n"
                         "Address, Name, service name, uuid16s, rfcomm node\n"
                         "For example:\n"
                         "AA:BB:CC:DD:EE:FF, Phone, DUN service, 0x1103, /dev/rfcomm0\n"
                         "uuid16s are returned as a comma seperated list\n\n"
                         "Upon device disconnection the script will be sent a HUP signal</span>")},
    }

    def on_load(self, applet):
        self.signals = SignalTracker()
        self.signals.Handle('bluez', Bluez.Device(), self.on_device_property_changed, 'PropertyChanged',
                            path_keyword="path")

        self.scripts = {}

    def on_unload(self):
        self.signals.DisconnectAll()
        for k in self.scripts.keys():
            self.terminate_all_scripts(k)

    def on_device_property_changed(self, key, value, path):
        if key == "Connected" and not value:
            d = Device(path)
            self.terminate_all_scripts(d.Address)

    def on_rfcomm_connected(self, device, port, uuid):
        uuid16 = sdp_get_serial_type(device.Address, uuid)
        if SERIAL_PORT_SVCLASS_ID in uuid16:
            Notification(_("Serial port connected"),
                         _("Serial port service on device <b>%s</b> now will be available via <b>%s</b>") % (
                         device.Alias, port),
                         pixbuf=get_icon("blueman-serial", 48),
                         status_icon=self.Applet.Plugins.StatusIcon)

            self.call_script(device.Address,
                             device.Alias,
                             sdp_get_serial_name(device.Address, uuid),
                             uuid16,
                             port)

    def terminate_all_scripts(self, address):
        try:
            for p in self.scripts[address].values():
                dprint("Sending HUP to", p.pid)
                os.killpg(p.pid, signal.SIGHUP)
        except:
            pass

    def on_script_closed(self, pid, cond, (address, node)):
        del self.scripts[address][node]
        dprint("Script with PID", pid, "closed")

    def manage_script(self, address, node, process):
        if not address in self.scripts:
            self.scripts[address] = {}

        if node in self.scripts[address]:
            self.scripts[address][node].terminate()

        self.scripts[address][node] = process
        GObject.child_watch_add(process.pid, self.on_script_closed, (address, node))

    def call_script(self, address, name, sv_name, uuid16, node):
        c = self.get_option("script")
        if c and c != "":
            args = c.split(" ")
            try:
                args += [address, name, sv_name, ",".join(map(lambda x: hex(x), uuid16)), node]
                dprint(args)
                p = spawn(args, True, reap=False, preexec_fn=lambda: os.setpgid(0, 0))

                self.manage_script(address, node, p)


            except Exception as e:
                Notification(_("Serial port connection script failed"),
                             _("There was a problem launching script %s\n"
                               "%s") % (c, str(e)),
                             pixbuf=get_icon("blueman-serial", 48),
                             status_icon=self.Applet.Plugins.StatusIcon)

    def on_rfcomm_disconnect(self, node):
        for k, v in self.scripts.items():
            if node in v:
                dprint("Sending HUP to", v[node].pid)
                os.killpg(v[node].pid, signal.SIGHUP)

    def rfcomm_connect_handler(self, device, uuid, reply, err):
        uuid16 = sdp_get_serial_type(device.Address, uuid)

        if SERIAL_PORT_SVCLASS_ID in uuid16:
            device.Services["serial"].Connect(uuid, reply_handler=reply, error_handler=err)

            return True
        else:
            return False

    def on_device_disconnect(self, device):
        self.terminate_all_scripts(device.Address)

        if "serial" in device.Services:
            ports = rfcomm_list()

            def flt(dev):
                if dev["dst"] == device.Address and dev["state"] == "connected":
                    return dev["id"]

            active_ports = map(flt, ports)

            serial = device.Services["serial"]

            for port in active_ports:
                name = "/dev/rfcomm%d" % port
                try:
                    dprint("Disconnecting", name)
                    serial.Disconnect(name)
                except:
                    dprint("Failed to disconnect", name)


@atexit.register
def exit_cleanup():
    if SerialManager.__instance__:
        self = SerialManager.__instance__

        for k in self.scripts.keys():
            self.terminate_all_scripts(k)

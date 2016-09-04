from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.Sdp import uuid128_to_uuid16, uuid16_to_name, SERIAL_PORT_SVCLASS_ID
from _blueman import rfcomm_list
from blueman.main.SignalTracker import SignalTracker
from blueman.main.Device import Device
from subprocess import Popen, PIPE
import dbus
import atexit

import blueman.bluez as Bluez

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk


class SerialManager(AppletPlugin):
    __icon__ = "blueman-serial"
    __description__ = _("Standard SPP profile connection handler, allows executing custom actions")
    __author__ = "walmis"

    __gsettings__ = {
        "schema": "org.blueman.plugins.serialmanager",
        "path": None
    }
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

    scripts = {}

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

    def on_rfcomm_connected(self, service, port):
        device = service.device
        uuid16 = uuid128_to_uuid16(service.uuid)
        if SERIAL_PORT_SVCLASS_ID == uuid16:
            Notification(_("Serial port connected"),
                         _("Serial port service on device <b>%s</b> now will be available via <b>%s</b>") % (
                         device.Alias, port),
                         pixbuf=get_icon("blueman-serial", 48),
                         status_icon=self.Applet.Plugins.StatusIcon)

            self.call_script(device.Address,
                             device.Alias,
                             uuid16_to_name(uuid16),
                             uuid16,
                             port)

    def terminate_all_scripts(self, address):
        try:
            for p in self.scripts[address].values():
                dprint("Sending HUP to", p.pid)
                os.killpg(p.pid, signal.SIGHUP)
        except:
            pass

    def on_script_closed(self, pid, cond, address_node):
        address, node = address_node
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
                args += [address, name, sv_name, "%s" % hex(uuid16), node]
                dprint(args)
                p = Popen(args, preexec_fn=lambda: os.setpgid(0, 0))

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

    def rfcomm_connect_handler(self, service, reply, err):
        if SERIAL_PORT_SVCLASS_ID == uuid128_to_uuid16(service.uuid):
            service.connect(reply_handler=reply, error_handler=err)
            return True
        else:
            return False

    def on_device_disconnect(self, device):
        self.terminate_all_scripts(device.Address)

        serial_services = [service for service in device.get_services() if service.group == 'serial']

        if not serial_services:
            return

        ports = rfcomm_list()

        def flt(dev):
            if dev["dst"] == device.Address and dev["state"] == "connected":
                return dev["id"]

        active_ports = map(flt, ports)

        for port in active_ports:
            if port is None:
                continue

            name = "/dev/rfcomm%d" % port
            try:
                dprint("Disconnecting", name)
                serial_services[0].disconnect(port)
            except Exception as e:
                dprint("Failed to disconnect", name)
                dprint(e)


@atexit.register
def exit_cleanup():
    if SerialManager.__instance__:
        self = SerialManager.__instance__

        for k in self.scripts.keys():
            self.terminate_all_scripts(k)

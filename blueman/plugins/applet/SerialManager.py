# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.Sdp import SERIAL_PORT_SVCLASS_ID
from blueman.services.Functions import get_services
from _blueman import rfcomm_list
from subprocess import Popen
import atexit
import logging
import os
import signal
import blueman.bluez as Bluez
from gi.repository import GObject


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
        self.scripts = {}

    def on_unload(self):
        for k in self.scripts.keys():
            self.terminate_all_scripts(k)

    def on_device_property_changed(self, path, key, value):
        if key == "Connected" and not value:
            self.terminate_all_scripts(Bluez.Device(path)["Address"])

    def on_rfcomm_connected(self, service, port):
        device = service.device
        if SERIAL_PORT_SVCLASS_ID == service.short_uuid:
            Notification(_("Serial port connected"),
                         _("Serial port service on device <b>%s</b> now will be available via <b>%s</b>") % (
                         device['Alias'], port),
                         icon_name="blueman-serial").show()

            self.call_script(device['Address'],
                             device['Alias'],
                             service.name,
                             service.short_uuid,
                             port)

    def terminate_all_scripts(self, address):
        try:
            for p in self.scripts[address].values():
                logging.info("Sending HUP to %s" % p.pid)
                os.killpg(p.pid, signal.SIGHUP)
        except:
            pass

    def on_script_closed(self, pid, cond, address_node):
        address, node = address_node
        del self.scripts[address][node]
        logging.info("Script with PID %s closed" % pid)

    def manage_script(self, address, node, process):
        if address not in self.scripts:
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
                logging.debug(" ".join(args))
                p = Popen(args, preexec_fn=lambda: os.setpgid(0, 0))

                self.manage_script(address, node, p)

            except Exception as e:
                Notification(_("Serial port connection script failed"),
                             _("There was a problem launching script %s\n"
                               "%s") % (c, str(e)),
                             icon_name="blueman-serial").show()

    def on_rfcomm_disconnect(self, node):
        for k, v in self.scripts.items():
            if node in v:
                logging.info("Sending HUP to %s" % v[node].pid)
                os.killpg(v[node].pid, signal.SIGHUP)

    def rfcomm_connect_handler(self, service, reply, err):
        if SERIAL_PORT_SVCLASS_ID == service.short_uuid:
            service.connect(reply_handler=reply, error_handler=err)
            return True
        else:
            return False

    def on_device_disconnect(self, device):
        self.terminate_all_scripts(device['Address'])

        serial_services = [service for service in get_services(device) if service.group == 'serial']

        if not serial_services:
            return

        ports = rfcomm_list()

        def flt(dev):
            if dev["dst"] == device['Address'] and dev["state"] == "connected":
                return dev["id"]

        active_ports = map(flt, ports)

        for port in active_ports:
            if port is None:
                continue

            name = "/dev/rfcomm%d" % port
            try:
                logging.info("Disconnecting %s" % name)
                serial_services[0].disconnect(port)
            except Exception:
                logging.error("Failed to disconnect %s" % name, exc_info=True)


@atexit.register
def exit_cleanup():
    if SerialManager.__instance__:
        self = SerialManager.__instance__

        for k in self.scripts.keys():
            self.terminate_all_scripts(k)

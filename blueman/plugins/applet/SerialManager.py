# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.Sdp import SERIAL_PORT_SVCLASS_ID
from blueman.services.Functions import get_services
from _blueman import rfcomm_list
from subprocess import Popen
import logging
import os
import signal
import blueman.bluez as bluez
from gi.repository import GLib


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

    def on_load(self):
        self.scripts = {}

    def on_unload(self):
        for bdaddr in self.scripts.keys():
            self.terminate_all_scripts(bdaddr)

    def on_delete(self):
        logging.debug("Terminating any running scripts")
        for bdaddr in self.scripts:
            self.terminate_all_scripts(bdaddr)

    def on_device_property_changed(self, path, key, value):
        if key == "Connected" and not value:
            device = bluez.Device(path)
            self.terminate_all_scripts(device["Address"])
            self.on_device_disconnect(device)

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
        if address not in self.scripts:
            # Script already terminated or failed to start
            return

        for p in self.scripts[address].values():
            logging.info("Sending HUP to %s" % p.pid)
            try:
                os.killpg(p.pid, signal.SIGHUP)
            except ProcessLookupError:
                logging.debug("No process found for pid %s" % p.pid)

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
        GLib.child_watch_add(process.pid, self.on_script_closed, (address, node))

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
                logging.debug(str(e))
                Notification(_("Serial port connection script failed"),
                             _("There was a problem launching script %s\n"
                               "%s") % (c, str(e)),
                             icon_name="blueman-serial").show()

    def on_rfcomm_disconnect(self, port):
        node = '/dev/rfcomm%i' % port
        for bdaddr, scripts in self.scripts.items():
            process = scripts.get(node)
            if process:
                logging.info("Sending HUP to %s" % process.pid)
                os.killpg(process.pid, signal.SIGHUP)

    def rfcomm_connect_handler(self, service, reply, err):
        if SERIAL_PORT_SVCLASS_ID == service.short_uuid:
            service.connect(reply_handler=reply, error_handler=err)
            return True
        else:
            return False

    def on_device_disconnect(self, device):
        serial_services = [service for service in get_services(device) if service.group == 'serial']

        if not serial_services:
            return

        active_ports = [rfcomm['id'] for rfcomm in rfcomm_list() if rfcomm['dst'] == device['Address']]

        for port in active_ports:
            name = "/dev/rfcomm%d" % port
            try:
                logging.info("Disconnecting %s" % name)
                serial_services[0].disconnect(port)
            except GLib.Error:
                logging.error("Failed to disconnect %s" % name, exc_info=True)

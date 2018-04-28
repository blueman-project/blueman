from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from io import open

import pickle
import os
import signal
import errno
import re
from socket import inet_aton, inet_ntoa
from blueman.Constants import *
from blueman.Functions import have, mask_ip4_address, dprint, is_running
from _blueman import create_bridge, destroy_bridge, BridgeException
from subprocess import call, Popen


class NetworkSetupError(Exception):
    pass


def calc_ip_range(ip):
    '''Calculate the ip range for dhcp config'''
    start_range = bytearray(ip)
    end_range = bytearray(ip)
    start_range[3] += 1
    end_range[3] = 254

    return bytes(start_range), bytes(end_range)

def read_pid_file(fname):
    try:
        with open(fname, "r") as f:
            pid = int(f.read())
    except (IOError, ValueError):
        pid = None

    return pid

class DnsMasqHandler(object):
    def __init__(self, netconf):
        self.pid = None
        self.netconf = netconf

    def do_apply(self):
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            if 1:
                rtr = "--dhcp-option=option:router,%s" % inet_ntoa(self.netconf.ip4_address)
            else:
                rtr = "--dhcp-option=3 --dhcp-option=6"  # no route and no dns

            start, end = calc_ip_range(self.netconf.ip4_address)

            args = "--pid-file=/var/run/dnsmasq.pan1.pid --bind-interfaces --dhcp-range=%s,%s,60m --except-interface=lo --interface=pan1 %s" % (inet_ntoa(start), inet_ntoa(end), rtr)

            cmd = [have("dnsmasq")] + args.split(" ")
            dprint(cmd)
            p = Popen(cmd)

            ret = p.wait()

            if ret == 0:
                dprint("Dnsmasq started correctly")
                f = open("/var/run/dnsmasq.pan1.pid", "r")
                self.pid = int(f.read())
                f.close()
                dprint("pid", self.pid)
                self.netconf.lock("dhcp")
            else:
                raise NetworkSetupError("dnsmasq failed to start. Check the system log for errors")


    def do_remove(self):
        if self.netconf.locked("dhcp"):
            if not self.pid:
                pid = read_pid_file("/var/run/dnsmasq.pan1.pid")
            else:
                pid = self.pid

            if pid and is_running("dnsmasq", pid):
                os.kill(pid, signal.SIGTERM)
                self.netconf.unlock("dhcp")
            else:
                dprint("Stale dhcp lockfile found")
                self.netconf.unlock("dhcp")

class DhcpdHandler(object):
    def __init__(self, netconf):
        self.pid = None
        self.netconf = netconf

    def _read_dhcp_config(self):
        f = open(DHCP_CONFIG_FILE, "r")
        insection = False
        dhcp_config = ""
        existing_subnet = ""
        for line in f:
            if line == "#### BLUEMAN AUTOMAGIC SUBNET ####\n":
                insection = True

            if line == "#### END BLUEMAN AUTOMAGIC SUBNET ####\n":
                insection = False

            if not insection:
                dhcp_config += line
            else:
                existing_subnet += line

        f.close()

        return (dhcp_config, existing_subnet)

    def get_dns_servers(self):
        dns_servers = []
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                match = re.search("^nameserver (.*)", line)
                if match:
                    server = match.group(1)
                    if ":" not in server:  # Exclude ipv6
                        dns_servers.append(server)

        return ", ".join(dns_servers)

    def _generate_subnet_config(self):
        dns = self.get_dns_servers()

        masked_ip = mask_ip4_address(self.netconf.ip4_address, self.netconf.ip4_mask)

        start, end = calc_ip_range(self.netconf.ip4_address)

        subnet = "#### BLUEMAN AUTOMAGIC SUBNET ####\n"
        subnet += "# Everything inside this section is destroyed after config change\n"
        subnet += """subnet %(ip_mask)s netmask %(netmask)s {
                option domain-name-servers %(dns)s;
                option subnet-mask %(netmask)s;
                option routers %(rtr)s;
                range %(start)s %(end)s;
                }\n""" % {"ip_mask": inet_ntoa(masked_ip),
                          "netmask": inet_ntoa(self.netconf.ip4_mask),
                          "dns": dns,
                          "rtr": inet_ntoa(self.netconf.ip4_address),
                          "start": inet_ntoa(start),
                          "end": inet_ntoa(end)
        }
        subnet += "#### END BLUEMAN AUTOMAGIC SUBNET ####\n"

        return subnet

    def do_apply(self):
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            dhcp_config, existing_subnet = self._read_dhcp_config()

            subnet = self._generate_subnet_config()

            # if subnet != self.existing_subnet:
            f = open(DHCP_CONFIG_FILE, "w")
            f.write(dhcp_config)
            f.write(subnet)
            f.close()

            cmd = [have("dhcpd3") or have("dhcpd"), "-pf", "/var/run/dhcpd.pan1.pid", "pan1"]
            p = Popen(cmd)

            ret = p.wait()

            if ret == 0:
                dprint("dhcpd started correctly")
                f = open("/var/run/dhcpd.pan1.pid", "r")
                self.pid = int(f.read())
                f.close()
                dprint("pid", self.pid)
                self.netconf.lock("dhcp")
            else:
                raise NetworkSetupError("dhcpd failed to start. Check the system log for errors")


    def do_remove(self):
        dhcp_config, existing_subnet = self._read_dhcp_config()
        f = open(DHCP_CONFIG_FILE, "w")
        f.write(dhcp_config)
        f.close()

        if self.netconf.locked("dhcp"):
            if not self.pid:
                pid = read_pid_file("/var/run/dhcpd.pan1.pid")
            else:
                pid = self.pid

            if pid and (is_running("dhcpd3", pid) or is_running("dhcpd", pid)):
                os.kill(pid, signal.SIGTERM)
                self.netconf.unlock("dhcp")
            else:
                dprint("Stale dhcp lockfile found")
                self.netconf.unlock("dhcp")

class_id = 10


class NetConf(object):
    default_inst = None

    @classmethod
    def get_default(cls):
        if NetConf.default_inst:
            return NetConf.default_inst

        try:
            f = open("/var/lib/blueman/network.state", "rb")
            obj = pickle.load(f)
            if obj.version != class_id:
                raise Exception
            NetConf.default_inst = obj
            f.close()
            return obj
        except (IOError, UnicodeDecodeError):
            n = cls()
            try:
                n.store()
            except:
                return n
            NetConf.default_inst = n
            return n

    def __init__(self):
        dprint()
        self.version = class_id
        self.dhcp_handler = None
        self.ipt_rules = []

        self.ip4_address = None
        self.ip4_mask = None
        self.ip4_changed = False


    def set_ipv4(self, ip, netmask):
        if self.ip4_address != ip or self.ip4_mask != netmask:
            self.ip4_changed = True

        self.ip4_address = ip
        self.ip4_mask = netmask

    def get_ipv4(self):
        return (self.ip4_address, self.ip4_mask)

    def enable_ip4_forwarding(self):
        f = open("/proc/sys/net/ipv4/ip_forward", "w")
        f.write("1")
        f.close()

        for d in os.listdir("/proc/sys/net/ipv4/conf"):
            f = open("/proc/sys/net/ipv4/conf/%s/forwarding" % d, "w")
            f.write("1")
            f.close()

    def add_ipt_rule(self, table, chain, rule):
        self.ipt_rules.append((table, chain, rule))
        args = ["/sbin/iptables", "-t", table, "-A", chain] + rule.split(" ")
        dprint(" ".join(args))
        ret = call(args)
        print("Return code", ret)

    def del_ipt_rules(self):
        for table, chain, rule in self.ipt_rules:
            call(["/sbin/iptables", "-t", table, "-D", chain] + rule.split(" "))
        self.ipt_rules = []
        self.unlock("iptables")

    def set_dhcp_handler(self, handler):
        if not isinstance(self.dhcp_handler, handler):
            running = False
            if self.dhcp_handler:
                self.dhcp_handler.do_remove()
                running = True

            self.dhcp_handler = handler(self)
            if running:
                self.dhcp_handler.do_apply()

    def get_dhcp_handler(self):
        if not self.dhcp_handler:
            return None

        return type(self.dhcp_handler)

    def apply_settings(self):
        if self.ip4_address == None or self.ip4_mask == None:
            if self.ip4_changed:
                self.ip4_changed = False
            self.store()
            return

        if self != NetConf.get_default():
            NetConf.get_default().remove_settings()
            NetConf.default_inst = self

        try:
            create_bridge("pan1")
        except BridgeException as e:
            if e.errno != errno.EEXIST:
                raise

        ip_str = inet_ntoa(self.ip4_address)
        mask_str = inet_ntoa(self.ip4_mask)

        if self.ip4_changed or not self.locked("netconfig"):
            self.enable_ip4_forwarding()

            if have("ip"):
                ret = call(["ip", "link", "set", "dev", "pan1", "up"])
                if ret != 0:
                    raise NetworkSetupError("Failed to bring up interface pan1")
                ret = call(["ip", "address", "add", "/".join((ip_str, mask_str)), "dev", "pan1"])
                if ret != 0:
                    raise NetworkSetupError("Failed to add ip address %s with netmask %s" % (ip_str, mask_str))
            elif have('ifconfig'):
                ret = call(["ifconfig", "pan1", ip_str, "netmask", mask_str, "up"])
                if ret != 0:
                    raise NetworkSetupError("Failed to add ip address %s with netmask %s" % (ip_str, mask_str))
            else:
                raise NetworkSetupError(
                    "Neither ifconfig or ip commands are found. Please install net-tools or iproute2")

            self.lock("netconfig")

        if self.ip4_changed or not self.locked("iptables"):
            self.del_ipt_rules()

            self.add_ipt_rule("nat", "POSTROUTING", "-s %s/%s -j MASQUERADE" % (ip_str, mask_str))
            self.add_ipt_rule("filter", "FORWARD", "-i pan1 -j ACCEPT")
            self.add_ipt_rule("filter", "FORWARD", "-o pan1 -j ACCEPT")
            self.add_ipt_rule("filter", "FORWARD", "-i pan1 -j ACCEPT")
            self.lock("iptables")

        if self.dhcp_handler:
            self.dhcp_handler.do_apply()
        self.ip4_changed = False

        self.store()

    def remove_settings(self):
        dprint(self)

        if self.dhcp_handler:
            self.dhcp_handler.do_remove()

        try:
            destroy_bridge("pan1")
        except:
            pass
        self.unlock("netconfig")

        self.del_ipt_rules()

        self.store()

    def lock(self, key):
        f = open("/var/run/blueman-%s" % key, "w")
        f.close()

    def unlock(self, key):
        try:
            os.unlink("/var/run/blueman-%s" % key)
        except:
            pass

    def locked(self, key):
        return os.path.exists("/var/run/blueman-%s" % key)

    # save the instance of this class, requires root
    def store(self):
        if not os.path.exists("/var/lib/blueman"):
            os.mkdir("/var/lib/blueman")
        f = open("/var/lib/blueman/network.state", "wb")
        pickle.dump(self, f, 2)
        f.close()

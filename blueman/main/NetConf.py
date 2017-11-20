# coding=utf-8
import pickle
import signal
import errno
import re
import os
from socket import inet_ntoa
from tempfile import mkstemp
from time import sleep
import logging
from blueman.Constants import DHCP_CONFIG_FILE
from blueman.Functions import have, mask_ip4_address, is_running
from _blueman import create_bridge, destroy_bridge, BridgeException
from subprocess import call, Popen, PIPE


class NetworkSetupError(Exception):
    pass


def calc_ip_range(ip):
    """Calculate the ip range for dhcp config"""
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


def get_dns_servers():
    f = open("/etc/resolv.conf", "r")
    dns_servers = ""
    for line in f:
        server = re.search("^nameserver ((?:[0-9]{1,3}\.){3}[0-9]{1,3}$)", line)
        if server:
            dns_servers += "%s, " % server.groups(1)[0]

    dns_servers = dns_servers.strip(", ")

    f.close()

    return dns_servers


class DnsMasqHandler(object):
    def __init__(self, netconf):
        self.pid = None
        self.netconf = netconf

    def do_apply(self):
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            start, end = calc_ip_range(self.netconf.ip4_address)
            cmd = [have("dnsmasq"), "--pid-file=/var/run/dnsmasq.pan1.pid", "--except-interface=lo",
                   "--interface=pan1", "--bind-interfaces",
                   "--dhcp-range=%s,%s,60m" % (inet_ntoa(start), inet_ntoa(end)),
                   "--dhcp-option=option:router,%s" % inet_ntoa(self.netconf.ip4_address)]

            logging.info(cmd)
            p = Popen(cmd, stderr=PIPE)

            error = p.communicate()[1]

            if not error:
                logging.info("Dnsmasq started correctly")
                f = open("/var/run/dnsmasq.pan1.pid", "r")
                self.pid = int(f.read())
                f.close()
                logging.info("pid %s" % self.pid)
                self.netconf.lock("dhcp")
            else:
                error_msg = error.decode("UTF-8").strip()
                logging.info(error_msg)
                raise NetworkSetupError("dnsmasq failed to start: %s" % error_msg)

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
                logging.info("Stale dhcp lockfile found")
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

    def _generate_subnet_config(self):
        dns = get_dns_servers()

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
                          "end": inet_ntoa(end)}
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
            p = Popen(cmd, stderr=PIPE)

            error = p.communicate()[1]

            if not error:
                logging.info("dhcpd started correctly")
                f = open("/var/run/dhcpd.pan1.pid", "r")
                self.pid = int(f.read())
                f.close()
                logging.info("pid %s" % self.pid)
                self.netconf.lock("dhcp")
            else:
                error_msg = error.decode("UTF-8").strip()
                logging.info(error_msg)
                raise NetworkSetupError("dhcpd failed to start: %s " % error_msg)

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
                logging.info("Stale dhcp lockfile found")
                self.netconf.unlock("dhcp")


class UdhcpdHandler(object):
    def __init__(self, netconf):
        self.pid = None
        self.netconf = netconf

    def _generate_config(self):
        dns = get_dns_servers()

        masked_ip = mask_ip4_address(self.netconf.ip4_address, self.netconf.ip4_mask)

        start, end = calc_ip_range(self.netconf.ip4_address)

        return """start %(start)s
end %(end)s
interface pan1
pidfile /var/run/udhcpd.pan1.pid
option subnet %(ip_mask)s
option dns %(dns)s
option router %(rtr)s
""" % {"ip_mask": inet_ntoa(masked_ip),
       "dns": dns,
       "rtr": inet_ntoa(self.netconf.ip4_address),
       "start": inet_ntoa(start),
       "end": inet_ntoa(end)
       }

    def do_apply(self):
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            config_file, config_path = mkstemp(prefix="udhcpd-")
            os.write(config_file, self._generate_config().encode('UTF-8'))
            os.close(config_file)

            logging.info("Running udhcpd with config file %s" % config_path)
            cmd = [have("udhcpd"), "-S", config_path]
            p = Popen(cmd, stderr=PIPE)
            error = p.communicate()[1]

            # udhcpd takes time to create pid file
            sleep(0.1)

            pid = read_pid_file("/var/run/udhcpd.pan1.pid")

            if p.pid and is_running("udhcpd", pid):
                logging.info("udhcpd started correctly")
                self.pid = pid
                logging.info("pid %s" % self.pid)
                self.netconf.lock("dhcp")
            else:
                error_msg = error.decode("UTF-8").strip()
                logging.info(error_msg)
                raise NetworkSetupError("udhcpd failed to start: %s" % error_msg)

            os.remove(config_path)

    def do_remove(self):
        if self.netconf.locked("dhcp"):
            if not self.pid:
                pid = read_pid_file("/var/run/udhcpd.pan1.pid")
            else:
                pid = self.pid

            if pid and is_running("udhcpd", pid):
                os.kill(pid, signal.SIGTERM)
                self.netconf.unlock("dhcp")
            else:
                logging.info("Stale dhcp lockfile found")
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
        logging.info("init")
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
        logging.debug(" ".join(args))
        ret = call(args)
        logging.info("Return code %s" % ret)

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
        if self.ip4_address is None or self.ip4_mask is None:
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
            else:
                ret = call(["ifconfig", "pan1", ip_str, "netmask", mask_str, "up"])
                if ret != 0:
                    raise NetworkSetupError("Failed to add ip address %s with netmask %s" % (ip_str, mask_str))

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
        logging.info(self)

        if self.dhcp_handler:
            self.dhcp_handler.do_remove()

        try:
            destroy_bridge("pan1")
        except BridgeException:
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
        except OSError:
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

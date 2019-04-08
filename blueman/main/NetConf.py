# coding=utf-8
import pickle
import errno
import re
import os
import ipaddress
from pickle import UnpicklingError
from tempfile import mkstemp
from time import sleep
import logging
from blueman.Constants import DHCP_CONFIG_FILE
from blueman.Functions import have, is_running, kill
from _blueman import create_bridge, destroy_bridge, BridgeException
from subprocess import call, Popen, PIPE


class NetworkSetupError(Exception):
    pass


def read_pid_file(fname):
    try:
        with open(fname, "r") as f:
            pid = int(f.read())
    except (IOError, ValueError):
        pid = None

    return pid


def get_dns_servers():
    dns_servers = ''
    with open("/etc/resolv.conf", "r") as f:
        for line in f:
            match = re.search(r"^nameserver ((?:[0-9]{1,3}\.){3}[0-9]{1,3}$)", line)
            if match:
                dns_servers += "%s, " % match.group(1)

        dns_servers = dns_servers.strip(", ")

    return dns_servers


class DnsMasqHandler(object):
    def __init__(self, netconf):
        self.pid = None
        self.netconf = netconf

    def do_apply(self):
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            ipiface = ipaddress.ip_interface('/'.join((self.netconf.ip4_address, '255.255.255.0')))
            cmd = [have("dnsmasq"), "--port=0", "--pid-file=/var/run/dnsmasq.pan1.pid", "--except-interface=lo",
                   "--interface=pan1", "--bind-interfaces",
                   "--dhcp-range=%s,%s,60m" % (ipiface.network[2], ipiface.network[-2]),
                   "--dhcp-option=option:router,%s" % self.netconf.ip4_address]

            logging.info(cmd)
            p = Popen(cmd, stderr=PIPE)

            error = p.communicate()[1]

            if not error:
                logging.info("Dnsmasq started correctly")
                with open("/var/run/dnsmasq.pan1.pid", "r") as f:
                    self.pid = int(f.read())
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

            if not kill(pid, 'dnsmasq'):
                logging.info("Stale dhcp lockfile found")
            self.netconf.unlock("dhcp")


DHCPDSUBNET = '''#### BLUEMAN AUTOMAGIC SUBNET ####
# Everything inside this section is destroyed after config change
subnet %(ip_mask)s netmask %(netmask)s {
  option domain-name-servers %(dns)s;
  option subnet-mask %(netmask)s;
  option routers %(rtr)s;
  range %(start)s %(end)s;
}
#### END BLUEMAN AUTOMAGIC SUBNET ####'''


class DhcpdHandler(object):
    def __init__(self, netconf):
        self.pid = None
        self.netconf = netconf

    @staticmethod
    def _read_dhcp_config():
        dhcp_config = ''
        existing_subnet = ''
        start = end = False

        with open(DHCP_CONFIG_FILE, 'r') as f:
            for line in f:
                if line == '#### BLUEMAN AUTOMAGIC SUBNET ####\n':
                    start = True
                elif line == '#### END BLUEMAN AUTOMAGIC SUBNET ####\n':
                    if not start:
                        # Because of bug end string got left upon removal
                        continue
                    end = True

                if start and not end:
                    existing_subnet += line
                elif start and end:
                    existing_subnet += line
                    start = end = False
                else:
                    dhcp_config += line

        return dhcp_config, existing_subnet

    def _generate_subnet_config(self):
        dns = get_dns_servers()

        ipiface = ipaddress.ip_interface('/'.join((self.netconf.ip4_address, self.netconf.ip4_mask)))

        return DHCPDSUBNET % {"ip_mask": ipiface.network.network_address,
                              "netmask": ipiface.netmask,
                              "dns": dns,
                              "rtr": ipiface.ip,
                              "start": ipiface.network[2],
                              "end": ipiface.network[-2]}

    def do_apply(self):
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            dhcp_config, existing_subnet = self._read_dhcp_config()

            subnet = self._generate_subnet_config()

            # if subnet != self.existing_subnet:
            with open(DHCP_CONFIG_FILE, "w") as f:
                f.write(dhcp_config)
                f.write(subnet)

            cmd = [have("dhcpd3") or have("dhcpd"), "-pf", "/var/run/dhcpd.pan1.pid", "pan1"]
            p = Popen(cmd, stderr=PIPE)

            error = p.communicate()[1]

            if p.returncode == 0:
                logging.info("dhcpd started correctly")
                with open("/var/run/dhcpd.pan1.pid", "r") as f:
                    self.pid = int(f.read())
                logging.info("pid %s" % self.pid)
                self.netconf.lock("dhcp")
            else:
                error_msg = error.decode("UTF-8").strip()
                logging.info(error_msg)
                raise NetworkSetupError("dhcpd failed to start: %s " % error_msg)

    def do_remove(self):
        dhcp_config, existing_subnet = self._read_dhcp_config()
        with open(DHCP_CONFIG_FILE, "w") as f:
            f.write(dhcp_config)

        if self.netconf.locked("dhcp"):
            if not self.pid:
                pid = read_pid_file("/var/run/dhcpd.pan1.pid")
            else:
                pid = self.pid

            if not kill(pid, 'dhcpd3') and not kill(pid, 'dhcpd'):
                logging.info("Stale dhcp lockfile found")
            self.netconf.unlock("dhcp")


UDHCP_CONF_TEMPLATE = """start %(start)s
end %(end)s
interface pan1
pidfile /var/run/udhcpd.pan1.pid
option subnet %(ip_mask)s
option dns %(dns)s
option router %(rtr)s
"""


class UdhcpdHandler(object):
    def __init__(self, netconf):
        self.pid = None
        self.netconf = netconf

    def _generate_config(self):
        dns = get_dns_servers()

        ipiface = ipaddress.ip_interface('/'.join((self.netconf.ip4_address, self.netconf.ip4_mask)))

        return UDHCP_CONF_TEMPLATE % {"ip_mask": ipiface.network.network_address,
                                      "dns": dns,
                                      "rtr": ipiface.ip,
                                      "start": ipiface.network[2],
                                      "end": ipiface.network[-2]}

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

            if not kill(pid, 'udhcpd'):
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
            with open("/var/lib/blueman/network.state", "rb") as f:
                obj = pickle.load(f)
                if obj.version != class_id:
                    raise Exception

                # Convert old 32bit packed ip's to strings
                if not isinstance(obj.ip4_address, str) and obj.ip4_address is not None:
                    obj.ip4_address = str(ipaddress.ip_address(obj.ip4_address))
                    obj.ip4_mask = '255.255.255.0'

                NetConf.default_inst = obj
                return obj
        except (IOError, UnicodeDecodeError, UnpicklingError):
            n = cls()
            try:
                n.store()
            # FIXME find out what could go wrong and drop bare exception
            except:  # noqa: E722
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
        return self.ip4_address, self.ip4_mask

    @staticmethod
    def enable_ip4_forwarding():
        with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
            f.write("1")

        for d in os.listdir("/proc/sys/net/ipv4/conf"):
            with open("/proc/sys/net/ipv4/conf/%s/forwarding" % d, "w") as f:
                f.write("1")

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
        if self != NetConf.get_default():
            NetConf.get_default().remove_settings()
            NetConf.default_inst = self

        try:
            create_bridge("pan1")
        except BridgeException as e:
            if e.errno != errno.EEXIST:
                raise

        if self.ip4_changed or not self.locked("netconfig"):
            self.enable_ip4_forwarding()

            if have("ip"):
                ret = call(["ip", "link", "set", "dev", "pan1", "up"])
                if ret != 0:
                    raise NetworkSetupError("Failed to bring up interface pan1")
                ret = call(["ip", "address", "add", "/".join((self.ip4_address, self.ip4_mask)), "dev", "pan1"])
                if ret != 0:
                    raise NetworkSetupError("Failed to add ip address %s with netmask %s" % (self.ip4_address,
                                                                                             self.ip4_mask))
            elif have('ifconfig'):
                ret = call(["ifconfig", "pan1", self.ip4_address, "netmask", self.ip4_mask, "up"])
                if ret != 0:
                    raise NetworkSetupError("Failed to add ip address %s with netmask %s" % (self.ip4_address,
                                                                                             self.ip4_mask))
            else:
                raise NetworkSetupError(
                    "Neither ifconfig or ip commands are found. Please install net-tools or iproute2")

            self.lock("netconfig")

        if self.ip4_changed or not self.locked("iptables"):
            self.del_ipt_rules()

            self.add_ipt_rule("nat", "POSTROUTING", "-s %s/%s -j MASQUERADE" % (self.ip4_address, self.ip4_mask))
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

    @staticmethod
    def lock(key):
        with open("/var/run/blueman-%s" % key, "w"):
            pass

    @staticmethod
    def unlock(key):
        try:
            os.unlink("/var/run/blueman-%s" % key)
        except OSError:
            pass

    @staticmethod
    def locked(key):
        return os.path.exists("/var/run/blueman-%s" % key)

    # save the instance of this class, requires root
    def store(self):
        if not os.path.exists("/var/lib/blueman"):
            os.mkdir("/var/lib/blueman")
        with open("/var/lib/blueman/network.state", "wb") as f:
            pickle.dump(self, f, 2)

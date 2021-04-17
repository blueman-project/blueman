import pickle
import errno
import re
import os
import ipaddress
from pickle import UnpicklingError
from tempfile import mkstemp
from time import sleep
import logging
import signal
from typing import List, Tuple, Optional, Type, TYPE_CHECKING

from blueman.Constants import DHCP_CONFIG_FILE
from blueman.Functions import have
from _blueman import create_bridge, destroy_bridge, BridgeException
from subprocess import call, Popen, PIPE

if TYPE_CHECKING:
    from typing_extensions import Protocol

    class DHCPHandler(Protocol):
        def __init__(self, netconf: "NetConf"):
            ...

        def do_apply(self) -> None:
            ...

        def do_remove(self) -> None:
            ...


class NetworkSetupError(Exception):
    pass


def is_running(name: str, pid: int) -> bool:
    if not os.path.exists(f"/proc/{pid}"):
        return False

    with open(f"/proc/{pid}/cmdline") as f:
        return name in f.readline().replace("\0", " ")


def kill(pid: Optional[int], name: str) -> bool:
    if pid and is_running(name, pid):
        print('Terminating ' + name)
        os.kill(pid, signal.SIGTERM)
        return True
    return False


def read_pid_file(fname: str) -> Optional[int]:
    try:
        with open(fname) as f:
            return int(f.read())
    except (OSError, ValueError):
        return None


def get_dns_servers() -> str:
    dns_servers = ''
    with open("/etc/resolv.conf") as f:
        for line in f:
            match = re.search(r"^nameserver ((?:[0-9]{1,3}\.){3}[0-9]{1,3}$)", line)
            if match:
                dns_servers += f"{match.group(1)}, "

        dns_servers = dns_servers.strip(", ")

    return dns_servers


def get_binary(*names: str) -> str:
    for name in names:
        path = have(name)
        if path:
            return path
    raise FileNotFoundError(f"{' '.join(names)} not found")


class DnsMasqHandler:
    def __init__(self, netconf: "NetConf") -> None:
        self.pid: Optional[int] = None
        self.netconf = netconf

    def do_apply(self) -> None:
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            assert self.netconf.ip4_address is not None

            ipiface = ipaddress.ip_interface('/'.join((self.netconf.ip4_address, '255.255.255.0')))
            cmd = [get_binary("dnsmasq"), "--port=0", "--pid-file=/var/run/dnsmasq.pan1.pid", "--except-interface=lo",
                   "--interface=pan1", "--bind-interfaces",
                   f"--dhcp-range={ipiface.network[2]},{ipiface.network[-2]},60m",
                   f"--dhcp-option=option:router,{self.netconf.ip4_address}"]

            logging.info(cmd)
            p = Popen(cmd, stderr=PIPE)

            error = p.communicate()[1]

            if not error:
                logging.info("Dnsmasq started correctly")
                with open("/var/run/dnsmasq.pan1.pid") as f:
                    self.pid = int(f.read())
                logging.info(f"pid {self.pid}")
                self.netconf.lock("dhcp")
            else:
                error_msg = error.decode("UTF-8").strip()
                logging.info(error_msg)
                raise NetworkSetupError(f"dnsmasq failed to start: {error_msg}")

    def do_remove(self) -> None:
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


class DhcpdHandler:
    def __init__(self, netconf: "NetConf") -> None:
        self.pid: Optional[int] = None
        self.netconf = netconf

    @staticmethod
    def _read_dhcp_config() -> Tuple[str, str]:
        dhcp_config = ''
        existing_subnet = ''
        start = end = False

        with open(DHCP_CONFIG_FILE) as f:
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

    def _generate_subnet_config(self) -> str:
        dns = get_dns_servers()

        assert self.netconf.ip4_address is not None and self.netconf.ip4_mask is not None

        ipiface = ipaddress.ip_interface('/'.join((self.netconf.ip4_address, self.netconf.ip4_mask)))

        return DHCPDSUBNET % {"ip_mask": ipiface.network.network_address,
                              "netmask": ipiface.netmask,
                              "dns": dns,
                              "rtr": ipiface.ip,
                              "start": ipiface.network[2],
                              "end": ipiface.network[-2]}

    def do_apply(self) -> None:
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            dhcp_config, existing_subnet = self._read_dhcp_config()

            subnet = self._generate_subnet_config()

            # if subnet != self.existing_subnet:
            with open(DHCP_CONFIG_FILE, "w") as f:
                f.write(dhcp_config)
                f.write(subnet)

            cmd = [get_binary("dhcpd3", "dhcpd"), "-pf", "/var/run/dhcpd.pan1.pid", "pan1"]
            p = Popen(cmd, stderr=PIPE)

            error = p.communicate()[1]

            if p.returncode == 0:
                logging.info("dhcpd started correctly")
                with open("/var/run/dhcpd.pan1.pid") as f:
                    self.pid = int(f.read())
                logging.info(f"pid {self.pid}")
                self.netconf.lock("dhcp")
            else:
                error_msg = error.decode("UTF-8").strip()
                logging.info(error_msg)
                raise NetworkSetupError(f"dhcpd failed to start: {error_msg}")

    def do_remove(self) -> None:
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


class UdhcpdHandler:
    def __init__(self, netconf: "NetConf") -> None:
        self.pid: Optional[int] = None
        self.netconf = netconf

    def _generate_config(self) -> str:
        dns = get_dns_servers()

        assert self.netconf.ip4_address is not None and self.netconf.ip4_mask is not None

        ipiface = ipaddress.ip_interface('/'.join((self.netconf.ip4_address, self.netconf.ip4_mask)))

        return UDHCP_CONF_TEMPLATE % {"ip_mask": ipiface.network.network_address,
                                      "dns": dns,
                                      "rtr": ipiface.ip,
                                      "start": ipiface.network[2],
                                      "end": ipiface.network[-2]}

    def do_apply(self) -> None:
        if not self.netconf.locked("dhcp") or self.netconf.ip4_changed:
            if self.netconf.ip4_changed:
                self.do_remove()

            config_file, config_path = mkstemp(prefix="udhcpd-")
            os.write(config_file, self._generate_config().encode('UTF-8'))
            os.close(config_file)

            logging.info(f"Running udhcpd with config file {config_path}")
            cmd = [get_binary("udhcpd"), "-S", config_path]
            p = Popen(cmd, stderr=PIPE)
            error = p.communicate()[1]

            # udhcpd takes time to create pid file
            sleep(0.1)

            pid = read_pid_file("/var/run/udhcpd.pan1.pid")

            if p.pid and pid is not None and is_running("udhcpd", pid):
                logging.info("udhcpd started correctly")
                self.pid = pid
                logging.info(f"pid {self.pid}")
                self.netconf.lock("dhcp")
            else:
                error_msg = error.decode("UTF-8").strip()
                logging.info(error_msg)
                raise NetworkSetupError(f"udhcpd failed to start: {error_msg}")

            os.remove(config_path)

    def do_remove(self) -> None:
        if self.netconf.locked("dhcp"):
            if not self.pid:
                pid = read_pid_file("/var/run/udhcpd.pan1.pid")
            else:
                pid = self.pid

            if not kill(pid, 'udhcpd'):
                logging.info("Stale dhcp lockfile found")
            self.netconf.unlock("dhcp")


class_id = 10


class NetConf:
    default_inst = None

    @classmethod
    def get_default(cls) -> "NetConf":
        if NetConf.default_inst:
            return NetConf.default_inst

        try:
            with open("/var/lib/blueman/network.state", "rb") as f:
                obj: "NetConf" = pickle.load(f)
                if obj.version != class_id:
                    raise Exception

                # Convert old 32bit packed ip's to strings
                if not isinstance(obj.ip4_address, str) and obj.ip4_address is not None:
                    obj.ip4_address = str(ipaddress.ip_address(obj.ip4_address))
                    obj.ip4_mask = '255.255.255.0'

                NetConf.default_inst = obj
                return obj
        except (OSError, UnicodeDecodeError, UnpicklingError):
            n = cls()
            try:
                n.store()
            # FIXME find out what could go wrong and drop bare exception
            except:  # noqa: E722
                return n
            NetConf.default_inst = n
            return n

    def __init__(self) -> None:
        self.ip4_mask: Optional[str] = None
        self.ip4_address: Optional[str] = None
        logging.info("init")
        self.version = class_id
        self.dhcp_handler: Optional[DHCPHandler] = None
        self.ipt_rules: List[Tuple[str, str, str]] = []

        self.ip4_changed = False

    def set_ipv4(self, ip: Optional[str], netmask: Optional[str]) -> None:
        if self.ip4_address != ip or self.ip4_mask != netmask:
            self.ip4_changed = True

        self.ip4_address = ip
        self.ip4_mask = netmask

    def get_ipv4(self) -> Tuple[Optional[str], Optional[str]]:
        return self.ip4_address, self.ip4_mask

    @staticmethod
    def enable_ip4_forwarding() -> None:
        with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
            f.write("1")

        for d in os.listdir("/proc/sys/net/ipv4/conf"):
            with open(f"/proc/sys/net/ipv4/conf/{d}/forwarding", "w") as f:
                f.write("1")

    def add_ipt_rule(self, table: str, chain: str, rule: str) -> None:
        self.ipt_rules.append((table, chain, rule))
        args = ["/sbin/iptables", "-t", table, "-A", chain] + rule.split(" ")
        logging.debug(" ".join(args))
        ret = call(args)
        logging.info(f"Return code {ret}")

    def del_ipt_rules(self) -> None:
        for table, chain, rule in self.ipt_rules:
            call(["/sbin/iptables", "-t", table, "-D", chain] + rule.split(" "))
        self.ipt_rules = []
        self.unlock("iptables")

    def set_dhcp_handler(self, handler: Type["DHCPHandler"]) -> None:
        if not isinstance(self.dhcp_handler, handler):
            running = False
            if self.dhcp_handler:
                self.dhcp_handler.do_remove()
                running = True

            self.dhcp_handler = handler(self)
            if running:
                self.dhcp_handler.do_apply()

    def get_dhcp_handler(self) -> Optional[Type["DHCPHandler"]]:
        if not self.dhcp_handler:
            return None

        return type(self.dhcp_handler)

    def apply_settings(self) -> None:
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

                assert self.ip4_address is not None and self.ip4_mask is not None

                ret = call(["ip", "address", "add", "/".join((self.ip4_address, self.ip4_mask)), "dev", "pan1"])
                if ret != 0:
                    raise NetworkSetupError(f"Failed to add ip address {self.ip4_address}"
                                            f"with netmask {self.ip4_mask}")
            elif have('ifconfig'):
                assert self.ip4_address is not None and self.ip4_mask is not None

                ret = call(["ifconfig", "pan1", self.ip4_address, "netmask", self.ip4_mask, "up"])
                if ret != 0:
                    raise NetworkSetupError(f"Failed to add ip address {self.ip4_address}"
                                            f"with netmask {self.ip4_mask}")
            else:
                raise NetworkSetupError(
                    "Neither ifconfig or ip commands are found. Please install net-tools or iproute2")

            self.lock("netconfig")

        if self.ip4_changed or not self.locked("iptables"):
            self.del_ipt_rules()

            self.add_ipt_rule("nat", "POSTROUTING", f"-s {self.ip4_address}/{self.ip4_mask} -j MASQUERADE")
            self.add_ipt_rule("filter", "FORWARD", "-i pan1 -j ACCEPT")
            self.add_ipt_rule("filter", "FORWARD", "-o pan1 -j ACCEPT")
            self.add_ipt_rule("filter", "FORWARD", "-i pan1 -j ACCEPT")
            self.lock("iptables")

        if self.dhcp_handler:
            self.dhcp_handler.do_apply()
        self.ip4_changed = False

        self.store()

    def remove_settings(self) -> None:
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
    def lock(key: str) -> None:
        with open(f"/var/run/blueman-{key}", "w"):
            pass

    @staticmethod
    def unlock(key: str) -> None:
        try:
            os.unlink(f"/var/run/blueman-{key}")
        except OSError:
            pass

    @staticmethod
    def locked(key: str) -> bool:
        return os.path.exists(f"/var/run/blueman-{key}")

    # save the instance of this class, requires root
    def store(self) -> None:
        if not os.path.exists("/var/lib/blueman"):
            os.mkdir("/var/lib/blueman")
        with open("/var/lib/blueman/network.state", "wb") as f:
            pickle.dump(self, f, 2)

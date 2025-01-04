import errno
import os
import pathlib
import ipaddress
import socket
from tempfile import mkstemp
from time import sleep
import logging
import signal

from blueman.Constants import DHCP_CONFIG_FILE
from blueman.Functions import have
from _blueman import create_bridge, destroy_bridge, BridgeException
from subprocess import call, Popen, PIPE

from blueman.main.DNSServerProvider import DNSServerProvider


class NetworkSetupError(Exception):
    pass


def _is_running(name: str, pid: int) -> bool:
    path = pathlib.Path(f"/proc/{pid}")
    if not path.exists():
        return False

    return name in path.joinpath("cmdline").read_text()


def _read_pid_file(fname: pathlib.Path) -> int | None:
    try:
        return int(fname.read_text())
    except (OSError, ValueError):
        return None


def _get_binary(*names: str) -> str:
    for name in names:
        path = have(name)
        if path is not None:
            return path.as_posix()
    raise FileNotFoundError(f"{' '.join(names)} not found")


class DHCPHandler:
    _BINARIES: list[str]

    @property
    def _key(self) -> str:
        return self._BINARIES[-1]

    def __init__(self) -> None:
        self._pid: int | None = None

    @staticmethod
    def _get_arguments(ip4_address: str) -> list[str]:
        return []

    @property
    def _pid_path(self) -> pathlib.Path:
        return pathlib.Path(f"/var/run/{self._key}.pan1.pid")

    def apply(self, ip4_address: str, ip4_mask: str) -> None:
        error = self._start(_get_binary(*self._BINARIES), ip4_address, ip4_mask,
                            [ip4_address if addr.is_loopback else str(addr)
                             for addr in DNSServerProvider.get_servers()])
        if error is None:
            logging.info(f"{self._key} started correctly")
            self._pid = _read_pid_file(self._pid_path)
            logging.info(f"pid {self._pid}")
            NetConf.lock("dhcp")
        else:
            error_msg = error.decode("UTF-8").strip()
            logging.info(error_msg)
            raise NetworkSetupError(f"{self._key} failed to start: {error_msg}")

    def _start(self, binary: str, ip4_address: str, ip4_mask: str, dns_servers: list[str]) -> bytes | None:
        ...

    def clean_up(self) -> None:
        self._clean_up_configuration()

        if NetConf.locked("dhcp"):
            if not self._pid:
                pid = _read_pid_file(self._pid_path)
            else:
                pid = self._pid

            if pid is not None:
                running_binary: str | None = next(binary for binary in self._BINARIES if _is_running(binary, pid))
                if running_binary is not None:
                    print('Terminating ' + running_binary)
                    os.kill(pid, signal.SIGTERM)
            else:
                running_binary = None

            if pid is None or running_binary is None:
                logging.info("Stale dhcp lockfile found")

            NetConf.unlock("dhcp")

    def _clean_up_configuration(self) -> None:
        ...


class DnsMasqHandler(DHCPHandler):
    _BINARIES = ["dnsmasq"]

    def _start(self, binary: str, ip4_address: str, ip4_mask: str, dns_servers: list[str]) -> bytes | None:
        ipiface = ipaddress.ip_interface('/'.join((ip4_address, ip4_mask)))
        cmd = [binary, f"--pid-file={self._pid_path}", "--except-interface=lo",
               "--interface=pan1", "--bind-interfaces",
               f"--dhcp-range={ipiface.network[2]},{ipiface.network[-2]},60m",
               f"--dhcp-option=option:router,{ip4_address}"]

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", 53)) == 0:
                cmd += ["--port=0", f"--dhcp-option=option:dns-server,{', '.join(dns_servers)}"]

        logging.info(cmd)
        p = Popen(cmd, stderr=PIPE)

        error = p.communicate()[1]

        return error if error else None


DHCPDSUBNET = '''#### BLUEMAN AUTOMAGIC SUBNET ####
# Everything inside this section is destroyed after config change
subnet %(ip_mask)s netmask %(netmask)s {
  option domain-name-servers %(dns)s;
  option subnet-mask %(netmask)s;
  option routers %(rtr)s;
  range %(start)s %(end)s;
}
#### END BLUEMAN AUTOMAGIC SUBNET ####'''


class DhcpdHandler(DHCPHandler):
    _BINARIES = ["dhcpd3", "dhcpd"]

    @staticmethod
    def _read_dhcp_config() -> tuple[str, str]:
        dhcp_config = ''
        existing_subnet = ''
        start = end = False

        with DHCP_CONFIG_FILE.open() as f:
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

    @staticmethod
    def _generate_subnet_config(ip4_address: str, ip4_mask: str, dns_servers: list[str]) -> str:
        ipiface = ipaddress.ip_interface('/'.join((ip4_address, ip4_mask)))

        return DHCPDSUBNET % {"ip_mask": ipiface.network.network_address,
                              "netmask": ipiface.netmask,
                              "dns": ', '.join(dns_servers),
                              "rtr": ipiface.ip,
                              "start": ipiface.network[2],
                              "end": ipiface.network[-2]}

    def _start(self, binary: str, ip4_address: str, ip4_mask: str, dns_servers: list[str]) -> bytes | None:
        dhcp_config, existing_subnet = self._read_dhcp_config()

        subnet = self._generate_subnet_config(ip4_address, ip4_mask, dns_servers)

        with DHCP_CONFIG_FILE.open("w") as f:
            f.write(dhcp_config)
            f.write(subnet)

        cmd = [binary, "-pf", self._pid_path.as_posix(), "pan1"]
        p = Popen(cmd, stderr=PIPE)

        error = p.communicate()[1]

        return None if p.returncode == 0 else error

    def _clean_up_configuration(self) -> None:
        dhcp_config, existing_subnet = self._read_dhcp_config()
        with DHCP_CONFIG_FILE.open("w") as f:
            f.write(dhcp_config)


UDHCP_CONF_TEMPLATE = """start %(start)s
end %(end)s
interface pan1
pidfile %(pid_path)s
option subnet %(ip_mask)s
option dns %(dns)s
option router %(rtr)s
"""


class UdhcpdHandler(DHCPHandler):
    _BINARIES = ["udhcpd"]
    _config_file: pathlib.Path | None = None

    def _generate_config(self, ip4_address: str, ip4_mask: str, dns_servers: list[str]) -> str:
        ipiface = ipaddress.ip_interface('/'.join((ip4_address, ip4_mask)))

        return UDHCP_CONF_TEMPLATE % {"ip_mask": ipiface.network.network_address,
                                      "dns": ', '.join(dns_servers),
                                      "rtr": ipiface.ip,
                                      "start": ipiface.network[2],
                                      "end": ipiface.network[-2],
                                      "pid_path": self._pid_path}

    def _start(self, binary: str, ip4_address: str, ip4_mask: str, dns_servers: list[str]) -> bytes | None:
        _handle, config_path = mkstemp(prefix="udhcpd-")
        self._config_file = pathlib.Path(config_path)

        with self._config_file.open("w", encoding="utf8") as f:
            f.write(self._generate_config(ip4_address, ip4_mask, dns_servers))

        logging.info(f"Running udhcpd with config file {self._config_file}")
        cmd = [binary, "-S", self._config_file.as_posix()]
        p = Popen(cmd, stderr=PIPE)
        error = p.communicate()[1]

        # udhcpd takes time to create pid file
        sleep(0.1)

        pid = _read_pid_file(self._pid_path)

        return None if p.pid and pid is not None and _is_running("udhcpd", pid) else error

    def _clean_up_configuration(self) -> None:
        if self._config_file is None:
            return
        self._config_file.unlink(missing_ok=True)


class NetConf:
    _dhcp_handler: DHCPHandler | None = None
    _ipt_rules: list[tuple[str, str, str]] = []

    _IPV4_SYS_PATH = pathlib.Path("/proc/sys/net/ipv4")
    _RUN_PATH = pathlib.Path("/var/run")

    @classmethod
    def _enable_ip4_forwarding(cls) -> None:
        cls._IPV4_SYS_PATH.joinpath("ip_forward").write_text("1")

        for p in cls._IPV4_SYS_PATH.joinpath("conf").glob("**/forwarding"):
            p.write_text("1")

    @classmethod
    def _add_ipt_rule(cls, table: str, chain: str, rule: str) -> None:
        cls._ipt_rules.append((table, chain, rule))
        args = ["/sbin/iptables", "-t", table, "-A", chain] + rule.split(" ")
        logging.debug(" ".join(args))
        ret = call(args)
        logging.info(f"Return code {ret}")

    @classmethod
    def _del_ipt_rules(cls) -> None:
        for table, chain, rule in cls._ipt_rules:
            call(["/sbin/iptables", "-t", table, "-D", chain] + rule.split(" "))
        cls._ipt_rules = []
        cls.unlock("iptables")

    @classmethod
    def apply_settings(cls, ip4_address: str, ip4_mask: str, handler: type["DHCPHandler"],
                       address_changed: bool) -> None:
        if not isinstance(cls._dhcp_handler, handler):
            if cls._dhcp_handler is not None:
                cls._dhcp_handler.clean_up()

            cls._dhcp_handler = handler()

        try:
            create_bridge("pan1")
        except BridgeException as e:
            if e.errno != errno.EEXIST:
                raise

        if address_changed or not cls.locked("netconfig"):
            cls._enable_ip4_forwarding()

            if have("ip"):
                ret = call(["ip", "link", "set", "dev", "pan1", "up"])
                if ret != 0:
                    raise NetworkSetupError("Failed to bring up interface pan1")

                ret = call(["ip", "address", "add", "/".join((ip4_address, ip4_mask)), "dev", "pan1"])
                if ret != 0:
                    raise NetworkSetupError(f"Failed to add ip address {ip4_address}"
                                            f"with netmask {ip4_mask}")
            elif have('ifconfig'):
                ret = call(["ifconfig", "pan1", ip4_address, "netmask", ip4_mask, "up"])
                if ret != 0:
                    raise NetworkSetupError(f"Failed to add ip address {ip4_address}"
                                            f"with netmask {ip4_mask}")
            else:
                raise NetworkSetupError(
                    "Neither ifconfig or ip commands are found. Please install net-tools or iproute2")

            cls.lock("netconfig")

        if address_changed or not cls.locked("iptables"):
            cls._del_ipt_rules()

            cls._add_ipt_rule("nat", "POSTROUTING", f"-s {ip4_address}/{ip4_mask} -j MASQUERADE")
            cls._add_ipt_rule("filter", "FORWARD", "-i pan1 -j ACCEPT")
            cls._add_ipt_rule("filter", "FORWARD", "-o pan1 -j ACCEPT")
            cls._add_ipt_rule("filter", "FORWARD", "-i pan1 -j ACCEPT")
            cls.lock("iptables")

        if address_changed or not NetConf.locked("dhcp"):
            cls._dhcp_handler.clean_up()
            cls._dhcp_handler.apply(ip4_address, ip4_mask)

    @classmethod
    def clean_up(cls) -> None:
        logging.info(cls)

        if cls._dhcp_handler:
            cls._dhcp_handler.clean_up()

        try:
            destroy_bridge("pan1")
        except BridgeException:
            pass
        cls.unlock("netconfig")

        cls._del_ipt_rules()

    @classmethod
    def lock(cls, key: str) -> None:
        cls._RUN_PATH.joinpath(f"blueman-{key}").touch()

    @classmethod
    def unlock(cls, key: str) -> None:
        cls._RUN_PATH.joinpath(f"blueman-{key}").unlink(missing_ok=True)

    @classmethod
    def locked(cls, key: str) -> bool:
        return cls._RUN_PATH.joinpath(f"blueman-{key}").exists()

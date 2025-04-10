import os.path
import shutil
import subprocess
from ipaddress import IPv4Address
from pathlib import Path
from subprocess import Popen
from typing import Optional, List
from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock

from blueman.main.NetConf import DnsMasqHandler, NetworkSetupError, DhcpdHandler, UdhcpdHandler, NetConf, DHCPHandler


class FakeSocket:
    def __init__(self, connect_return_value: int) -> None:
        self._ret = connect_return_value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def connect_ex(self, *_args: object) -> int:
        return self._ret


@patch("blueman.main.NetConf.have", return_value=Path("/usr/bin/mydnsmasq"))
@patch("blueman.main.NetConf.DnsMasqHandler._pid_path", PropertyMock(return_value=Path("/tmp/pid")))
class TestDnsmasqHandler(TestCase):
    @patch("blueman.main.NetConf.Popen", return_value=Popen("true"))
    @patch("blueman.main.NetConf.NetConf.lock")
    @patch("blueman.main.NetConf.socket.socket", lambda *args: FakeSocket(1))
    @patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [])
    def test_success_with_dns(self, lock_mock: Mock, popen_mock: Mock, have_mock: Mock) -> None:
        with open("/tmp/pid", "w") as f:
            f.write("123")
        DnsMasqHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        lock_mock.assert_called_with("dhcp")

    @patch("blueman.main.NetConf.Popen", return_value=Popen("true"))
    @patch("blueman.main.NetConf.NetConf.lock")
    @patch("blueman.main.NetConf.socket.socket", lambda *args: FakeSocket(0))
    @patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [IPv4Address("203.0.113.10")])
    def test_success_without_dns(self, lock_mock: Mock, popen_mock: Mock, have_mock: Mock) -> None:
        with open("/tmp/pid", "w") as f:
            f.write("123")
        DnsMasqHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock, ["--port=0", "--dhcp-option=option:dns-server,203.0.113.10"])
        lock_mock.assert_called_with("dhcp")

    @patch("blueman.main.NetConf.Popen", return_value=Popen(["sh", "-c", "echo errormsg >&2"], stderr=subprocess.PIPE))
    @patch("blueman.main.NetConf.socket.socket", lambda *args: FakeSocket(1))
    @patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [])
    def test_failure(self, popen_mock: Mock, have_mock: Mock) -> None:
        with self.assertRaises(NetworkSetupError) as cm:
            DnsMasqHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        self.assertEqual(cm.exception.args, ("dnsmasq failed to start: errormsg",))

    def _check_invocation(self, have_mock: Mock, popen_mock: Mock, additional_args: Optional[List[str]] = None) -> None:
        have_mock.assert_called_with("dnsmasq")
        popen_mock.assert_called_with(
            ["/usr/bin/mydnsmasq", "--pid-file=/tmp/pid", "--except-interface=lo",
             "--interface=pan1", "--bind-interfaces", "--dhcp-range=203.0.113.2,203.0.113.254,60m",
             "--dhcp-option=option:router,203.0.113.1"] + ([] if additional_args is None else additional_args),
            stderr=subprocess.PIPE
        )


@patch("blueman.main.NetConf.have", return_value=Path("/usr/bin/mydhcpd"))
@patch("blueman.main.NetConf.DhcpdHandler._pid_path", PropertyMock(return_value=Path("/tmp/pid")))
@patch("blueman.main.NetConf.DHCP_CONFIG_FILE", Path("/tmp/dhcpd.conf"))
@patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [])
class TestDhcpdHandler(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open("/tmp/dhcpd.conf", "w"):
            pass

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove("/tmp/dhcpd.conf")

    @patch("blueman.main.NetConf.Popen", return_value=Popen(["sh", "-c", "echo warning >&2"], stderr=subprocess.PIPE))
    @patch("blueman.main.NetConf.NetConf.lock")
    def test_success(self, lock_mock: Mock, popen_mock: Mock, have_mock: Mock) -> None:
        with open("/tmp/pid", "w") as f:
            f.write("123")
        DhcpdHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        lock_mock.assert_called_with("dhcp")

    @patch("blueman.main.NetConf.Popen",
           return_value=Popen(["sh", "-c", "echo errormsg >&2; exit 1"], stderr=subprocess.PIPE))
    def test_failure(self, popen_mock: Mock, have_mock: Mock) -> None:
        with self.assertRaises(NetworkSetupError) as cm:
            DhcpdHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        self.assertEqual(cm.exception.args, ("dhcpd failed to start: errormsg",))

    def _check_invocation(self, have_mock: Mock, popen_mock: Mock) -> None:
        have_mock.assert_called_with("dhcpd3")
        popen_mock.assert_called_with(
            ["/usr/bin/mydhcpd", "-pf", "/tmp/pid", "pan1"],
            stderr=subprocess.PIPE
        )


@patch("blueman.main.NetConf.have", return_value=Path("/usr/bin/myudhcpd"))
@patch("blueman.main.NetConf.UdhcpdHandler._pid_path", PropertyMock(return_value=Path("/tmp/pid")))
@patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [])
class TestUdhcpdHandler(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open("/tmp/dhcpd.conf", "w"):
            pass

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove("/tmp/dhcpd.conf")

    @patch("blueman.main.NetConf.Popen", return_value=Popen(["sh", "-c", "echo warning >&2"], stderr=subprocess.PIPE))
    @patch("blueman.main.NetConf.NetConf.lock")
    @patch("blueman.main.NetConf._is_running", lambda _name, _pid: True)
    def test_success(self, lock_mock: Mock, popen_mock: Mock, have_mock: Mock) -> None:
        with open("/tmp/pid", "w") as f:
            f.write("123")
        UdhcpdHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        lock_mock.assert_called_with("dhcp")

    @patch("blueman.main.NetConf.Popen", return_value=Popen(["sh", "-c", "echo errormsg >&2"], stderr=subprocess.PIPE))
    @patch("blueman.main.NetConf._is_running", lambda _name, _pid: False)
    def test_failure(self, popen_mock: Mock, have_mock: Mock) -> None:
        with open("/tmp/pid", "w") as f:
            f.write("123")
        with self.assertRaises(NetworkSetupError) as cm:
            UdhcpdHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        self.assertEqual(cm.exception.args, ("udhcpd failed to start: errormsg",))

    def _check_invocation(self, have_mock: Mock, popen_mock: Mock) -> None:
        have_mock.assert_called_with("udhcpd")
        args = popen_mock.call_args
        self.assertEqual(len(args[0]), 1)
        self.assertEqual(args[0][0][:-1], ["/usr/bin/myudhcpd", "-S"])
        self.assertEqual(args[1], {"stderr": subprocess.PIPE})


@patch("blueman.main.NetConf.NetConf._IPV4_SYS_PATH", Path("/tmp/blueman-test/ipv4"))
@patch("blueman.main.NetConf.NetConf._RUN_PATH", Path("/tmp/blueman-test/run"))
@patch("blueman.main.NetConf.create_bridge")
@patch("blueman.main.NetConf.call", return_value=0)
class TestNetConf(TestCase):
    def setUp(self) -> None:
        tmpdir = Path("/tmp/blueman-test")
        tmpdir.joinpath("run").mkdir(parents=True)
        tmpdir.joinpath("ipv4").mkdir()
        tmpdir.joinpath("ipv4", "ip_forward").write_text("0")

        i0fw = tmpdir.joinpath("ipv4", "conf", "i0", "forwarding")
        i0fw.parent.mkdir(parents=True)
        i0fw.write_text("0")
        i1fw = tmpdir.joinpath("ipv4", "conf", "i1", "forwarding")
        i1fw.parent.mkdir(parents=True)
        i1fw.write_text("0")

    def tearDown(self) -> None:
        shutil.rmtree("/tmp/blueman-test")

    class TestDHCPHandler(DHCPHandler):
        @property
        def _key(self) -> str:
            return "test-dhcp-handler"

        apply = Mock()

    class TestDHCPHandler2(TestDHCPHandler):
        clean_up = Mock()

    def test_initial_apply(self, call_mock: Mock, bridge_mock: Mock) -> None:
        NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler, False)

        bridge_mock.assert_called_once_with("pan1")
        self._check_forwarding()
        self._check_iptables(call_mock)
        self.TestDHCPHandler.apply.assert_called_with("203.0.113.1", "255.255.255.0")

        call_mock.assert_any_call(["ip", "link", "set", "dev", "pan1", "up"])
        call_mock.assert_any_call(["ip", "address", "add", "203.0.113.1/255.255.255.0", "dev", "pan1"])
        self.assertTrue(NetConf.locked("netconfig"))

    def test_address_change(self, call_mock: Mock, bridge_mock: Mock) -> None:
        NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler, True)

        bridge_mock.assert_called_once_with("pan1")
        self._check_forwarding()
        self._check_iptables(call_mock)
        self.TestDHCPHandler.apply.assert_called_with("203.0.113.1", "255.255.255.0")

        call_mock.assert_any_call(["ip", "link", "set", "dev", "pan1", "up"])
        call_mock.assert_any_call(["ip", "address", "add", "203.0.113.1/255.255.255.0", "dev", "pan1"])
        self.assertTrue(NetConf.locked("netconfig"))

    @patch("blueman.main.NetConf.have", lambda key: key != "ip")
    def test_nettools(self, call_mock: Mock, bridge_mock: Mock) -> None:
        NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler, False)

        bridge_mock.assert_called_once_with("pan1")
        self._check_forwarding()

        call_mock.assert_any_call(["ifconfig", "pan1", "203.0.113.1", "netmask", "255.255.255.0", "up"])
        self.assertTrue(NetConf.locked("netconfig"))

    def _check_forwarding(self) -> None:
        for file in [
            "/tmp/blueman-test/ipv4/ip_forward",
            "/tmp/blueman-test/ipv4/conf/i0/forwarding",
            "/tmp/blueman-test/ipv4/conf/i1/forwarding",
        ]:
            with open(file, "r") as f:
                self.assertEqual(f.read(), "1")

    def _check_iptables(self, call_mock: Mock, remove: bool = False) -> None:
        command = "-D" if remove else "-A"
        call_mock.assert_any_call(["/sbin/iptables", "-t", "nat", command, "POSTROUTING",
                                   "-s", "203.0.113.1/255.255.255.0", "-j", "MASQUERADE"])
        call_mock.assert_any_call(["/sbin/iptables", "-t", "filter", command, "FORWARD", "-i", "pan1", "-j", "ACCEPT"])
        call_mock.assert_any_call(["/sbin/iptables", "-t", "filter", command, "FORWARD", "-o", "pan1", "-j", "ACCEPT"])
        self.assertEqual(NetConf.locked("iptables"), not remove)

    def test_dhcp_handler_replacement(self, _call_mock: Mock, _bridge_mock: Mock) -> None:
        NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler2, False)
        self.TestDHCPHandler2.clean_up.reset_mock()
        NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler, False)
        self.TestDHCPHandler2.clean_up.assert_called_once_with()
        self.TestDHCPHandler.apply.assert_called_with("203.0.113.1", "255.255.255.0")

    @patch("blueman.main.NetConf.destroy_bridge")
    def test_cleanup(self, destroy_bridge_mock: Mock, call_mock: Mock, _create_bridge_mock: Mock) -> None:
        NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler2, False)
        self.TestDHCPHandler2.clean_up.reset_mock()

        NetConf.clean_up()

        destroy_bridge_mock.assert_called_once_with("pan1")
        self.TestDHCPHandler2.clean_up.assert_called_once_with()
        self._check_iptables(call_mock, remove=True)

        self.assertFalse(NetConf.locked("netconfig"))
        self.assertFalse(NetConf.locked("iptables"))

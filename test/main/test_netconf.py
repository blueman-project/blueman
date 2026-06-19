import errno
import fcntl
import os.path
import shutil
import signal
import subprocess
from ipaddress import IPv4Address
from pathlib import Path
from subprocess import Popen
from typing import Optional, List
from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock

from blueman.main.NetConf import (
    DnsMasqHandler, NetworkSetupError, DhcpdHandler, UdhcpdHandler, NetConf, DHCPHandler, _is_running,
    _poll_pid_file, _communicate_stderr,
)
from _blueman import BridgeException


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

    @patch("blueman.main.NetConf.Popen", return_value=Popen("true"))
    @patch("blueman.main.NetConf.NetConf.lock")
    @patch("blueman.main.NetConf.socket.socket", lambda *args: FakeSocket(0))
    @patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [])
    def test_local_resolver_no_dns_servers(self, lock_mock: Mock, popen_mock: Mock, have_mock: Mock) -> None:
        # Local resolver present (port 53 reachable) but no DNS servers:
        # disable dnsmasq DNS with --port=0 but emit no dns-server option,
        # which with an empty list would be a dnsmasq-rejected trailing comma.
        with open("/tmp/pid", "w") as f:
            f.write("123")
        DnsMasqHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock, ["--port=0"])
        lock_mock.assert_called_with("dhcp")

    @patch("blueman.main.NetConf.Popen", return_value=Popen(["sh", "-c", "echo errormsg >&2"], stderr=subprocess.PIPE))
    @patch("blueman.main.NetConf.socket.socket", lambda *args: FakeSocket(1))
    @patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [])
    def test_failure(self, popen_mock: Mock, have_mock: Mock) -> None:
        with self.assertRaises(NetworkSetupError) as cm:
            DnsMasqHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        self.assertEqual(cm.exception.args, ("dnsmasq failed to start: errormsg",))

    @patch("blueman.main.NetConf.Popen", return_value=Popen("true"))
    @patch("blueman.main.NetConf.NetConf.lock")
    @patch("blueman.main.NetConf.sleep")
    @patch("blueman.main.NetConf._PID_POLL_ATTEMPTS", 3)
    @patch("blueman.main.NetConf.socket.socket", lambda *args: FakeSocket(1))
    @patch("blueman.main.NetConf.DNSServerProvider.get_servers", lambda: [])
    def test_no_pid_file_tears_down(self, sleep_mock: Mock, lock_mock: Mock,
                                    popen_mock: Mock, have_mock: Mock) -> None:
        # Start succeeds but no pid file appears: must not lock dhcp; instead
        # tear down and raise.
        try:
            os.remove("/tmp/pid")
        except FileNotFoundError:
            pass
        with self.assertRaises(NetworkSetupError) as cm:
            DnsMasqHandler().apply("203.0.113.1", "255.255.255.0")
        self.assertIn("wrote no pid file", cm.exception.args[0])
        lock_mock.assert_not_called()

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
    @patch("blueman.main.NetConf.sleep")
    @patch("blueman.main.NetConf._is_running", lambda _name, _pid: True)
    def test_success(self, sleep_mock: Mock, lock_mock: Mock, popen_mock: Mock, have_mock: Mock) -> None:
        with open("/tmp/pid", "w") as f:
            f.write("123")
        UdhcpdHandler().apply("203.0.113.1", "255.255.255.0")
        self._check_invocation(have_mock, popen_mock)
        lock_mock.assert_called_with("dhcp")
        # pid file already present: poll returns at once with no blocking sleep.
        sleep_mock.assert_not_called()

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


@patch("blueman.main.NetConf.NetConf._iptables", new=classmethod(lambda cls: "/sbin/iptables"))
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

        # Fake `iptables -S <chain>` by reflecting the rules blueman has
        # installed (tracked in _ipt_rules) as the live kernel ruleset, so the
        # flush-by-comment path can find and delete them.
        def fake_run(args: list, **_kwargs: object) -> Mock:
            table, chain = args[2], args[4]
            lines = [f"-A {chain} " + " ".join(spec)
                     for t, c, spec in NetConf._ipt_rules if t == table and c == chain]
            return Mock(stdout="\n".join(lines) + ("\n" if lines else ""))

        self.run_patch = patch("blueman.main.NetConf.run", side_effect=fake_run)
        self.run_patch.start()
        self.addCleanup(self.run_patch.stop)

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
        cmt = ["-m", "comment", "--comment", "blueman-pan1"]
        call_mock.assert_any_call(["/sbin/iptables", "-t", "nat", command, "POSTROUTING",
                                   "-s", "203.0.113.1/255.255.255.0", "-j", "MASQUERADE", *cmt])
        call_mock.assert_any_call(
            ["/sbin/iptables", "-t", "filter", command, "FORWARD", "-i", "pan1", "-j", "ACCEPT", *cmt])
        call_mock.assert_any_call(
            ["/sbin/iptables", "-t", "filter", command, "FORWARD", "-o", "pan1", "-j", "ACCEPT", *cmt])
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

    def test_missing_sysctl_path_raises(self, call_mock: Mock, _bridge_mock: Mock) -> None:
        with patch.object(NetConf, "_IPV4_SYS_PATH", Path("/tmp/blueman-test/does-not-exist")):
            with self.assertRaises(NetworkSetupError) as cm:
                NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler, False)
        self.assertIn("IPv4 forwarding control not available", cm.exception.args[0])

    @patch("blueman.main.NetConf.destroy_bridge", side_effect=BridgeException(errno.ENODEV))
    def test_cleanup_logs_bridge_failure(self, destroy_bridge_mock: Mock, call_mock: Mock,
                                         _create_bridge_mock: Mock) -> None:
        NetConf.apply_settings("203.0.113.1", "255.255.255.0", self.TestDHCPHandler2, False)
        with self.assertLogs(level="WARNING") as logs:
            NetConf.clean_up()
        self.assertTrue(any("Failed to destroy bridge pan1" in m for m in logs.output))
        # The lock must still be released despite the bridge failure.
        self.assertFalse(NetConf.locked("netconfig"))


class TestIsRunning(TestCase):
    def setUp(self) -> None:
        self.proc = Path("/tmp/blueman-proc")
        self.proc.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(self.proc))

    def _write_proc(self, pid: int, cmdline: str) -> None:
        d = self.proc / str(pid)
        d.mkdir()
        d.joinpath("cmdline").write_text(cmdline)

    def test_procfs_match(self) -> None:
        self._write_proc(123, "/usr/sbin/dnsmasq\0--foo")
        with patch("blueman.main.NetConf._PROC_PATH", self.proc):
            self.assertTrue(_is_running("dnsmasq", 123))

    def test_procfs_name_mismatch(self) -> None:
        self._write_proc(123, "/usr/sbin/other\0")
        with patch("blueman.main.NetConf._PROC_PATH", self.proc):
            self.assertFalse(_is_running("dnsmasq", 123))

    def test_procfs_pid_absent(self) -> None:
        with patch("blueman.main.NetConf._PROC_PATH", self.proc):
            self.assertFalse(_is_running("dnsmasq", 999))

    def test_no_procfs_falls_back_to_liveness(self) -> None:
        missing = Path("/tmp/blueman-no-proc")
        with patch("blueman.main.NetConf._PROC_PATH", missing):
            with patch("blueman.main.NetConf.os.kill") as kill_mock:
                self.assertTrue(_is_running("dnsmasq", 123))
                kill_mock.assert_called_once_with(123, 0)
            with patch("blueman.main.NetConf.os.kill", side_effect=OSError):
                self.assertFalse(_is_running("dnsmasq", 123))


class _CleanupHandler(DHCPHandler):
    _BINARIES = ["dnsmasq"]


@patch("blueman.main.NetConf.NetConf._RUN_PATH", Path("/tmp/blueman-cleanup"))
class TestDHCPHandlerCleanup(TestCase):
    def setUp(self) -> None:
        Path("/tmp/blueman-cleanup").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree("/tmp/blueman-cleanup")

    @patch("blueman.main.NetConf.os.kill")
    @patch("blueman.main.NetConf._is_running", lambda _name, _pid: True)
    def test_terminate_logs_binary_and_pid(self, kill_mock: Mock) -> None:
        handler = _CleanupHandler()
        handler._pid = 4321
        NetConf.lock("dhcp")
        with self.assertLogs(level="INFO") as logs:
            handler.clean_up()
        kill_mock.assert_called_once_with(4321, signal.SIGTERM)
        self.assertTrue(any("Terminating dnsmasq (pid 4321)" in m for m in logs.output))
        self.assertFalse(NetConf.locked("dhcp"))

    @patch("blueman.main.NetConf.os.kill")
    @patch("blueman.main.NetConf._is_running", lambda _name, _pid: True)
    def test_clean_up_clears_pid_and_is_idempotent(self, kill_mock: Mock) -> None:
        handler = _CleanupHandler()
        handler._pid = 4321
        NetConf.lock("dhcp")
        handler.clean_up()
        self.assertIsNone(handler._pid)
        # Second call: lock already gone, must not signal anything again.
        handler.clean_up()
        kill_mock.assert_called_once_with(4321, signal.SIGTERM)

    @patch("blueman.main.NetConf.os.kill", side_effect=ProcessLookupError)
    @patch("blueman.main.NetConf._is_running", lambda _name, _pid: True)
    def test_clean_up_survives_already_dead_pid(self, kill_mock: Mock) -> None:
        handler = _CleanupHandler()
        handler._pid = 4321
        NetConf.lock("dhcp")
        # Must not propagate ProcessLookupError, and must still unlock.
        handler.clean_up()
        self.assertFalse(NetConf.locked("dhcp"))

    @patch("blueman.main.NetConf.os.kill")
    @patch("blueman.main.NetConf._is_running", lambda _name, _pid: False)
    def test_clean_up_stale_lock_no_kill(self, kill_mock: Mock) -> None:
        handler = _CleanupHandler()
        handler._pid = 4321
        NetConf.lock("dhcp")
        with self.assertLogs(level="INFO") as logs:
            handler.clean_up()
        kill_mock.assert_not_called()
        self.assertTrue(any("Stale dhcp lockfile" in m for m in logs.output))
        self.assertFalse(NetConf.locked("dhcp"))

    @patch("blueman.main.NetConf.os.kill")
    def test_clean_up_not_locked_is_noop(self, kill_mock: Mock) -> None:
        handler = _CleanupHandler()
        handler._pid = 4321
        # dhcp not locked -> nothing happens.
        handler.clean_up()
        kill_mock.assert_not_called()


class TestValidateIpv4(TestCase):
    def test_valid_addresses_pass(self) -> None:
        for addr, mask in [
            ("203.0.113.1", "255.255.255.0"),
            ("10.0.0.1", "255.0.0.0"),
            ("192.168.1.254", "255.255.255.252"),
            ("0.0.0.0", "0.0.0.0"),
            ("255.255.255.255", "255.255.255.255"),
        ]:
            with self.subTest(addr=addr, mask=mask):
                # Must not raise.
                NetConf._validate_ipv4(addr, mask)

    def test_invalid_address_raises(self) -> None:
        for bad in [
            "203.0.113.1 -j ACCEPT",      # argument injection via space
            "203.0.113.1/24",             # CIDR, not a bare address
            "203.0.113.256",              # octet out of range
            "203.0.113",                  # too few octets
            "::1",                        # IPv6
            "hostname",
            "",
            " ",
            "203.0.113.1\n-j ACCEPT",     # newline injection
            "0x7f.0.0.1",
        ]:
            with self.subTest(bad=bad):
                with self.assertRaises(NetworkSetupError):
                    NetConf._validate_ipv4(bad, "255.255.255.0")

    def test_invalid_mask_raises(self) -> None:
        for bad in ["255.255.255.0 extra", "notamask", "", "255.255.255"]:
            with self.subTest(bad=bad):
                with self.assertRaises(NetworkSetupError):
                    NetConf._validate_ipv4("203.0.113.1", bad)

    def test_fuzz_never_other_exception(self) -> None:
        # Whatever the input, validation either passes or raises
        # NetworkSetupError -- never a raw ValueError/TypeError.
        samples = [
            "1.2.3.4", "1.2.3.4 ", " 1.2.3.4", "1.2.3.4;rm -rf", "a.b.c.d",
            "999.999.999.999", "1.2.3.4/255.255.255.0", "\t", "1.2.3.4\x00",
            "12345", "-1.-1.-1.-1", "1.2.3.4 5.6.7.8",
        ]
        for s in samples:
            with self.subTest(s=s):
                try:
                    NetConf._validate_ipv4(s, "255.255.255.0")
                except NetworkSetupError:
                    pass


@patch("blueman.main.NetConf.NetConf._iptables", new=classmethod(lambda cls: "/sbin/iptables"))
class TestIptablesRuleArgs(TestCase):
    def setUp(self) -> None:
        NetConf._ipt_rules = []
        self.addCleanup(lambda: setattr(NetConf, "_ipt_rules", []))

    @patch("blueman.main.NetConf.call", return_value=0)
    def test_args_passed_without_splitting(self, call_mock: Mock) -> None:
        NetConf._add_ipt_rule("nat", "POSTROUTING", "-s", "203.0.113.1/255.255.255.0", "-j", "MASQUERADE")
        call_mock.assert_called_once_with(
            ["/sbin/iptables", "-t", "nat", "-A", "POSTROUTING",
             "-s", "203.0.113.1/255.255.255.0", "-j", "MASQUERADE",
             "-m", "comment", "--comment", "blueman-pan1"])

    @patch("blueman.main.NetConf.call", return_value=0)
    def test_value_with_space_stays_single_arg(self, call_mock: Mock) -> None:
        # A value containing a space must remain one argument, not get split
        # into extra iptables arguments.
        NetConf._add_ipt_rule("filter", "FORWARD", "-s", "1.2.3.4 -j ACCEPT")
        args = call_mock.call_args.args[0]
        self.assertIn("1.2.3.4 -j ACCEPT", args)
        self.assertEqual(args.count("-j"), 0)

    @patch("blueman.main.NetConf.run")
    @patch("blueman.main.NetConf.call", return_value=0)
    def test_flush_deletes_kernel_rules_by_comment(self, call_mock: Mock, run_mock: Mock) -> None:
        # The kernel reports a blueman-tagged rule plus an unrelated one; only
        # the tagged rule must be deleted, regardless of in-memory state.
        def fake_run(args: list, **_kwargs: object) -> Mock:
            if args[2] == "filter" and args[4] == "FORWARD":
                return Mock(stdout=(
                    "-A FORWARD -i pan1 -j ACCEPT -m comment --comment blueman-pan1\n"
                    "-A FORWARD -i eth0 -j ACCEPT\n"))
            return Mock(stdout="")

        run_mock.side_effect = fake_run
        NetConf._ipt_rules = []  # simulate a restarted mechanism with no memory
        NetConf.unlock("iptables")
        NetConf._del_ipt_rules()

        call_mock.assert_called_once_with(
            ["/sbin/iptables", "-t", "filter", "-D", "FORWARD",
             "-i", "pan1", "-j", "ACCEPT", "-m", "comment", "--comment", "blueman-pan1"])
        self.assertEqual(NetConf._ipt_rules, [])


class TestExclusiveLock(TestCase):
    def setUp(self) -> None:
        self.run_dir = Path("/tmp/blueman-lock")
        self.run_dir.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(self.run_dir))
        self.patch = patch.object(NetConf, "_RUN_PATH", self.run_dir)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    @patch("blueman.main.NetConf.fcntl.flock")
    def test_acquires_and_releases_exclusively(self, flock_mock: Mock) -> None:
        with NetConf._exclusive_lock():
            pass
        modes = [c.args[1] for c in flock_mock.call_args_list]
        self.assertEqual(modes, [fcntl.LOCK_EX, fcntl.LOCK_UN])
        self.assertTrue((self.run_dir / "blueman-mechanism.lock").exists())

    @patch("blueman.main.NetConf.fcntl.flock")
    def test_releases_on_exception(self, flock_mock: Mock) -> None:
        with self.assertRaises(ValueError):
            with NetConf._exclusive_lock():
                raise ValueError("boom")
        modes = [c.args[1] for c in flock_mock.call_args_list]
        self.assertIn(fcntl.LOCK_UN, modes)


class TestCommunicateStderr(TestCase):
    def test_returns_stderr_within_timeout(self) -> None:
        p = Mock()
        p.communicate.return_value = (b"", b"some error")
        self.assertEqual(_communicate_stderr(p), b"some error")
        p.communicate.assert_called_once_with(timeout=10)
        p.kill.assert_not_called()

    def test_kills_on_timeout(self) -> None:
        p = Mock()
        p.communicate.side_effect = [subprocess.TimeoutExpired(cmd="dnsmasq", timeout=10), (b"", b"")]
        with self.assertLogs(level="WARNING"):
            result = _communicate_stderr(p)
        p.kill.assert_called_once_with()
        self.assertIn(b"timed out", result)


class TestPollPidFile(TestCase):
    def setUp(self) -> None:
        self.path = Path("/tmp/blueman-poll.pid")
        self.addCleanup(lambda: self.path.unlink(missing_ok=True))

    @patch("blueman.main.NetConf.sleep")
    def test_returns_pid_immediately_when_present(self, sleep_mock: Mock) -> None:
        self.path.write_text("4321")
        self.assertEqual(_poll_pid_file(self.path), 4321)
        sleep_mock.assert_not_called()

    @patch("blueman.main.NetConf.sleep")
    @patch("blueman.main.NetConf._PID_POLL_ATTEMPTS", 4)
    def test_returns_none_after_attempts(self, sleep_mock: Mock) -> None:
        self.assertIsNone(_poll_pid_file(self.path))
        # Sleeps between attempts but not after the final one.
        self.assertEqual(sleep_mock.call_count, 3)

    @patch("blueman.main.NetConf.sleep")
    @patch("blueman.main.NetConf._PID_POLL_ATTEMPTS", 5)
    def test_returns_pid_when_it_appears_late(self, sleep_mock: Mock) -> None:
        calls = {"n": 0}

        def write_on_third(_delay: float) -> None:
            calls["n"] += 1
            if calls["n"] == 2:
                self.path.write_text("77")

        sleep_mock.side_effect = write_on_third
        self.assertEqual(_poll_pid_file(self.path), 77)


class TestPidPath(TestCase):
    def test_pid_path_derives_from_run_path(self) -> None:
        with patch.object(NetConf, "_RUN_PATH", Path("/run")):
            self.assertEqual(DnsMasqHandler()._pid_path, Path("/run/dnsmasq.pan1.pid"))

    def test_pid_path_follows_run_path_override(self) -> None:
        with patch.object(NetConf, "_RUN_PATH", Path("/var/run")):
            self.assertEqual(UdhcpdHandler()._pid_path, Path("/var/run/udhcpd.pan1.pid"))


class TestIptablesResolution(TestCase):
    @patch("blueman.main.NetConf.have", return_value=Path("/usr/sbin/iptables"))
    def test_resolves_via_have(self, have_mock: Mock) -> None:
        self.assertEqual(NetConf._iptables(), "/usr/sbin/iptables")
        have_mock.assert_called_with("iptables")

    @patch("blueman.main.NetConf.have", return_value=None)
    def test_missing_iptables_raises(self, _have_mock: Mock) -> None:
        with self.assertRaises(FileNotFoundError):
            NetConf._iptables()

    @patch("blueman.main.NetConf.have", return_value=Path("/usr/sbin/iptables"))
    @patch("blueman.main.NetConf.call", return_value=0)
    def test_add_rule_uses_resolved_path(self, call_mock: Mock, _have_mock: Mock) -> None:
        self.addCleanup(lambda: setattr(NetConf, "_ipt_rules", []))
        NetConf._ipt_rules = []
        NetConf._add_ipt_rule("filter", "FORWARD", "-i", "pan1", "-j", "ACCEPT")
        self.assertEqual(call_mock.call_args.args[0][0], "/usr/sbin/iptables")

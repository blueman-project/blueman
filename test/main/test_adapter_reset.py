import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

from blueman.main.AdapterReset import (
    AdapterResetError,
    ControllerBinding,
    hci_name_from_path,
    parse_kernel_fault,
    pkexec_command,
    rebind,
    reload_module,
    reset_controller,
    resolve_binding,
)


def make_sysfs(root: Path, hci: str = "hci0", device_id: str = "1-9:1.0", driver: str = "btusb",
               module: bool = True) -> Path:
    driver_dir = root / "bus" / "usb" / "drivers" / driver
    driver_dir.mkdir(parents=True)
    (driver_dir / "bind").write_text("")
    (driver_dir / "unbind").write_text("")
    if module:
        (root / "module" / driver).mkdir(parents=True)
        (driver_dir / "module").symlink_to(root / "module" / driver)
    device = root / "devices" / "usb1" / "1-9" / device_id
    device.mkdir(parents=True)
    (device / "driver").symlink_to(driver_dir)
    hci_dir = root / "class" / "bluetooth" / hci
    hci_dir.mkdir(parents=True)
    (hci_dir / "device").symlink_to(device)
    return driver_dir


class TestHciName(TestCase):
    def test_adapter_paths(self) -> None:
        self.assertEqual(hci_name_from_path("/org/bluez/hci0"), "hci0")
        self.assertEqual(hci_name_from_path("/org/bluez/hci12/"), "hci12")

    def test_rejects_other_paths(self) -> None:
        for path in (None, "", "/org/bluez", "/org/bluez/hci0/dev_00_11_22_33_44_55", "/org/bluez/hci0;rm"):
            self.assertIsNone(hci_name_from_path(path), path)


class TestResolveBinding(TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_resolves_usb_interface_driver_and_module(self) -> None:
        driver_dir = make_sysfs(self.root)
        binding = resolve_binding("hci0", self.root)
        self.assertEqual(binding, ControllerBinding("hci0", "1-9:1.0", driver_dir.resolve(), "btusb"))

    def test_module_is_optional(self) -> None:
        make_sysfs(self.root, module=False)
        self.assertIsNone(resolve_binding("hci0", self.root).module)

    def test_missing_adapter_or_driver(self) -> None:
        with self.assertRaises(AdapterResetError):
            resolve_binding("hci0", self.root)
        make_sysfs(self.root)
        (self.root / "devices" / "usb1" / "1-9" / "1-9:1.0" / "driver").unlink()
        with self.assertRaises(AdapterResetError):
            resolve_binding("hci0", self.root)

    def test_rejects_names_that_are_not_adapters(self) -> None:
        for name in ("../hci0", "hci0/..", "eth0", ""):
            with self.assertRaises(AdapterResetError):
                resolve_binding(name, self.root)


class TestReset(TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.driver_dir = make_sysfs(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_rebind_unbinds_then_binds_the_interface(self) -> None:
        sleep = Mock()
        rebind(resolve_binding("hci0", self.root), sleep)
        self.assertEqual((self.driver_dir / "unbind").read_text(), "1-9:1.0")
        self.assertEqual((self.driver_dir / "bind").read_text(), "1-9:1.0")
        sleep.assert_called_once()

    def test_reset_prefers_rebind(self) -> None:
        run = Mock()
        self.assertEqual(reset_controller("hci0", self.root, sleep=Mock(), run=run), "rebind")
        run.assert_not_called()

    def test_reset_falls_back_to_module_reload(self) -> None:
        (self.driver_dir / "bind").unlink()
        (self.driver_dir / "bind").mkdir()  # writing to a directory raises OSError
        run = Mock()
        self.assertEqual(reset_controller("hci0", self.root, sleep=Mock(), run=run), "reload")
        self.assertEqual([c.args[0] for c in run.call_args_list],
                         [["modprobe", "-r", "btusb"], ["modprobe", "btusb"]])

    def test_reset_reports_reload_failure(self) -> None:
        (self.driver_dir / "unbind").unlink()
        (self.driver_dir / "unbind").mkdir()
        run = Mock(side_effect=subprocess.CalledProcessError(1, "modprobe"))
        with self.assertRaises(AdapterResetError):
            reset_controller("hci0", self.root, sleep=Mock(), run=run)

    def test_reload_rejects_option_like_module_names(self) -> None:
        with self.assertRaises(AdapterResetError):
            reload_module("btusb --all", Mock())


class TestPkexecCommand(TestCase):
    def test_arguments_are_positional(self) -> None:
        binding = ControllerBinding("hci0", "1-9:1.0", Path("/sys/bus/usb/drivers/btusb"), "btusb")
        argv = pkexec_command(binding)
        self.assertEqual(argv[:3], ["pkexec", "/bin/sh", "-c"])
        self.assertEqual(argv[4:], ["sh", "1-9:1.0", "/sys/bus/usb/drivers/btusb", "btusb"])
        self.assertNotIn("1-9:1.0", argv[3])

    def test_without_module_only_rebinds(self) -> None:
        argv = pkexec_command(ControllerBinding("hci0", "serial0-0", Path("/sys/bus/serial/drivers/hci_uart_h5"),
                                                None))
        self.assertNotIn("modprobe", argv[3])
        self.assertEqual(argv[4:], ["sh", "serial0-0", "/sys/bus/serial/drivers/hci_uart_h5"])


class TestKernelFaults(TestCase):
    def test_recognises_controller_timeouts(self) -> None:
        cases = {
            "Bluetooth: hci0: command 0x0c1a tx timeout": "command 0x0c1a tx timeout",
            "Oct 31 17:02:02 dorin kernel: Bluetooth: hci0: Opcode 0x0c24 failed: -110": "Opcode 0x0c24 failed: -110",
            "Bluetooth: hci1: Resetting usb device.": "Resetting usb device",
            "Bluetooth: hci0: hardware error 0x00": "hardware error 0x00",
            "Bluetooth: hci0: Reading Intel version command timed out": "Reading Intel version command timed out",
        }
        for line, message in cases.items():
            fault = parse_kernel_fault(line)
            self.assertIsNotNone(fault, line)
            assert fault is not None
            self.assertEqual(fault.message, message)
        self.assertEqual(parse_kernel_fault("Bluetooth: hci1: Resetting usb device.").hci, "hci1")  # type: ignore

    def test_ignores_normal_startup(self) -> None:
        for line in (
            "Bluetooth: hci0: Legacy ROM 2.x revision 5.0 build 25 week 20 2015",
            "Bluetooth: hci0: Intel Bluetooth firmware file: intel/ibt-hw-37.8.10-fw-22.50.19.14.f.bseq",
            "Bluetooth: hci0: Intel BT fw patch 0x43 completed & activated",
            "Bluetooth: MGMT ver 1.22",
            "usbcore: registered new interface driver btusb",
            "Bluetooth: hci0: Opcode 0x0c24 failed: -16",
        ):
            self.assertIsNone(parse_kernel_fault(line), line)

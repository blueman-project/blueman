"""Recover a Bluetooth controller that stopped responding, and recognise when it has.

Some controllers (notably Intel USB parts with autosuspend) stop discovering until their
driver is reloaded. The reset here unbinds and rebinds only that adapter's device from its
kernel driver, which is what ``modprobe -r btusb && modprobe btusb`` achieves without
touching other adapters. Reloading the driver module is the fallback.

The module has no GTK or D-Bus dependency: the root mechanism uses it to reset, and the
manager uses it to read the kernel log and to build the ``pkexec`` fallback command.
"""

import logging
import re
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

SYSFS_ROOT = Path("/sys")

# Kernel identifiers are written into sysfs files and passed to modprobe; reject anything
# that is not a plain name so no path or option can be smuggled in.
_HCI_RE = re.compile(r"^hci\d{1,3}$")
_DEVICE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._-]*$")
_MODULE_RE = re.compile(r"^[A-Za-z0-9_-]+$")

# Gives the driver time to release the device before it is bound again.
REBIND_SETTLE_SECONDS = 1.0

# Shell script run under pkexec when the installed mechanism predates ResetAdapter.
# Arguments are passed positionally, never interpolated into the script.
_PKEXEC_REBIND_SCRIPT = (
    'printf %s "$1" > "$2/unbind" && sleep 1 && printf %s "$1" > "$2/bind"'
    ' || { modprobe -r "$3" && modprobe "$3"; }'
)
_PKEXEC_RELOAD_SCRIPT = 'modprobe -r "$1" && modprobe "$1"'


class AdapterResetError(Exception):
    pass


@dataclass(frozen=True)
class ControllerBinding:
    """Where an HCI adapter's device sits in sysfs and which driver owns it."""
    hci: str
    device_id: str
    driver_dir: Path
    module: str | None


def hci_name_from_path(object_path: str | None) -> str | None:
    """``/org/bluez/hci0`` → ``hci0``; ``None`` for anything that is not an adapter path."""
    if not object_path:
        return None
    name = object_path.rstrip("/").rsplit("/", 1)[-1]
    return name if _HCI_RE.match(name) else None


def resolve_binding(hci: str, sysfs_root: Path = SYSFS_ROOT) -> ControllerBinding:
    if not _HCI_RE.match(hci):
        raise AdapterResetError(f"Not an adapter name: {hci!r}")
    device = sysfs_root / "class" / "bluetooth" / hci / "device"
    if not device.exists():
        raise AdapterResetError(f"{hci} has no device in sysfs")
    device_id = device.resolve().name
    driver = device / "driver"
    if not driver.exists():
        raise AdapterResetError(f"{hci} is not bound to a driver")
    driver_dir = driver.resolve()
    module_link = driver_dir / "module"
    module = module_link.resolve().name if module_link.exists() else None
    if not _DEVICE_ID_RE.match(device_id):
        raise AdapterResetError(f"Unexpected device id {device_id!r}")
    if module is not None and not _MODULE_RE.match(module):
        module = None
    return ControllerBinding(hci, device_id, driver_dir, module)


def rebind(binding: ControllerBinding, sleep: Callable[[float], None] = time.sleep) -> None:
    (binding.driver_dir / "unbind").write_text(binding.device_id)
    sleep(REBIND_SETTLE_SECONDS)
    (binding.driver_dir / "bind").write_text(binding.device_id)


def reload_module(module: str, run: Callable[..., object] = subprocess.run) -> None:
    if not _MODULE_RE.match(module):
        raise AdapterResetError(f"Unexpected module name {module!r}")
    run(["modprobe", "-r", module], check=True, timeout=30)
    run(["modprobe", module], check=True, timeout=30)


def reset_controller(hci: str, sysfs_root: Path = SYSFS_ROOT,
                     sleep: Callable[[float], None] = time.sleep,
                     run: Callable[..., object] = subprocess.run) -> str:
    """Reset ``hci`` as root; returns ``"rebind"`` or ``"reload"`` naming what worked."""
    binding = resolve_binding(hci, sysfs_root)
    try:
        rebind(binding, sleep)
        return "rebind"
    except OSError as e:
        logging.warning(f"Rebinding {binding.device_id} to {binding.driver_dir.name} failed: {e}")
        if binding.module is None:
            raise AdapterResetError(f"Could not rebind {hci}: {e}") from e
    try:
        reload_module(binding.module, run)
    except (OSError, subprocess.SubprocessError) as e:
        raise AdapterResetError(f"Could not reload {binding.module}: {e}") from e
    return "reload"


def pkexec_command(binding: ControllerBinding) -> list[str]:
    """Command that performs the same reset through pkexec, for an older mechanism."""
    if binding.module is None:
        return ["pkexec", "/bin/sh", "-c", 'printf %s "$1" > "$2/unbind" && sleep 1 && printf %s "$1" > "$2/bind"',
                "sh", binding.device_id, binding.driver_dir.as_posix()]
    return ["pkexec", "/bin/sh", "-c", _PKEXEC_REBIND_SCRIPT, "sh",
            binding.device_id, binding.driver_dir.as_posix(), binding.module]


@dataclass(frozen=True)
class KernelFault:
    hci: str
    message: str


# Messages the kernel prints when a controller stops answering HCI commands. -110 is
# ETIMEDOUT. Ordinary start-up lines (firmware, patch, MGMT) never match.
_KERNEL_FAULT_RE = re.compile(
    r"Bluetooth: (?P<hci>hci\d+): (?P<message>"
    r"command 0x[0-9a-fA-F]+ tx timeout"
    r"|Opcode 0x[0-9a-fA-F]+ failed: -110"
    r"|Resetting usb device\.?"
    r"|hardware error 0x[0-9a-fA-F]+"
    r"|[^\n]*\btimed out\b[^\n]*"
    r")"
)


def parse_kernel_fault(line: str) -> KernelFault | None:
    match = _KERNEL_FAULT_RE.search(line)
    if match is None:
        return None
    return KernelFault(match.group("hci"), match.group("message").rstrip("."))

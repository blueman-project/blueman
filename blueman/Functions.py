# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from time import sleep
from typing import Optional, Dict, Tuple, List, Callable, Iterable, Union, Any
import re
import os
import sys
import errno
from gettext import gettext as _
import logging
import logging.handlers
import argparse
from ctypes import cdll, byref, create_string_buffer
import traceback
import fcntl
import struct
import socket
import array
import time

import cairo

from blueman.main.Config import Config
from blueman.main.DBusProxies import AppletService, DBusProxyFailed
from blueman.Constants import BIN_DIR, ICON_PATH

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gio

__all__ = ["check_bluetooth_status", "launch", "setup_icon_path", "adapter_path_to_name", "e_", "bmexit",
           "format_bytes", "create_menuitem", "have", "set_proc_title", "create_logger", "create_parser", "open_rfcomm",
           "get_local_interfaces"]


def check_bluetooth_status(message: str, exitfunc: Callable[[], Any]) -> None:
    try:
        applet = AppletService()
    except DBusProxyFailed as e:
        logging.exception(e)
        print("Blueman applet needs to be running")
        exitfunc()
        return

    if "PowerManager" not in applet.QueryPlugins():
        return

    if not applet.GetBluetoothStatus():
        d = Gtk.MessageDialog(
            type=Gtk.MessageType.ERROR, icon_name="blueman",
            text=_("Bluetooth Turned Off"), secondary_text=message)
        d.add_button(_("Exit"), Gtk.ResponseType.NO)
        d.add_button(_("Enable Bluetooth"), Gtk.ResponseType.YES)

        resp = d.run()
        d.destroy()

        if resp != Gtk.ResponseType.YES:
            exitfunc()
            return

    applet.SetBluetoothStatus('(b)', True)
    if not applet.GetBluetoothStatus():
        print('Failed to enable bluetooth')
        exitfunc()
        return

    config = Config("org.blueman.plugins.powermanager")
    if config["auto-power-on"] is None:
        d = Gtk.MessageDialog(
            type=Gtk.MessageType.QUESTION, icon_name="blueman",
            text=_("Shall bluetooth get enabled automatically?"))
        d.add_button(_("Yes"), Gtk.ResponseType.YES)
        d.add_button(_("No"), Gtk.ResponseType.NO)

        resp = d.run()
        d.destroy()

        config["auto-power-on"] = resp == Gtk.ResponseType.YES


def launch(
    cmd: str,
    paths: Optional[Iterable[str]] = None,
    system: bool = False,
    icon_name: Optional[str] = None,
    name: str = "blueman",
    sn: bool = True,
) -> bool:
    """Launch a gui app with starup notification"""
    context = None
    gtktimestamp = Gtk.get_current_event_time()
    if gtktimestamp == 0:
        logging.info("Gtk eventtime is 0, not using LaunchContext")
        timestamp = int(time.clock_gettime(time.CLOCK_MONOTONIC_RAW))
    else:
        timestamp = gtktimestamp
        display = Gdk.Display.get_default()
        assert display
        context = display.get_app_launch_context()
        context.set_timestamp(timestamp)

    if sn:
        flags = Gio.AppInfoCreateFlags.SUPPORTS_STARTUP_NOTIFICATION
    else:
        flags = Gio.AppInfoCreateFlags.NONE

    env = os.environ
    env["BLUEMAN_EVENT_TIME"] = str(timestamp)

    if not system:
        cmd = os.path.join(BIN_DIR, cmd)
    else:
        cmd = os.path.expanduser(cmd)

    if paths:
        files: Optional[List[Gio.File]] = [Gio.File.new_for_commandline_arg(p) for p in paths]
    else:
        files = None

    if icon_name and context is not None:
        context.set_icon_name(icon_name)

    appinfo = Gio.AppInfo.create_from_commandline(cmd, name, flags)
    launched: bool = appinfo.launch(files, context)

    if not launched:
        logging.error(f"Command: {cmd} failed")

    return launched


def setup_icon_path() -> None:
    ic = Gtk.IconTheme.get_default()
    ic.prepend_search_path(ICON_PATH)


def adapter_path_to_name(path: Optional[str]) -> Optional[str]:
    if path is None or path == '':
        return None

    match = re.search(r".*(hci[0-9]*)", path)
    if match:
        return match.group(1)
    return None


# format error
def e_(msg: Union[str, Exception]) -> Tuple[str, Optional[str]]:
    if isinstance(msg, Exception):
        return str(msg), traceback.format_exc()
    else:
        s = msg.strip().split(": ")[-1]
        return s, None


def format_bytes(size: float) -> Tuple[float, str]:
    size = float(size)
    if size < 1024:
        ret = size
        suffix = "B"
    elif 1024 < size < (1024 * 1024):
        ret = size / 1024
        suffix = "KB"
    elif (1024 * 1024) < size < (1024 * 1024 * 1024):
        ret = size / (1024 * 1024)
        suffix = "MB"
    else:
        ret = size / (1024 * 1024 * 1024)
        suffix = "GB"

    return ret, suffix


def create_menuitem(
    text: str,
    icon_name: Optional[str] = None,
    pixbuf: Optional[GdkPixbuf.Pixbuf] = None,
    surface: Optional[cairo.Surface] = None,
) -> Gtk.ImageMenuItem:
    image = Gtk.Image(pixel_size=16)
    if icon_name:
        image.set_from_icon_name(icon_name, Gtk.IconSize.MENU)
    elif surface:
        image.set_from_surface(surface)
    elif pixbuf:
        image.set_from_pixbuf(pixbuf)
    else:
        raise ValueError("At least provide one of, icon name, surface or pixbuf")

    item = Gtk.ImageMenuItem(label=text, image=image, use_underline=True)
    child = item.get_child()
    assert isinstance(child, Gtk.AccelLabel)
    child.set_use_markup(True)
    item.show_all()

    return item


def have(t: str) -> Optional[str]:
    paths = os.environ['PATH'] + ':/sbin:/usr/sbin'
    for path in paths.split(os.pathsep):
        exec_path = os.path.join(path, t)
        exists = os.path.exists(exec_path)
        executable = os.access(exec_path, os.EX_OK)
        if exists and executable:
            return exec_path
    return None


def set_proc_title(name: Optional[str] = None) -> int:
    """Set the process title"""

    if not name:
        name = os.path.basename(sys.argv[0])

    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(name) + 1)
    buff.value = name.encode("UTF-8")
    ret: int = libc.prctl(15, byref(buff), 0, 0, 0)

    if ret != 0:
        logging.error("Failed to set process title")

    return ret


logger_format = '%(name)s %(asctime)s %(levelname)-8s %(module)s:%(lineno)s %(funcName)-10s: %(message)s'
syslog_logger_format = '%(name)s %(levelname)s %(module)s:%(lineno)s %(funcName)s: %(message)s'
logger_date_fmt = '%H.%M.%S'


def create_logger(
    log_level: int,
    name: str,
    log_format: Optional[str] = None,
    date_fmt: Optional[str] = None,
    syslog: bool = False,
) -> logging.Logger:
    if log_format is None:
        log_format = logger_format
    if date_fmt is None:
        date_fmt = logger_date_fmt
    logging.basicConfig(level=log_level, format=log_format, datefmt=date_fmt)

    logger = logging.getLogger(None)  # Root logger
    logger.name = name

    if syslog:
        syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
        syslog_formatter = logging.Formatter(syslog_logger_format)
        syslog_handler.setFormatter(syslog_formatter)
        logger.addHandler(syslog_handler)

    return logger


def create_parser(
    parser: Optional[argparse.ArgumentParser] = None,
    syslog: bool = True,
    loglevel: bool = True,
) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser()

    if loglevel:
        parser.add_argument("--loglevel", dest="LEVEL", default="warning")

    if syslog:
        parser.add_argument("--syslog", dest="syslog", action="store_true")

    return parser


def open_rfcomm(file: str, mode: int) -> int:
    try:
        return os.open(file, mode | os.O_EXCL | os.O_NONBLOCK | os.O_NOCTTY)
    except OSError as err:
        if err.errno == errno.EBUSY:
            logging.warning(f"{file} is busy, delaying 2 seconds")
            sleep(2)
            return open_rfcomm(file, mode)
        else:
            raise


def _netmask_for_ifacename(name: str, sock: socket.socket) -> Optional[str]:
    siocgifnetmask = 0x891b
    bytebuf = struct.pack('256s', name.encode('utf-8'))
    try:
        ret = fcntl.ioctl(sock.fileno(), siocgifnetmask, bytebuf)
    except OSError:
        logging.error('siocgifnetmask failed')
        return None

    return socket.inet_ntoa(ret[20:24])


def get_local_interfaces() -> Dict[str, Tuple[str, Optional[str]]]:
    """ Returns a dictionary of name:ip, mask key value pairs. """
    siocgifconf = 0x8912
    names = array.array('B', 4096 * b'\0')
    names_address, names_length = names.buffer_info()
    mutable_byte_buffer = struct.pack('iL', 4096, names_address)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                mutated_byte_buffer = fcntl.ioctl(sock.fileno(), siocgifconf, mutable_byte_buffer)
            except OSError:
                logging.error('siocgifconf failed')
                return {}

            max_bytes_out, names_address_out = struct.unpack('iL', mutated_byte_buffer)
            namestr = names.tobytes()

            ip_dict = {}
            for i in range(0, max_bytes_out, 40):
                name = namestr[i: i + 16].split(b'\0', 1)[0].decode('utf-8')
                ipaddr = socket.inet_ntoa(namestr[i + 20: i + 24])
                mask = _netmask_for_ifacename(name, sock)
                ip_dict[name] = (ipaddr, mask)
    except OSError:
        logging.error('Socket creation failed', exc_info=True)
        return {}

    return ip_dict


def bmexit(msg: Optional[Union[str, int]] = None) -> None:
    raise SystemExit(msg)

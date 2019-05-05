# coding=utf-8
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
import re
import os
import signal
import atexit
import sys
import errno
import logging
import logging.handlers
import argparse
from ctypes import cdll, byref, create_string_buffer
import traceback
import fcntl
import struct
import termios

from blueman.main.Config import Config

try:
    in_fg = os.getpgrp() == struct.unpack(str('h'), fcntl.ioctl(0, termios.TIOCGPGRP, "  "))[0]
except IOError:
    in_fg = 'DEBUG' in os.environ

from blueman.main.DBusProxies import AppletService, DBusProxyFailed
from blueman.Constants import *

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gio


__all__ = ["check_bluetooth_status", "launch", "setup_icon_path", "get_icon",
           "get_notification_icon", "adapter_path_to_name", "e_", "opacify_pixbuf", "composite_icon",
           "format_bytes", "create_menuitem", "get_lockfile", "get_pid", "is_running", "check_single_instance", "kill",
           "have", "set_proc_title", "create_logger", "create_parser", "open_rfcomm"]


def check_bluetooth_status(message, exitfunc):
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
            None, type=Gtk.MessageType.ERROR, icon_name="blueman",
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
            None, type=Gtk.MessageType.QUESTION, icon_name="blueman",
            text=_("Shall bluetooth get enabled automatically?"))
        d.add_button(_("Yes"), Gtk.ResponseType.YES)
        d.add_button(_("No"), Gtk.ResponseType.NO)

        resp = d.run()
        d.destroy()

        config["auto-power-on"] = resp == Gtk.ResponseType.YES


def launch(cmd, paths=None, system=False, icon_name=None, sn=True, name="blueman"):
    """Launch a gui app with starup notification"""
    display = Gdk.Display.get_default()
    timestamp = Gtk.get_current_event_time()
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
        files = [Gio.File.new_for_commandline_arg(p) for p in paths]
    else:
        files = None

    if icon_name:
        icon = Gio.Icon.new_for_string(icon_name)
        context.set_icon(icon)

    appinfo = Gio.AppInfo.create_from_commandline(cmd, name, flags)
    launched = appinfo.launch(files, context)

    if not launched:
        logging.error("Command: %s failed" % cmd)

    return launched


def setup_icon_path():
    ic = Gtk.IconTheme.get_default()
    ic.prepend_search_path(ICON_PATH)


def get_icon(name, size=24, fallback="image-missing"):
    ic = Gtk.IconTheme.get_default()

    try:
        icon = ic.load_icon(name, size, 0)
    except GLib.Error:
        if not fallback:
            raise
        try:
            icon = ic.load_icon(fallback, size, 0)
        except GLib.Error:
            icon = ic.load_icon("image-missing", size, 0)

    if icon.props.width > size:
        new_w = size
        new_h = int(size * (float(icon.props.width) / icon.props.height))
        icon = icon.scale_simple(new_w, new_h, GdkPixbuf.InterpType.BILINEAR)

    if icon.props.height > size:
        new_w = int(size * (float(icon.props.height) / icon.props.width))
        new_h = size
        icon = icon.scale_simple(new_w, new_h, GdkPixbuf.InterpType.BILINEAR)

    return icon


def get_notification_icon(icon, main_icon="blueman"):
    main = get_icon(main_icon, 48)
    sub = get_icon(icon, 24)

    return composite_icon(main, [(sub, 24, 24, 255)])


def adapter_path_to_name(path):
    if path is None or path == '':
        return

    match = re.search(r".*(hci[0-9]*)", path)
    if match:
        return match.group(1)


# format error
def e_(msg):
    if isinstance(msg, Exception):
        return str(msg), traceback.format_exc()
    else:
        s = msg.strip().split(": ")[-1]
        return s, None


def opacify_pixbuf(pixbuf, alpha):
    new = pixbuf.copy()
    new.fill(0x00000000)
    pixbuf.composite(new, 0, 0, pixbuf.props.width, pixbuf.props.height, 0, 0, 1, 1,
                     GdkPixbuf.InterpType.BILINEAR, alpha)
    return new


# pixbuf, [(pixbuf, x, y, alpha), (pixbuf, x, y, alpha)]

def composite_icon(target, sources):
    target = target.copy()
    for source in sources:
        source[0].composite(target, source[1], source[2], source[0].get_width(), source[0].get_height(), source[1],
                            source[2], 1, 1, GdkPixbuf.InterpType.NEAREST, source[3])

    return target


def format_bytes(size):
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


def create_menuitem(text, icon_name=None, pixbuf=None, surface=None):
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
    child.set_use_markup(True)
    item.show_all()

    return item


def get_lockfile(name):
    cachedir = GLib.get_user_cache_dir()
    if not os.path.exists(cachedir):
        try:
            os.mkdir(cachedir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return os.path.join(cachedir, "%s-%s" % (name, os.getuid()))


def get_pid(lockfile):
    try:
        with open(lockfile, "r") as f:
            return int(f.readline())
    except (ValueError, IOError):
        pass


def is_running(name, pid):
    if not os.path.exists("/proc/%s" % pid):
        return False

    with open("/proc/%s/cmdline" % pid, "r") as f:
        return name in f.readline().replace("\0", " ")


def check_single_instance(name, unhide_func=None):
    print("%s version %s starting" % (name, VERSION))
    lockfile = get_lockfile(name)

    def handler(signum, frame):
        if unhide_func:
            try:
                with open(lockfile, "r") as f:
                    f.readline()
                    event_time = int(f.readline())
            except ValueError:
                event_time = 0

            unhide_func(event_time)

    signal.signal(signal.SIGUSR1, handler)

    if os.path.exists(lockfile):
        pid = get_pid(lockfile)
        if pid:
            if not is_running(name, pid):
                print("Stale PID, overwriting")
                os.remove(lockfile)
            else:
                print("There is an instance already running")
                time = os.getenv("BLUEMAN_EVENT_TIME") or 0

                with open(lockfile, "w") as f:
                    f.write("%s\n%s" % (str(pid), str(time)))

                os.kill(pid, signal.SIGUSR1)
                exit()
        else:
            os.remove(lockfile)

    try:
        fd = os.open(lockfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o664)
        pid_str = "%s\n%s" % (str(os.getpid()), "0")
        os.write(fd, pid_str.encode("UTF-8"))
        os.close(fd)
    except OSError:
        print("There is an instance already running")
        exit()

    atexit.register(lambda: os.remove(lockfile))


def kill(pid, name):
    if pid and is_running(name, pid):
        print('Terminating ' + name)
        os.kill(pid, signal.SIGTERM)
        return True
    return False


def have(t):
    paths = os.environ['PATH'] + ':/sbin:/usr/sbin'
    for path in paths.split(os.pathsep):
        exec_path = os.path.join(path, t)
        exists = os.path.exists(exec_path)
        executable = os.access(exec_path, os.EX_OK)
        if exists and executable:
            return exec_path
    return None


def set_proc_title(name=None):
    """Set the process title"""

    if not name:
        name = os.path.basename(sys.argv[0])

    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(name) + 1)
    buff.value = name.encode("UTF-8")
    ret = libc.prctl(15, byref(buff), 0, 0, 0)

    if ret != 0:
        logging.error("Failed to set process title")

    return ret


logger_format = '%(name)s %(asctime)s %(levelname)-8s %(module)s:%(lineno)s %(funcName)-10s: %(message)s'
syslog_logger_format = '%(name)s %(levelname)s %(module)s:%(lineno)s %(funcName)s: %(message)s'
logger_date_fmt = '%H.%M.%S'


def create_logger(log_level, name, log_format=None, date_fmt=None, syslog=False):
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


def create_parser(parser=None, syslog=True, loglevel=True):
    if parser is None:
        parser = argparse.ArgumentParser()

    if loglevel:
        parser.add_argument("--loglevel", dest="LEVEL", default="warning")

    if syslog:
        parser.add_argument("--syslog", dest="syslog", action="store_true")

    return parser


def open_rfcomm(file, mode):
    try:
        return os.open(file, mode | os.O_EXCL | os.O_NONBLOCK | os.O_NOCTTY)
    except OSError as err:
        if err.errno == errno.EBUSY:
            logging.warning('%s is busy, delaying 2 seconds' % file)
            sleep(2)
            return open_rfcomm(file, mode)
        else:
            raise

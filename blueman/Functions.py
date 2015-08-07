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

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from io import open

from blueman.Constants import *

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gio
import re
import os
import signal
import atexit
import sys
from ctypes import cdll, byref, create_string_buffer
from subprocess import Popen
from gi.repository import GObject
import traceback
try: import __builtin__ as builtins
except ImportError: import builtins

GREEN = lambda x: "\x1b[32;01m" + x + "\x1b[39;49;00m"
BLUE = lambda x: "\x1b[34;01m" + x + "\x1b[39;49;00m"
BOLD = lambda x: "\033[1m" + x + "\033[0m"
YELLOW = lambda x: "\x1b[33;01m" + x + "\x1b[39;49;00m"

import fcntl, struct, termios

try:
    in_fg = os.getpgrp() == struct.unpack(str('h'), fcntl.ioctl(0, termios.TIOCGPGRP, "  "))[0]
except IOError:
    in_fg = 'DEBUG' in os.environ


def dprint(*args):
    #dont print if in the background
    if in_fg:

        s = ""
        for a in args:
            s += ("%s " % a)
        co = sys._getframe(1).f_code

        fname = BOLD(co.co_name)

        print("_________")
        print("%s %s" % (fname, "(%s:%d)" % (co.co_filename, co.co_firstlineno)))
        print(s)
        try:
            sys.stdout.flush()
        except IOError:
            pass


builtins.dprint = dprint

from blueman.main.AppletService import AppletService


def check_bluetooth_status(message, exitfunc, *args, **kwargs):
    try:
        applet = AppletService()
    except:
        print("Blueman applet needs to be running")
        exitfunc()
    if "PowerManager" in applet.QueryPlugins():
        if not applet.GetBluetoothStatus():

            d = Gtk.MessageDialog(None, type=Gtk.MessageType.ERROR)
            d.props.icon_name = "blueman"
            d.props.text = _("Bluetooth Turned Off")
            d.props.secondary_text = message

            d.add_button("Exit", Gtk.ResponseType.NO)
            d.add_button(_("Enable Bluetooth"), Gtk.ResponseType.YES)
            resp = d.run()
            d.destroy()
            if resp != Gtk.ResponseType.YES:
                exitfunc()
            else:
                applet.SetBluetoothStatus(True, *args, **kwargs)


def wait_for_adapter(bluez_adapter, callback, timeout=1000):
    def on_prop_change(key, value):
        if key == "Powered" and value:
            GObject.source_remove(source)
            bluez_adapter.unhandle_signal(on_prop_change, "PropertyChanged")
            callback()

    def on_timeout():
        bluez_adapter.unhandle_signal(on_prop_change, "PropertyChanged")
        GObject.source_remove(source)
        dprint(YELLOW("Warning:"),
               "Bluez didn't provide 'Powered' property in a reasonable timeout\nAssuming adapter is ready")
        callback()

    props = bluez_adapter.get_properties()
    if props["Address"] != "00:00:00:00:00:00":
        callback()
        return

    source = GObject.timeout_add(timeout, on_timeout)
    bluez_adapter.handle_signal(on_prop_change, "PropertyChanged")


def enable_rgba_colormap():
    #screen = Gdk.Display.get_default().get_default_screen()
    #colormap = screen.get_rgba_colormap()
    #if colormap == None:
    #	colormap = screen.get_rgb_colormap()
    #Gtk.widget_set_default_colormap(colormap)
    pass


def launch(cmd, paths=None, system=False, icon_name=None, sn=True, name="blueman"):
    '''Launch a gui app with starup notification'''
    display = Gdk.Display.get_default()
    timestamp = Gtk.get_current_event_time()
    context = display.get_app_launch_context()
    context.set_timestamp(timestamp)
    if sn: flags = Gio.AppInfoCreateFlags.SUPPORTS_STARTUP_NOTIFICATION
    else: flags = Gio.AppInfoCreateFlags.NONE

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
        dprint("Command: %s failed" % cmd)

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
        new_h = int(size * ( float(icon.props.width) / icon.props.height ))
        icon = icon.scale_simple(new_w, new_h, GdkPixbuf.InterpType.BILINEAR)

    if icon.props.height > size:
        new_w = int(size * ( float(icon.props.height) / icon.props.width ))
        new_h = size
        icon = icon.scale_simple(new_w, new_h, GdkPixbuf.InterpType.BILINEAR)

    return icon


def get_notification_icon(icon, main_icon="blueman"):
    main = get_icon(main_icon, 48)
    sub = get_icon(icon, 24)

    return composite_icon(main, [(sub, 24, 24, 255)])


def adapter_path_to_name(path):
    return re.search(".*(hci[0-9]*)", path).groups(0)[0]

#format error
def e_(msg):
    if isinstance(msg, Exception):
        return str(msg) + "\n" + traceback.format_exc()
    else:
        msg = str(msg)

        s = msg.split(": ")
        del s[0]
        return ": ".join(s)


def opacify_pixbuf(pixbuf, alpha):
    new = pixbuf.copy()
    new.fill(0x00000000)
    pixbuf.composite(new, 0, 0, pixbuf.props.width, pixbuf.props.height, 0, 0, 1, 1, GdkPixbuf.InterpType.BILINEAR, alpha)
    return new

#pixbuf, [(pixbuf, x, y, alpha), (pixbuf, x, y, alpha)]

def composite_icon(target, sources):
    target = target.copy()
    for source in sources:
        source[0].composite(target, source[1], source[2], source[0].get_width(), source[0].get_height(), source[1],
                            source[2], 1, 1, GdkPixbuf.InterpType.NEAREST, source[3])

    return target


def format_bytes(size):
    ret = 0.0
    size = float(size)
    suffix = ""
    if size < 1024:
        ret = size
        suffix = "B"
    elif size > 1024 and size < (1024 * 1024):
        ret = size / 1024
        suffix = "KB"
    elif size > (1024 * 1024) and size < (1024 * 1024 * 1024):
        ret = size / (1024 * 1024)
        suffix = "MB"
    else:
        ret = size / (1024 * 1024 * 1024)
        suffix = "GB"

    return (ret, suffix)


def create_menuitem_box(text, pixbuf, orientation=Gtk.Orientation.HORIZONTAL, size=6):
    '''Create a box with icon and label, optinally set size and orientation'''
    item_box = Gtk.Box.new(orientation, size)
    icon = Gtk.Image.new_from_pixbuf(pixbuf)
    label = Gtk.Label.new_with_mnemonic(text)

    item_box.add(icon)
    item_box.add(label)

    return item_box

def create_menuitem(text, pixbuf):
    box = create_menuitem_box(text, pixbuf)
    item = Gtk.MenuItem()
    item.add(box)
    item.show_all()

    return item


def get_lockfile(name):
    cachedir = GLib.get_user_cache_dir()
    if not os.path.exists(cachedir):
        os.mkdir(cachedir)
    return os.path.join(cachedir, "%s-%s" % (name, os.getuid()))


def get_pid(lockfile):
    f = open(lockfile)
    try:
        return int(f.readline())
    except:
        pass
    finally:
        f.close()


def is_running(name, pid):
    if not os.path.exists("/proc/%s" % pid):
        return False
    f = open("/proc/%s/cmdline" % pid)
    try:
        return name in f.readline().replace("\0", " ")
    finally:
        f.close()


def check_single_instance(name, unhide_func=None):
    print("%s version %s starting" % (name, VERSION))
    lockfile = get_lockfile(name)

    def handler(signum, frame):
        if unhide_func:
            f = open(lockfile)
            f.readline()
            try:
                event_time = int(f.readline())
            except:
                event_time = 0
            f.close()
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

                f = open(lockfile, "w")
                f.write("%s\n%s" % (str(pid), str(time)))
                f.close()

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


def have(t):
    paths = os.environ['PATH'] + ':/sbin:/usr/sbin'
    for path in paths.split(os.pathsep):
        exec_path = os.path.join(path, t)
        exists = os.path.exists(exec_path)
        executable = os.access(exec_path, os.EX_OK)
        if exists and executable:
            return exec_path
    return None

def mask_ip4_address(ip, subnet):
    masked_ip = bytearray()

    for x, y in zip(bytearray(ip), bytearray(subnet)):
        masked_ip.append(x & y)

    return bytes(masked_ip)

def set_proc_title(name=None):
    '''Set the process title'''

    if not name:
        name = os.path.basename(sys.argv[0])

    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(name)+1)
    buff.value = name.encode("UTF-8")
    ret = libc.prctl(15, byref(buff), 0, 0, 0)

    if ret != 0:
        dprint("Failed to set process title")

    return ret

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

from blueman.Constants import *

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import re
import os
import signal
import atexit
import sys
from subprocess import Popen, call
import subprocess
import commands
from gi.repository import GObject
import traceback
from blueman.Lib import sn_launcher
import __builtin__

GREEN = lambda (x): "\x1b[32;01m" + x + "\x1b[39;49;00m"
BLUE = lambda (x): "\x1b[34;01m" + x + "\x1b[39;49;00m"
BOLD = lambda (x): "\033[1m" + x + "\033[0m"
YELLOW = lambda (x): "\x1b[33;01m" + x + "\x1b[39;49;00m"

import fcntl, struct, termios

try:
    in_fg = os.getpgrp() == struct.unpack('h', fcntl.ioctl(0, termios.TIOCGPGRP, "  "))[0]
except:
    in_fg = False


def dprint(*args):
    #dont print if in the background
    if in_fg:

        s = ""
        for a in args:
            s += (str(a) + " ")
        co = sys._getframe(1).f_code

        fname = BOLD(co.co_name)

        print "_________"
        print "%s %s" % (fname, "(%s:%d)" % (co.co_filename, co.co_firstlineno))
        print s
        try:
            sys.stdout.flush()
        except IOError:
            pass


__builtin__.dprint = dprint

from blueman.main.AppletService import AppletService


def check_bluetooth_status(message, exitfunc, *args, **kwargs):
    try:
        applet = AppletService()
    except:
        print "Blueman applet needs to be running"
        exitfunc()
    if "PowerManager" in applet.QueryPlugins():
        if not applet.GetBluetoothStatus():

            d = Gtk.MessageDialog(None, type=Gtk.MessageType.ERROR)
            d.props.icon_name = "blueman"
            d.props.text = _("Bluetooth Turned Off")
            d.props.secondary_text = message

            d.add_button(Gtk.STOCK_QUIT, Gtk.ResponseType.NO)
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


def startup_notification(name, desc=None, bin_name=None, icon=None):
    dpy = Gdk.Display.get_default()
    #FIXME this will work with GTK3
    #screen = dpy.get_default_screen().get_number()
    screen = Gdk.Screen.get_default().get_number()
    sn = sn_launcher(dpy, screen)
    sn.set_name(name)

    if bin_name:
        sn.set_binary_name(bin_name.encode('UTF-8'))
    if icon:
        sn.set_icon_name(icon.encode('UTF-8'))

    if desc:
        sn.set_description(desc.encode('UTF-8'))

    sn.initiate("", "", Gtk.get_current_event_time())

    return sn


def enable_rgba_colormap():
    #screen = Gdk.Display.get_default().get_default_screen()
    #colormap = screen.get_rgba_colormap()
    #if colormap == None:
    #	colormap = screen.get_rgb_colormap()
    #Gtk.widget_set_default_colormap(colormap)
    pass


def spawn(command, system=False, sn=None, reap=True, *args, **kwargs):
    def child_closed(pid, cond):
        dprint(command, "closed")
        if sn:
            sn.complete()

    if not system:
        if type(command) == list:
            command[0] = os.path.join(BIN_DIR, command[0])
        else:
            command = os.path.join(BIN_DIR, command)
    else:
        if type(command) == list:
            command[0] = os.path.expanduser(command[0])
        else:
            command = os.path.expanduser(command)

    env = os.environ

    if sn:
        id = sn.get_startup_id()
        env["DESKTOP_STARTUP_ID"] = id

    env["BLUEMAN_EVENT_TIME"] = str(Gtk.get_current_event_time())

    p = Popen(command, env=env, *args, **kwargs)
    if reap:
        GObject.child_watch_add(p.pid, child_closed)
    return p


def setup_icon_path():
    ic = Gtk.IconTheme.get_default()
    ic.prepend_search_path(ICON_PATH)


def get_icon(name, size=24, fallback="gtk-missing-image"):
    ic = Gtk.IconTheme.get_default()

    try:
        icon = ic.load_icon(name, size, 0)
    except:
        if not fallback:
            raise
        try:
            icon = ic.load_icon(fallback, size, 0)
        except:
            icon = ic.load_icon("gtk-missing-image", size, 0)

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


def create_menuitem(text, image):
    item = Gtk.ImageMenuItem.new_with_mnemonic(text)
    item.set_image(Gtk.Image.new_from_pixbuf(image))

    return item


def check_single_instance(id, unhide_func=None):
    print "%s version %s starting" % (id, VERSION)
    cachedir = os.path.expanduser("~/.cache/")
    if not os.path.exists(cachedir):
        os.mkdir(cachedir)
    lockfile = os.path.join(cachedir, "%s-%s" % (id, os.getuid()))

    def handler(signum, frame):
        if unhide_func:
            f = open(lockfile)
            f.readline()
            try:
                event_time = long(f.readline())
            except:
                event_time = 0
            f.close()
            unhide_func(event_time)


    signal.signal(signal.SIGUSR1, handler)

    if os.path.exists(lockfile):
        f = open(lockfile)
        try:
            pid = int(f.readline())
        except:
            pid = 0

        try:
            event_time = int(f.readline())
        except:
            event_time = 0
        f.close()
        if pid > 0:
            isrunning = os.path.exists("/proc/%s" % pid)
            if isrunning:
                try:
                    f = open("/proc/%s/cmdline" % pid)
                    cmdline = f.readline().replace("\0", " ")
                    f.close()
                except:
                    cmdline = None
            if not isrunning or (isrunning and id not in cmdline):
                print "Stale PID, overwriting"
                os.remove(lockfile)
            else:
                print "There is an instance already running"
                time = os.getenv("BLUEMAN_EVENT_TIME") or 0

                f = file(lockfile, "w")
                f.write("%s\n%s" % (str(pid), str(time)))
                f.close()

                os.kill(pid, signal.SIGUSR1)
                exit()
        else:
            os.remove(lockfile)

    try:
        fd = os.open(lockfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0664)
        os.write(fd, "%s\n%s" % (str(os.getpid()), "0"))
        os.close(fd)
    except OSError:
        print "There is an instance already running"
        exit()

    atexit.register(lambda: os.remove(lockfile))


def have(t):
    out = call(["which", t], stdout=subprocess.PIPE)

    return out != 1


def mask_ip4_address(ip, subnet):
    masked_ip = ""
    for i in range(4):
        masked_ip += chr(ord(ip[i]) & ord(subnet[i]))

    return masked_ip

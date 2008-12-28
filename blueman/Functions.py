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
import gtk
import re
import os
import signal
import atexit
import sys
from subprocess import Popen
import gobject

from blueman.Lib import sn_launcher

GREEN = lambda(x): "\x1b[32;01m"+x+"\x1b[39;49;00m"
BLUE = lambda(x): "\x1b[34;01m"+x+"\x1b[39;49;00m"
BOLD = lambda(x): "\033[1m"+x+"\033[0m"

def dprint(*args):
	s = ""
	for a in args:
		s += (str(a) + " ")
	co = sys._getframe(1).f_code
	
	fname = BOLD(co.co_name)
	
	print "_________"
	print "%s %s" % (fname, "(%s:%d)" % (co.co_filename, co.co_firstlineno))
	print s



def startup_notification(name, desc=None, bin_name=None, icon=None):
	dpy = gtk.gdk.display_get_default()
	screen = dpy.get_default_screen().get_number()
	sn = sn_launcher(dpy, screen)
	sn.set_name(name)
	
	if bin_name:
		sn.set_binary_name(bin_name)
	if icon:
		sn.set_icon_name(icon)
		
	if desc:
		sn.set_description(desc)
	
	sn.initiate("", "", gtk.get_current_event_time())
	
	return sn

def enable_rgba_colormap():
	screen = gtk.gdk.display_get_default().get_default_screen()
	colormap = screen.get_rgba_colormap()
	if colormap == None:
		colormap = screen.get_rgb_colormap()
	gtk.widget_set_default_colormap(colormap)

def spawn(command, system=False, sn=None):

	def child_closed(pid, cond):
		dprint(command, "closed")
		if sn:
			sn.complete()
	if not system:
		if type(command) == list:
			command[0] = os.path.join(BIN_DIR, command[0])
		else:
			command = os.path.join(BIN_DIR, command)
	
	if not sn:
		env=None
	else:
		env = os.environ
		id = sn.get_startup_id()
		env["DESKTOP_STARTUP_ID"] = id
	
	p = Popen(command, env=env)
	gobject.child_watch_add(p.pid, child_closed)

def setup_icon_path():
	ic = gtk.icon_theme_get_default()
	ic.prepend_search_path(ICON_PATH)

def get_icon(name, size=24):
	ic = gtk.icon_theme_get_default()

	try:
		icon = ic.load_icon(name, size, 0) 
	except:
		icon = ic.load_icon("gtk-missing-image", size, 0) 

	return icon
	
def adapter_path_to_name(path):
	return re.search(".*(hci[0-9]*)", path).groups(0)[0]
	


def make_device_icon(target, is_bonded=False, is_trusted=False, is_discovered=False):
	sources = []
	if is_bonded:
		sources.append((get_icon("gtk-dialog-authentication", 16), 0, 0, 200))
		
	if is_trusted:
		sources.append((get_icon("blueman-trust", 16), 0, 32, 200))
	
	if is_discovered:
		sources.append((get_icon("gtk-find", 24), 24, 0, 255))

	return composite_icon(target, sources)


#pixbuf, [(pixbuf, x, y, alpha), (pixbuf, x, y, alpha)]

def composite_icon(target, sources):
	target = target.copy()
	for source in sources:

		source[0].composite(target, source[1], source[2], source[0].get_width(), source[0].get_height(), source[1], source[2], 1, 1, gtk.gdk.INTERP_NEAREST, source[3])
		
	return target
	
def format_bytes(size):
	ret = 0.0
	size = float(size)
	suffix = ""
	if size < 1024:
		ret = size
		suffix = "B"
	elif size > 1024 and size < (1024*1024):
		ret = size / 1024
		suffix = "KB"
	elif size > (1024*1024) and size < (1024*1024*1024):
		ret = size / (1024*1024)
		suffix = "MB"
	else:
		ret = size / (1024*1024*1024)
		suffix="GB"
		
	return (ret, suffix)
	
def create_menuitem(text, image):
	item = gtk.ImageMenuItem()
	item.set_image(gtk.image_new_from_pixbuf(image))
	
	label = gtk.Label()
	label.set_text(text)
	label.set_alignment(0,0.5)

	label.show()
	
	item.add(label)
	
	return item
	
def check_single_instance(id, unhide_func=None):
	def handler(signum, frame):
		if unhide_func:
			unhide_func()


	signal.signal(signal.SIGUSR1, handler)
	
	lockfile = os.path.expanduser("/tmp/%s-%s" % (id, os.getuid()))
	if os.path.exists(lockfile):
		f = open(lockfile)
		pid = f.read()
		f.close()
		if len(pid) > 0:
			isrunning = os.path.exists("/proc/%s" % pid)

			if not isrunning:
				os.remove(lockfile)
			else:
				print "there is an instance already running"
				os.kill(int(pid), signal.SIGUSR1)
				exit()
		else:
			os.remove(lockfile)

	f = file(lockfile, "w")
	f.write(str(os.getpid()))
	f.close()
	atexit.register(lambda:os.remove(lockfile))

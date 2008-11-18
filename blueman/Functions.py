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
from subprocess import call


def spawn(command):
	command = os.path.join(BIN_DIR, command)
	call([command])

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
		sources.append((get_icon("gtk-search", 24), 24, 0, 255))

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

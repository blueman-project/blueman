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

from subprocess import *

from blueman.Constants import *
from blueman.Functions import *

from gi.repository import Gtk


def show_about_dialog(app_name, run=True):
	def uri_open(uri):
		Popen(['xdg-open', uri], stdout=PIPE)

	def email_hook(dialog, email, black_hole):
		uri_open('mailto:'+email)
		
	def url_hook(dialog, url, black_hole):
		uri_open(url)
	
	#FIXME find equivalents with introspection
	#Gtk.about_dialog_set_email_hook(email_hook, None)
	#Gtk.about_dialog_set_url_hook(url_hook, None)
	
	about = Gtk.AboutDialog()
	about.set_name(app_name)
	about.set_version(VERSION)
	about.set_translator_credits(_("translator-credits"))
	about.set_copyright('Copyright \xc2\xa9 2008 Valmantas Palikša\n'\
						'Copyright \xc2\xa9 2008 Tadas Dailyda')
	about.set_comments(_('Blueman is a GTK based Bluetooth manager'))
	about.set_website(WEBSITE)
	about.set_icon(get_icon('blueman'))
	about.set_logo(get_icon('blueman', 48))
	authors = ['Valmantas Palikša <walmis@balticum-tv.lt>',
				'Tadas Dailyda <tadas@dailyda.com>']
	about.set_authors(authors)
	if run:
		about.run()
		about.destroy()
	else:
		return about

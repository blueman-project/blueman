# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from datetime import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def show_about_dialog(app_name, run=True):
    about = Gtk.AboutDialog()
    about.set_name(app_name)
    about.set_version(VERSION)
    about.set_translator_credits(_("translator-credits"))
    about.set_copyright('Copyright © 2008 Valmantas Palikša\n'
                        'Copyright © 2008 Tadas Dailyda\n'
                        'Copyright © 2008 - %s blueman project' % datetime.now().year
                        )
    about.set_comments(_('Blueman is a GTK based Bluetooth manager'))
    about.set_website(WEBSITE)
    about.set_icon(get_icon('blueman'))
    about.set_logo(get_icon('blueman', 48))
    about.set_authors(['Valmantas Palikša <walmis@balticum-tv.lt>',
                       'Tadas Dailyda <tadas@dailyda.com>',
                       '%s/graphs/contributors' % WEBSITE
                       ])
    if run:
        about.run()
        about.destroy()
    else:
        return about

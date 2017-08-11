# coding=utf-8
from datetime import datetime
from blueman.Constants import WEBSITE, VERSION

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def show_about_dialog(app_name, run=True, parent=None):
    about = Gtk.AboutDialog()
    about.set_transient_for(parent)
    about.set_name(app_name)
    about.set_version(VERSION)
    about.set_translator_credits(_("translator-credits"))
    about.set_copyright('Copyright © 2008 Valmantas Palikša\n'
                        'Copyright © 2008 Tadas Dailyda\n'
                        'Copyright © 2008 - %s blueman project' % datetime.now().year
                        )
    about.set_comments(_('Blueman is a GTK+ Bluetooth manager'))
    about.set_website(WEBSITE)
    about.set_website_label(WEBSITE)
    about.set_icon_name('blueman')
    about.set_logo_icon_name('blueman')
    about.set_authors(['Valmantas Palikša <walmis@balticum-tv.lt>',
                       'Tadas Dailyda <tadas@dailyda.com>',
                       '%s/graphs/contributors' % WEBSITE
                       ])
    if run:
        about.run()
        about.destroy()
    else:
        return about

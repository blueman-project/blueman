from datetime import datetime
from gettext import gettext as _
from typing import Optional, overload, TYPE_CHECKING

from blueman.Constants import WEBSITE, VERSION

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

if TYPE_CHECKING:
    from typing_extensions import Literal


class ErrorDialog(Gtk.MessageDialog):
    def __init__(self, markup: str, secondary_markup: Optional[str] = None, excp: Optional[object] = None,
                 icon_name: str = "dialog-error", buttons: Gtk.ButtonsType = Gtk.ButtonsType.CLOSE,
                 title: Optional[str] = None, parent: Optional[Gtk.Container] = None, modal: bool = False,
                 margin_left: int = 0,
                 ) -> None:
        super().__init__(name="ErrorDialog", icon_name=icon_name, buttons=buttons,
                         type=Gtk.MessageType.ERROR, title=title, parent=parent, modal=modal, margin_left=margin_left)

        self.set_markup(markup)

        if secondary_markup:
            self.format_secondary_markup(secondary_markup)

        if excp:
            message_box = self.get_message_area()

            label_expander = Gtk.Label(label="<b>Exception</b>", use_markup=True, visible=True)

            excp_label = Gtk.Label(label=str(excp), selectable=True, visible=True)

            expander = Gtk.Expander(label_widget=label_expander, visible=True)
            expander.add(excp_label)

            message_box.pack_start(expander, False, False, 10)


@overload
def show_about_dialog(app_name: str, run: "Literal[True]" = True, parent: Optional[Gtk.Window] = None) -> None:
    ...


@overload
def show_about_dialog(app_name: str, run: "Literal[False]", parent: Optional[Gtk.Window] = None) -> Gtk.AboutDialog:
    ...


def show_about_dialog(app_name: str, run: bool = True, parent: Optional[Gtk.Window] = None
                      ) -> Optional[Gtk.AboutDialog]:
    about = Gtk.AboutDialog()
    about.set_transient_for(parent)
    about.set_modal(True)
    # on KDE it shows a close button which is unconnected.
    about.connect("response", lambda x, y: about.destroy())
    about.set_name(app_name)
    about.set_version(VERSION)
    about.set_copyright('Copyright © 2008 Valmantas Palikša\n'
                        'Copyright © 2008 Tadas Dailyda\n'
                        f'Copyright © 2008 - {datetime.now().year} blueman project'
                        )
    about.set_comments(_('Blueman is a GTK+ Bluetooth manager'))
    about.set_website(WEBSITE)
    about.set_website_label(WEBSITE)
    about.set_icon_name('blueman')
    about.set_logo_icon_name('blueman')
    about.set_authors(['Valmantas Palikša <walmis@balticum-tv.lt>',
                       'Tadas Dailyda <tadas@dailyda.com>',
                       f'{WEBSITE}/graphs/contributors'
                       ])
    if run:
        about.show()
        return None
    else:
        return about

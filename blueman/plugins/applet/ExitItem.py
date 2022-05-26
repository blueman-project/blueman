from gettext import gettext as _
from blueman.plugins.AppletPlugin import AppletPlugin


class ExitItem(AppletPlugin):
    __depends__ = ["Menu"]
    __description__ = _("Adds an exit menu item to quit the applet")
    __author__ = "Walmis"
    __icon__ = "application-exit-symbolic"

    def on_load(self) -> None:
        self.parent.Plugins.Menu.add(self, 100, text=_("_Exit"), icon_name='application-exit-symbolic',
                                     callback=self.parent.quit)

    def on_unload(self) -> None:
        self.parent.Plugins.Menu.unregister(self)

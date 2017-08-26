from gi.repository import Caja, GObject, Gio


# noinspection PyMissingConstructor
class BluemanSendtoExtension(GObject.GObject, Caja.MenuProvider):
    def __init__(self):
        pass

    def on_menu_activate(self, menu, files):
        send_files = []

        for f in files:
            if f.is_directory():
                print("Skipping directory")
                continue
            elif f.is_gone():
                print("Skipping none existing file")
                continue

            gfile = f.get_location()
            send_files.append("\"%s\"" % gfile.get_path())

        if len(send_files) == 0:
            return
        else:
            cmd = "blueman-sendto %s" % " ".join(send_files)
            flags = Gio.AppInfoCreateFlags.SUPPORTS_STARTUP_NOTIFICATION
            appinfo = Gio.AppInfo.create_from_commandline(cmd, "blueman-sendto", flags)
            print("Running: %s" % cmd)

            launched = appinfo.launch()
            if not launched:
                print("*** Failed to launch program ***")

    def get_file_items(self, window, files):
        if len(files) == 0:
            return

        # We do not support sending whole directories
        for f in files:
            if f.is_directory():
                return

        item = Caja.MenuItem(
            name='BluemanSendto::blueman_send_files',
            label='Send files over bluetooth',
            tip='Sends files over bluetooth with blueman',
            icon='blueman'
        )

        item.connect('activate', self.on_menu_activate, files)

        return [item]

    # stub to avoid potential warning (nautilus throws fit)
    def get_background_items(self, window, file):
        return []

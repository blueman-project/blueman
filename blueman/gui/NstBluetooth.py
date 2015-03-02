from gi.repository import Gtk, GObject, Pango
from blueman.gui.DeviceSelectorWidget import DeviceSelectorWidget
from blueman.Functions import setup_icon_path, spawn
from blueman.main.Config import Config

class NstBluetooth:
    def __init__(self):
        setup_icon_path()

        self.list = DeviceSelectorWidget()
        self.list.show()
        self.list.List.connect("row-activated", self.on_row_activated)
        self.list.List.connect("device-selected", self.on_device_selected)

        self.config = Config("org.blueman.transfer")

        self.device = None

        self.list.set_size_request(240, 280)

        self.button = Gtk.ToggleButton()

        box = Gtk.HBox()
        self.button.add(box)

        self.button_image = Gtk.Image()
        self.button_label = Gtk.Label()
        self.button_label.props.use_markup = True
        self.button_label.props.ellipsize = Pango.EllipsizeMode.END

        if not self.config["last-device"]:
            self.list.List.set_cursor((0,))
        else:
            iter = self.list.List.find_device(self.config["last-device"])
            if iter:
                self.list.List.set_cursor(self.list.List.get_model().get_path(iter))

        box.pack_start(self.button_image, False, True)
        box.pack_start(Gtk.VSeparator, False, True, 4)
        box.pack_start(self.button_label, True, True, 0)

        self.button.show_all()

        self.button.connect("toggled", self.on_button_toggled)

        self.wd = Gtk.Window(Gtk.WindowType.POPUP)

        self.wd.props.decorated = False
        self.wd.props.skip_pager_hint = True
        self.wd.props.skip_taskbar_hint = True
        # self.wd.props.modal = True
        self.wd.connect("button_press_event", self.on_button_press)

        self.wd.add(self.list)
        self.wd.realize()

    def on_row_activated(self, treeview, path, column):
        self.button.props.active = False

    def on_device_selected(self, treeview, device, iter):
        self.config["last-device"] = str(device.Address)

        self.button_label.props.label = "<b>%s</b> (%s)" % (device.Alias, device.Address)
        self.button_label.props.tooltip_markup = self.button_label.props.label
        self.button_image.props.icon_name = device.Icon

        self.device = device


    def on_button_press(self, widget, data=None):

        if data == None or data.window == None:
            return False

        child = data.window.get_user_data()
        if child != widget:
            while child:
                if child == widget:
                    return False
                child = child.parent

        self.button.props.active = False
        return True

    def popup_grab_on_window(self, window, activate_time):
        if Gdk.pointer_grab(window, True, Gdk.EventMask.BUTTON_PRESS_MASK
                | Gdk.EventMask.BUTTON_RELEASE_MASK
                | Gdk.EventMask.POINTER_MOTION_MASK,
                            None, None, activate_time) == 0:
            if Gdk.keyboard_grab(window, True, activate_time) == 0:
                return True
            else:
                Gdk.pointer_ungrab(activate_time)
                return False
        return False


    def on_button_toggled(self, button):

        if button.props.active:
            if not self.popup_grab_on_window(button.window, Gtk.get_current_event_time()):
                print('error during grab')
                return

            x, y = button.window.get_origin()
            x += button.allocation[0]
            y += button.allocation[1] + button.allocation[3]

            self.wd.move(x, y)
            self.list.set_size_request(button.allocation[2], 280)

            self.wd.grab_add()
            self.wd.show()
            self.wd.grab_focus()

            self.popup_grab_on_window(self.wd.window, Gtk.get_current_event_time())

        else:
            self.wd.hide()
            self.wd.grab_remove()


    def get_contacts_widget(self):
        return self.button

    def send_files(self, files):
        spawn(["blueman-sendto", "-d", self.device.Address] + files)

        return True

    def destroy(self):
        pass

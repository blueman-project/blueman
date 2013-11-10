import gtk
from blueman.gui.DeviceSelectorWidget import DeviceSelectorWidget


class DeviceSelectorDialog(gtk.Dialog):
    def __init__(self, title=_("Select Device"), parent=None, discover=True):

        gtk.Dialog.__init__(self, title, parent, 0, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                     gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.set_has_separator(False)
        self.props.resizable = False
        self.props.icon_name = "blueman"
        self.selector = DeviceSelectorWidget()
        self.selector.show()

        #self.selector.destroy()
        #self.selector = None

        align = gtk.Alignment(0.5, 0.5, 1.0, 1.0)
        align.add(self.selector)

        align.set_padding(6, 6, 6, 6)
        align.show()
        self.vbox.pack_start(align)


        #(adapter, device)
        self.selection = None

        self.selector.List.connect("device-selected", self.on_device_selected)
        self.selector.List.connect("adapter-changed", self.on_adapter_changed)
        if discover:
            self.selector.List.DiscoverDevices()

        self.selector.List.connect("row-activated", self.on_row_activated)

    def on_row_activated(self, treeview, path, view_column, *args):
        self.response(gtk.RESPONSE_ACCEPT)

    def on_adapter_changed(self, devlist, adapter):
        self.selection = None

    def on_device_selected(self, devlist, device, iter):
        self.selection = (devlist.Adapter.GetObjectPath(), device)

    def GetSelection(self):
        if self.selection:
            return (self.selection[0], self.selection[1].Copy())
        else:
            return None
		


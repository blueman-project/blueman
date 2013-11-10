import gobject
import gtk
from blueman.Sdp import *
from blueman.Functions import *
from blueman.main.SignalTracker import SignalTracker
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.main.Config import Config
from blueman.main.AppletService import AppletService
from blueman.gui.MessageArea import MessageArea

from blueman.Lib import rfcomm_list


def get_x_icon(icon_name, size):
    ic = get_icon(icon_name, size)
    x = get_icon("blueman-x", size)
    pixbuf = composite_icon(ic, [(x, 0, 0, 255)])

    return pixbuf


class ManagerDeviceMenu(gtk.Menu):
    __ops__ = {}
    __instances__ = []

    def __init__(self, blueman):
        gtk.Menu.__init__(self)
        self.Blueman = blueman
        self.SelectedDevice = None

        self.is_popup = False

        #object, args,
        self.Signals = SignalTracker()
        self.MainSignals = SignalTracker()

        self.MainSignals.Handle("gobject", self.Blueman.List, "device-property-changed",
                                self.on_device_property_changed)

        ManagerDeviceMenu.__instances__.append(self)

        self.Generate()

    def __del__(self):
        dprint("deleting devicemenu")

    #	gobject.GObject.__del__(self)


    def popup(self, *args):
        self.is_popup = True

        self.MainSignals.DisconnectAll()
        self.MainSignals.Handle("gobject", self.Blueman.List, "device-property-changed",
                                self.on_device_property_changed)

        def disconnectall(x):
            self.MainSignals.DisconnectAll()

        self.MainSignals.Handle("gobject", self, "selection-done", disconnectall)

        self.Generate()

        gtk.Menu.popup(self, *args)

    def clear(self):
        self.Signals.DisconnectAll()

        def each(child):
            self.remove(child)
            child.destroy()

        self.foreach(each)

    def set_op(self, device, message):
        ManagerDeviceMenu.__ops__[device.GetObjectPath()] = message
        for inst in ManagerDeviceMenu.__instances__:
            dprint("op: regenerating instance", inst)
            if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
                inst.Generate()


    def get_op(self, device):
        try:
            return ManagerDeviceMenu.__ops__[device.GetObjectPath()]
        except:
            return None

    def unset_op(self, device):
        del ManagerDeviceMenu.__ops__[device.GetObjectPath()]
        for inst in ManagerDeviceMenu.__instances__:
            dprint("op: regenerating instance", inst)
            if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
                inst.Generate()


    def service_property_changed(self, key, value):
        if key == "Connected":
            self.Generate()


    def on_connect(self, item, device, service_id, *args):
        def success(*args2):
            try:
                uuid16 = sdp_get_serial_type(device.Address, args[0])
            except:
                uuid16 = 0

            dprint("success", args2)
            prog.message(_("Success!"))

            if service_id == "serial" and SERIAL_PORT_SVCLASS_ID in uuid16:
                MessageArea.show_message(_("Serial port connected to %s") % args2[0], gtk.STOCK_DIALOG_INFO)
            else:
                MessageArea.close()

            self.unset_op(device)

        def fail(*args):
            prog.message(_("Failed"))

            self.unset_op(device)
            dprint("fail", args)
            MessageArea.show_message(_("Connection Failed: ") + e_(str(args[0])))

        def cancel(prog, *args):
            try:
                svc.Disconnect(*args)
            except:
                pass
            prog.message(_("Cancelled"))
            self.unset_op(device)

        svc = device.Services[service_id]
        self.set_op(device, _("Connecting..."))
        prog = ManagerProgressbar(self.Blueman, False)

        try:
            appl = AppletService()
        except:
            dprint("** Failed to connect to applet")
            fail()
            return
        try:
            appl.SetTimeHint(gtk.get_current_event_time())
        except:
            pass

        if service_id == "network":
            uuid = args[0]
            appl.ServiceProxy(svc.GetInterfaceName(),
                              svc.GetObjectPath(),
                              "Connect",
                              [uuid],
                              reply_handler=success,
                              error_handler=fail, timeout=200)
        #prog.set_cancellable(True)
        #prog.connect("cancelled", cancel)

        elif service_id == "input":
            appl.ServiceProxy(svc.GetInterfaceName(),
                              svc.GetObjectPath(),
                              "Connect", [],
                              reply_handler=success,
                              error_handler=fail, timeout=200)
        #prog.connect("cancelled", cancel)

        elif service_id == "serial":
            uuid = str(args[0])

            appl.RfcommConnect(device.GetObjectPath(),
                               uuid,
                               reply_handler=success,
                               error_handler=fail, timeout=200)

        else:
            appl.ServiceProxy(svc.GetInterfaceName(),
                              svc.GetObjectPath(),
                              "Connect", [],
                              reply_handler=success,
                              error_handler=fail, timeout=200)

        prog.start()

    def on_disconnect(self, item, device, service_id, *args):
        svc = device.Services[service_id]
        if service_id == "serial":
            try:
                appl = AppletService()
            except:
                dprint("** Failed to connect to applet")
            else:
                appl.RfcommDisconnect(device.GetObjectPath(), args[0])
                self.Generate()
        else:
            try:
                appl = AppletService()
            except:
                dprint("** Failed to connect to applet")
                return
            appl.ServiceProxy(svc.GetInterfaceName(),
                              svc.GetObjectPath(), "Disconnect", [])


    def on_device_property_changed(self, List, device, iter, (key, value)):
    #		print "menu:", key, value
        if List.compare(iter, List.selected()):
            if key == "Connected" \
                or key == "Fake" \
                or key == "UUIDs" \
                or key == "Trusted" \
                or key == "Paired":
                self.Generate()

    def Generate(self):
        self.clear()

        appl = AppletService()

        items = []

        if not self.is_popup or self.props.visible:
            device = self.Blueman.List.get(self.Blueman.List.selected(), "device")["device"]
        else:
            (x, y) = self.Blueman.List.get_pointer()
            path = self.Blueman.List.get_path_at_pos(x, y)
            if path != None:
                device = self.Blueman.List.get(path[0][0], "device")["device"]
            else:
                return

        if not device.Valid:
            return
        self.SelectedDevice = device

        op = self.get_op(device)

        if op != None:
            item = create_menuitem(op, get_icon("gtk-connect", 16))
            item.props.sensitive = False
            item.show()
            self.append(item)
            return

        rets = self.Blueman.Plugins.Run("on_request_menu_items", self, device)

        for ret in rets:
            if ret:
                for (item, pos) in ret:
                    items.append((pos, item))

        if device.Fake:
            item = create_menuitem(_("_Add Device"), get_icon("gtk-add", 16))
            self.Signals.Handle("gobject", item, "activate",
                                lambda x: self.Blueman.add_device(device))
            item.show()
            self.append(item)
            item.props.tooltip_text = _("Add this device to known devices list")

            item = create_menuitem(_("_Setup..."), get_icon("gtk-properties", 16))
            self.append(item)
            self.Signals.Handle("gobject", item, "activate",
                                lambda x: self.Blueman.setup(device))
            item.show()
            item.props.tooltip_text = _("Run the setup assistant for this device")

            item = create_menuitem(_("_Pair"), get_icon("gtk-dialog-authentication", 16))
            self.Signals.Handle("gobject", item, "activate",
                                lambda x: self.Blueman.bond(device))
            self.append(item)
            item.show()
            item.props.tooltip_text = _("Pair with the device")

            item = gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            send_item = create_menuitem(_("Send a _File..."), get_icon("gtk-copy", 16))
            self.Signals.Handle("gobject", send_item, "activate",
                                lambda x: self.Blueman.send(device))
            send_item.show()
            self.append(send_item)



        else:
            dprint(device.Alias)

            item = None

            have_disconnectables = False
            have_connectables = False

            if True in map(lambda x: x[0] >= 100 and x[0] < 200, items):
                have_disconnectables = True

            if True in map(lambda x: x[0] < 100, items):
                have_connectables = True

            if True in map(lambda x: x[0] >= 200, items) and (have_connectables or have_disconnectables):
                item = gtk.SeparatorMenuItem()
                item.show()
                items.append((199, item))

            if have_connectables:
                item = gtk.MenuItem()
                label = gtk.Label()
                label.set_markup(_("<b>Connect To:</b>"))
                label.props.xalign = 0.0

                label.show()
                item.add(label)
                item.props.sensitive = False
                item.show()
                items.append((0, item))

            if have_disconnectables:
                item = gtk.MenuItem()
                label = gtk.Label()
                label.set_markup(_("<b>Disconnect:</b>"))
                label.props.xalign = 0.0

                label.show()
                item.add(label)
                item.props.sensitive = False
                item.show()
                items.append((99, item))

            items.sort(lambda a, b: cmp(a[0], b[0]))
            for priority, item in items:
                self.append(item)

            if items != []:
                item = gtk.SeparatorMenuItem()
                item.show()
                self.append(item)

            del items

            send_item = create_menuitem(_("Send a _File..."), get_icon("gtk-copy", 16))
            send_item.props.sensitive = False
            self.append(send_item)
            send_item.show()

            browse_item = create_menuitem(_("_Browse Device..."), get_icon("gtk-open", 16))
            browse_item.props.sensitive = False
            self.append(browse_item)
            browse_item.show()

            uuids = device.UUIDs
            for uuid in uuids:
                uuid16 = uuid128_to_uuid16(uuid)
                if uuid16 == OBEX_OBJPUSH_SVCLASS_ID:
                    self.Signals.Handle("gobject", send_item, "activate", lambda x: self.Blueman.send(device))
                    send_item.props.sensitive = True

                if uuid16 == OBEX_FILETRANS_SVCLASS_ID:
                    self.Signals.Handle("gobject", browse_item, "activate", lambda x: self.Blueman.browse(device))
                    browse_item.props.sensitive = True

            item = gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            item = create_menuitem(_("_Pair"), get_icon("gtk-dialog-authentication", 16))
            item.props.tooltip_text = _("Create pairing with the device")
            self.append(item)
            item.show()
            if not device.Paired:
                self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.bond(device))
            else:
                item.props.sensitive = False

            if not device.Trusted:
                item = create_menuitem(_("_Trust"), get_icon("blueman-trust", 16))
                self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.toggle_trust(device))
                self.append(item)
                item.show()
            else:
                item = create_menuitem(_("_Untrust"), get_icon("blueman-untrust", 16))
                self.append(item)
                self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.toggle_trust(device))
                item.show()
            item.props.tooltip_text = _("Mark/Unmark this device as trusted")

            item = create_menuitem(_("_Setup..."), get_icon("gtk-properties", 16))
            self.append(item)
            self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.setup(device))
            item.show()
            item.props.tooltip_text = _("Run the setup assistant for this device")

            def update_services(item):
                def reply():
                    self.unset_op(device)
                    prog.message(_("Success!"))
                    MessageArea.close()

                def error(*args):
                    self.unset_op(device)
                    prog.message(_("Fail"))
                    MessageArea.show_message(e_(str(args[0])))

                prog = ManagerProgressbar(self.Blueman, False, _("Refreshing"))
                prog.start()
                self.set_op(device, _("Refreshing Services..."))
                appl.RefreshServices(device.GetObjectPath(), reply_handler=reply, error_handler=error)

            item = create_menuitem(_("Refresh Services"), get_icon("gtk-refresh", 16))
            self.append(item)
            self.Signals.Handle(item, "activate", update_services)
            item.show()

            item = gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            item = create_menuitem(_("_Remove..."), get_icon("gtk-delete", 16))
            self.Signals.Handle(item, "activate", lambda x: self.Blueman.remove(device))
            self.append(item)
            item.show()
            item.props.tooltip_text = _("Remove this device from the known devices list")

            item = gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            item = create_menuitem(_("_Disconnect"), get_icon("gtk-disconnect", 16))
            item.props.tooltip_text = _("Forcefully disconnect the device")

            self.append(item)
            item.show()

            def on_disconnect(item):
                def finished(*args):
                    self.unset_op(device)

                self.set_op(device, _("Disconnecting..."))
                self.Blueman.disconnect(device,
                                        reply_handler=finished,
                                        error_handler=finished)

            if device.Connected:
                self.Signals.Handle(item, "activate", on_disconnect)

            else:
                item.props.sensitive = False

		

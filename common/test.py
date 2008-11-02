import gtk



from main_device_list import main_device_list
import blueman.device_class as t

print t.get_minor_class(268)

win = gtk.Window()


a = main_device_list("hci0");
a.DiscoverDevices()

win.add(a)
win.show_all()

gtk.main()

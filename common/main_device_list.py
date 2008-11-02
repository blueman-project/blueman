from device_list import device_list
from blueman.device_class import get_minor_class

import gtk


def get_icon(name, size=24):
	ic = gtk.icon_theme_get_default()

	icon = ic.load_icon(name, size, 0) 

	
	return icon


class main_device_list(device_list):
	
	def __init__(self, adapter=None):
		device_list.__init__(self, adapter)
		
	def row_setup_event(self, iter, device):
		props = device.GetProperties()
		print props
		try:
			icon_name = props["Icon"]
			icon = get_icon(icon_name, 48)
		except:
			icon = get_icon("bluetooth", 48)
			
		try:
			klass = get_minor_class(props["Class"]).capitalize()
		except:
			klass = "Unknown"
			

		name = props["Alias"]
		address = props["Address"]

		caption = "<span size='x-large'>%(0)s</span>\n<span size='small'>%(1)s</span>\n<i>%(2)s</i>" % {"0":name, "1":klass, "2":address}
		self.set(iter, caption=caption, device_pb=icon)




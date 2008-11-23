
import os, sys
#support running uninstalled
_dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if os.path.exists(os.path.join(_dirname,"ChangeLog")):
	sys.path.insert(0, _dirname)
	
from blueman.gui.DeviceSelectorWidget import DeviceSelectorWidget
import gtk

w = gtk.Window()

s = DeviceSelectorWidget()

s.show()
w.add(s)
w.show()
gtk.main()

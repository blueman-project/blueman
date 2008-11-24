
import os, sys
#support running uninstalled
_dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if os.path.exists(os.path.join(_dirname,"ChangeLog")):
	sys.path.insert(0, _dirname)
	
from blueman.gui.DeviceSelectorDialog import DeviceSelectorDialog
import gtk

w = DeviceSelectorDialog()

w.run()
w.destroy()


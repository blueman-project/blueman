bluemandir = $(pythondir)/blueman/plugins/applet

blueman_PYTHON = ExitItem.py ShowConnected.py AuthAgent.py DhcpClient.py NMPANSupport.py DBusService.py DiscvManager.py NetUsage.py Headset.py __init__.py KillSwitch.py Menu.py Networking.py PowerManager.py PPPSupport.py NMDUNSupport.py RecentConns.py SerialManager.py StandardItems.py StatusIcon.py TransferService.py GameControllerWakelock.py

if HAVE_APPINDICATOR
blueman_PYTHON += AppIndicator.py
endif

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


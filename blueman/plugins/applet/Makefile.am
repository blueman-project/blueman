bluemandir = $(pythondir)/blueman/plugins/applet

if USE_APPINDICATOR3
APPINDICATOR3_FILES=AppIndicator.py
endif

blueman_PYTHON = ExitItem.py ShowConnected.py AuthAgent.py DhcpClient.py NMPANSupport.py DBusService.py DiscvManager.py NetUsage.py Headset.py __init__.py KillSwitch.py Menu.py Networking.py PowerManager.py PPPSupport.py NMDUNSupport.py RecentConns.py SerialManager.py StandardItems.py StatusIcon.py TransferService.py $(APPINDICATOR3_FILES)

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


bluemandir = $(pythondir)/blueman/plugins/applet

if ENABLE_HAL
HAL = NMIntegration.py NMMonitor.py
else
HAL = 
endif

blueman_PYTHON = AppIndicator.py ExitItem.py ShowConnected.py AuthAgent.py DhcpClient.py NMPANSupport.py DBusService.py DiscvManager.py NetUsage.py Headset.py __init__.py KillSwitch.py Menu.py Networking.py PowerManager.py PPPSupport.py NMDUNSupport.py PulseAudio.py RecentConns.py SerialManager.py StandardItems.py StatusIcon.py TransferService.py $(HAL)

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


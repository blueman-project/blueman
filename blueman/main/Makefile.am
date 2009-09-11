SUBDIRS = applet

if ENABLE_HAL
HAL = HalManager.py 
else
HAL = 
endif

bluemandir = $(pythondir)/blueman/main
blueman_PYTHON = KillSwitchNG.py AppletService.py PPPConnection.py Config.py DhcpClient.py Device.py FakeDevice.py __init__.py KillSwitch.py Mechanism.py NetConf.py PolicyKitAuth.py SignalTracker.py SpeedCalc.py

blueman_PYTHON += $(HAL)

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

clean-local:
	rm -rf *.pyc *.pyo 


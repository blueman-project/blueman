SUBDIRS =	\
	applet

bluemandir = $(pythondir)/blueman/main
blueman_PYTHON = KillSwitchNG.py AppletService.py PPPConnection.py Config.py Device.py FakeDevice.py HalManager.py __init__.py KillSwitch.py Mechanism.py NetConf.py PolicyKitAuth.py SignalTracker.py SpeedCalc.py

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

clean-local:
	rm -rf *.pyc *.pyo 


SUBDIRS = applet

if ENABLE_HAL
HAL = HalManager.py KillSwitch.py
else
HAL = 
endif

bluemandir = $(pythondir)/blueman/main
blueman_PYTHON = PulseAudioUtils.py BluezConfig.py KillSwitchNG.py AppletService.py PPPConnection.py Config.py DhcpClient.py Device.py FakeDevice.py __init__.py Mechanism.py NetConf.py SignalTracker.py SpeedCalc.py DbusService.py PluginManager.py

blueman_PYTHON += $(HAL)

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

clean-local:
	rm -rf *.pyc *.pyo 


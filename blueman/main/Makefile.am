SUBDIRS =	\
	applet

bluemandir = $(pythondir)/blueman/main
blueman_PYTHON = 		\
	AppletService.py	\
	Config.py			\
	Device.py			\
	FakeDevice.py		\
	HalManager.py		\
	Mechanism.py		\
	NetConf.py			\
	PolicyKitAuth.py	\
	SignalTracker.py	\
	SpeedCalc.py		\
	__init__.py	

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

clean-local:
	rm -rf *.pyc *.pyo 


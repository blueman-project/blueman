SUBDIRS = applet indicators

bluemandir = $(pythondir)/blueman/main

blueman_PYTHON = \
	PPPConnection.py \
	Config.py \
	DhcpClient.py \
	__init__.py \
	NetConf.py \
	SpeedCalc.py \
	DbusService.py \
	PluginManager.py \
	Adapter.py \
	Applet.py \
	Builder.py \
	Manager.py \
	MechanismApplication.py \
	Sendto.py \
	Services.py \
	Tray.py \
	DBusProxies.py \
	NetworkManager.py

if HAVE_PULSEAUDIO
blueman_PYTHON += PulseAudioUtils.py
endif


CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

clean-local:
	rm -rf *.pyc *.pyo 


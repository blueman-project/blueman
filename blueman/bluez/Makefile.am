SUBDIRS = obex

bluemandir = $(pythondir)/blueman/bluez
blueman_PYTHON =				\
	__init__.py					\
	Adapter.py					\
	Agent.py					\
	AgentManager.py				\
	BlueZInterface.py			\
	Device.py					\
	errors.py					\
	Manager.py					\
	PropertiesBlueZInterface.py	\
	ServiceInterface.py			\
	Network.py					\
	NetworkServer.py			\
	Serial.py					\
	AudioSource.py				\
	AudioSink.py				\
	Headset.py

CLEANFILES = \
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)

clean-local:
	rm -rf *.pyc *.pyo

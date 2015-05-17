SUBDIRS = obex

bluemandir = $(pythondir)/blueman/bluez
blueman_PYTHON =				\
	__init__.py					\
	Adapter.py					\
	Agent.py					\
	AgentManager.py				\
	Base.py						\
	Device.py					\
	errors.py					\
	Manager.py					\
	PropertiesBase.py				\
	Network.py					\
	NetworkServer.py			\
	Headset.py

CLEANFILES = \
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)

clean-local:
	rm -rf *.pyc *.pyo

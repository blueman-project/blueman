SUBDIRS = obex

bluemandir = $(pythondir)/blueman/bluez
blueman_PYTHON =				\
	__init__.py					\
	Adapter.py					\
	Agent.py					\
	AgentManager.py				\
	AnyBase.py					\
	Base.py						\
	Device.py					\
	errors.py					\
	Manager.py					\
	Network.py					\
	NetworkServer.py

CLEANFILES = \
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)

clean-local:
	rm -rf *.pyc *.pyo

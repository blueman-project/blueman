SUBDIRS =	\
	services	\
	applet		\
	mechanism	\
	manager


bluemandir = $(pythondir)/blueman/plugins
blueman_PYTHON = 	\
	ServicePlugin.py	\
	AppletPlugin.py		\
	MechanismPlugin.py	\
	ManagerPlugin.py	\
	BasePlugin.py		\
	errors.py		\
	__init__.py

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


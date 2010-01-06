SUBDIRS =	\
	services	\
	applet		\
	config		\
	mechanism


bluemandir = $(pythondir)/blueman/plugins
blueman_PYTHON = 	\
	ServicePlugin.py	\
	AppletPlugin.py		\
	ConfigPlugin.py		\
	MechanismPlugin.py	\
	BasePlugin.py		\
	ConfigurablePlugin.py \
	__init__.py

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


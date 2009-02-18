SUBDIRS =	\
	services	\
	applet		\
	config


bluemandir = $(pythondir)/blueman/plugins
blueman_PYTHON = 	\
	ServicePlugin.py	\
	AppletPlugin.py		\
	ConfigPlugin.py		\
	__init__.py

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


SUBDIRS =	\
	services	\
	applet


bluemandir = $(pythondir)/blueman/plugins
blueman_PYTHON = 	\
	ServicePlugin.py	\
	AppletPlugin.py	\
	__init__.py

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


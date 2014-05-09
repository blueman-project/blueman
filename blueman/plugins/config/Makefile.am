
bluemandir = $(pythondir)/blueman/plugins/config
blueman_PYTHON = 	\
	File.py	\
	__init__.py	\
	Gconf.py \
	GSettings.py

gschemadir = /usr/share/glib-2.0/schemas/
blueman_SCHEMA = \
	apps.blueman.gschema.xml \
	apps.blueman.network.gschema.xml \
	apps.blueman.plugins.netusage.gschema.xml \
	apps.blueman.sdp.gschema.xml \
	apps.blueman.transfer.gschema.xml 
	

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 



bluemandir = $(pythondir)/blueman/plugins/config
blueman_PYTHON = 	\
	File.py	\
	__init__.py	\
	Gconf.py \
	GSettings.py

gschemadir = /usr/share/glib-2.0/schemas/
blueman_SCHEMA = \
	org.blueman.gschema.xml \
	org.blueman.network.gschema.xml \
	org.blueman.plugins.netusage.gschema.xml \
	org.blueman.sdp.gschema.xml \
	org.blueman.transfer.gschema.xml 
	

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


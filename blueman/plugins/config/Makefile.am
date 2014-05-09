
bluemandir = $(pythondir)/blueman/plugins/config
blueman_PYTHON = 	\
	File.py	\
	__init__.py	\
	Gconf.py \
	GSettings.py

gschemadir = /usr/share/glib-2.0/schemas/
blueman_SCHEMA = \
	org.blueman.schema.xml \
	org.blueman.network.schema.xml \
	org.blueman.plugins.netusage.schema.xml \
	org.blueman.transfer.schema.xml


CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 


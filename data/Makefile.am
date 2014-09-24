@INTLTOOL_DESKTOP_RULE@ 
autostartdir = $(sysconfdir)/xdg/autostart
autostart_in_files = blueman.desktop.in
autostart_DATA = $(autostart_in_files:.desktop.in=.desktop)

@INTLTOOL_DESKTOP_RULE@ 
appdir = $(datadir)/applications
app_in_files = blueman-manager.desktop.in
app_DATA = $(app_in_files:.desktop.in=.desktop)

gsettings_SCHEMAS = \
	org.blueman.gschema.xml \
	org.blueman.gsmsettings.gschema.xml \
	org.blueman.netusage.gschema.xml \
	org.blueman.network.gschema.xml \
	org.blueman.pppsupport.gschema.xml \
	org.blueman.sdp.gschema.xml \
	org.blueman.transfer.gschema.xml

# include the appropriate makefile rules for schema handling
@GSETTINGS_RULES@

EXTRA_DIST = 	$(autostart_in_files) \
		$(app_in_files) \
		$(gsettings_SCHEMAS)

SUBDIRS = 		\
	configs		\
	icons		\
	ui		\
	man

CLEANFILES =		\
	blueman-manager.desktop \
	blueman.desktop \
	$(BUILT_SOURCES) \
	*.gschema.valid
	
DISTCLEANFILES = \
	$(CLEANFILES)

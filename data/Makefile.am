autostartdir = $(sysconfdir)/xdg/autostart
autostart_in_files = blueman.desktop.in
autostart_DATA = $(autostart_in_files:.desktop.in=.desktop)

$(autostart_DATA): $(autostart_in_files)
	$(AM_V_GEN) $(MSGFMT) --desktop --template $< -d $(top_srcdir)/po -o $@

appdir = $(datadir)/applications
app_in_files = blueman-manager.desktop.in
app_DATA = $(app_in_files:.desktop.in=.desktop)

$(app_DATA): $(app_in_files)
	$(AM_V_GEN) $(MSGFMT) --desktop --template $< -d $(top_srcdir)/po -o $@

if HAVE_THUNAR
thunardir = $(datadir)/Thunar/sendto
thunar_in_files = thunar-sendto-blueman.desktop.in
thunar_DATA = $(thunar_in_files:.desktop.in=.desktop)

$(thunar_DATA): $(thunar_in_files)
	$(AM_V_GEN) $(MSGFMT) --desktop --template $< -d $(top_srcdir)/po -o $@
endif

if HAVE_SETTINGS
settingsdir = $(datadir)/applications
settings_in_files = blueman-adapters.desktop.in
settings_DATA = $(settings_in_files:.desktop.in=.desktop)

$(settings_DATA): $(settings_in_files)
	$(AM_V_GEN) $(MSGFMT) --desktop --template $< -d $(top_srcdir)/po -o $@
endif

gsettings_SCHEMAS = org.blueman.gschema.xml

# include the appropriate makefile rules for schema handling
@GSETTINGS_RULES@

# Compile the resource file that contains all the UI and icon files
gresourcedir = $(pkgdatadir)
gresource_in_files = blueman.gresource.xml
gresource_DATA = $(gresource_in_files:.gresource.xml=.gresource)

$(gresource_DATA): $(gresource_in_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --sourcedir $(srcdir) --target=$@ $<

EXTRA_DIST =	\
		$(autostart_in_files)	\
		$(app_in_files)		\
		$(thunar_in_files)	\
		$(settings_in_files)	\
		$(gsettings_SCHEMAS)	\
		$(gresource_in_files)	\
		meson.build

SUBDIRS = 		\
	configs		\
	icons		\
	ui		\
	man

CLEANFILES =		\
	thunar-sendto-blueman.desktop	\
	blueman-adapters.desktop	\
	blueman-manager.desktop	\
	blueman.desktop		\
	$(BUILT_SOURCES)	\
	*.gschema.valid	\
	gschemas.compiled	\
	$(gresource_DATA)
	
DISTCLEANFILES = \
	$(CLEANFILES)

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

metainfodir = $(datadir)/metainfo
metainfo_in_files = org.blueman.Blueman.metainfo.xml.in
metainfo_DATA = $(metainfo_in_files:.xml.in=.xml)

$(metainfo_DATA): $(metainfo_in_files)
	$(AM_V_GEN) $(MSGFMT) --xml --template $< -d $(top_srcdir)/po -o $@

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

# GTK icon cache
gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook: update-icon-cache
uninstall-hook: update-icon-cache

update-icon-cache:
	if test -z "$(DESTDIR)"; then \
			echo "Updating Gtk icon cache."; \
			$(gtk_update_icon_cache); \
	else \
			echo "*** Icon cache not updated.  After (un)install, run this:"; \
			echo "***   $(gtk_update_icon_cache)"; \
	fi

EXTRA_DIST = 	blueman.desktop.in.in	\
		blueman-manager.desktop.in.in	\
		org.blueman.Blueman.metainfo.xml.in.in	\
		branding.json		\
		$(thunar_in_files)	\
		$(settings_in_files)	\
		$(gsettings_SCHEMAS)    \
		meson.build

SUBDIRS = 		\
	configs		\
	icons		\
	themes		\
	ui		\
	man

CLEANFILES =		\
	thunar-sendto-blueman.desktop	\
	blueman-adapters.desktop	\
	blueman-manager.desktop	\
	blueman.desktop		\
	org.blueman.Blueman.metainfo.xml	\
	$(BUILT_SOURCES)	\
	*.gschema.valid	\
	gschemas.compiled
	
DISTCLEANFILES = \
	$(CLEANFILES) \
	blueman.desktop.in \
	blueman-manager.desktop.in \
	org.blueman.Blueman.metainfo.xml.in

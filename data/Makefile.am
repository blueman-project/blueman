@INTLTOOL_DESKTOP_RULE@
autostartdir = $(sysconfdir)/xdg/autostart
autostart_in_files = blueman.desktop.in
autostart_DATA = $(autostart_in_files:.desktop.in=.desktop)

@INTLTOOL_DESKTOP_RULE@
appdir = $(datadir)/applications
app_in_files = blueman-manager.desktop.in
app_DATA = $(app_in_files:.desktop.in=.desktop)

thunar_in_files = thunar-sendto-blueman.desktop.in
settings_in_files = blueman-adapters.desktop.in

if HAVE_THUNAR
@INTLTOOL_DESKTOP_RULE@
thunardir = $(datadir)/Thunar/sendto
thunar_DATA = $(thunar_in_files:.desktop.in=.desktop)
endif

if HAVE_SETTINGS
@INTLTOOL_DESKTOP_RULE@
settingsdir = $(datadir)/applications
settings_DATA = $(settings_in_files:.desktop.in=.desktop)
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

EXTRA_DIST = 	$(autostart_in_files)	\
		$(app_in_files)		\
		$(thunar_in_files)	\
		$(settings_in_files)	\
		$(gsettings_SCHEMAS)

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
	*.gschema.valid
	
DISTCLEANFILES = \
	$(CLEANFILES)

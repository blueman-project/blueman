@INTLTOOL_DESKTOP_RULE@ 
autostartdir = $(sysconfdir)/xdg/autostart
autostart_in_files = blueman.desktop.in
autostart_DATA = $(autostart_in_files:.desktop.in=.desktop)

@INTLTOOL_DESKTOP_RULE@ 
appdir = $(datadir)/applications
app_in_files = blueman-manager.desktop.in
app_DATA = $(app_in_files:.desktop.in=.desktop)

@INTLTOOL_DESKTOP_RULE@ 
appdir = $(datadir)/Thunar/sendto
sendto_in_files = thunar-sendto-blueman.desktop.in
sendto_DATA = $(sendto_in_files:.desktop.in=.desktop)


EXTRA_DIST = 	$(autostart_in_files)	\
		$(app_in_files)	\
		$(sendto_in_files)

SUBDIRS = 		\
	configs		\
	icons		\
	ui		\
	man

CLEANFILES =		\
	thunar-sendto-blueman.desktop	\
	blueman-manager.desktop	\
	blueman.desktop		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)

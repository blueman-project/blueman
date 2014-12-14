@INTLTOOL_DESKTOP_RULE@
autostartdir = $(sysconfdir)/xdg/autostart
autostart_in_files = blueman.desktop.in
autostart_DATA = $(autostart_in_files:.desktop.in=.desktop)

@INTLTOOL_DESKTOP_RULE@
appdir = $(datadir)/applications
app_in_files = blueman-manager.desktop.in
app_DATA = $(app_in_files:.desktop.in=.desktop)

thunar_in_files = thunar-sendto-blueman.desktop.in
xfce_in_files = blueman-adapters.desktop.in

if HAVE_THUNAR
@INTLTOOL_DESKTOP_RULE@
thunardir = $(datadir)/Thunar/sendto
thunar_DATA = $(thunar_in_files:.desktop.in=.desktop)
endif

if HAVE_XFCE
@INTLTOOL_DESKTOP_RULE@
xfcedir = $(datadir)/applications
xfce_DATA = $(xfce_in_files:.desktop.in=.desktop)
endif

EXTRA_DIST = 	$(autostart_in_files)	\
		$(app_in_files)		\
		$(thunar_in_files)	\
		$(xfce_in_files)

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
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)

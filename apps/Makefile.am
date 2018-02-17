APPS =				\
	blueman-adapters	\
	blueman-applet		\
	blueman-manager		\
	blueman-services	\
	blueman-sendto		\
	blueman-assistant	\
	blueman-report		\
	blueman-tray

appsdir = $(bindir)
apps_SCRIPTS = $(APPS)

polkitdir = $(libexecdir)
polkit_SCRIPTS = 	\
	blueman-mechanism

helpersdir = $(libexecdir)
helpers_SCRIPTS = blueman-rfcomm-watcher

EXTRA_DIST = $(APPS) $(polkit_SCRIPTS) $(helpers_SCRIPTS)

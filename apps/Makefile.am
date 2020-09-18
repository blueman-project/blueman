APPS =				\
	blueman-adapters	\
	blueman-applet		\
	blueman-manager		\
	blueman-services	\
	blueman-sendto		\
	blueman-tray

appsdir = $(bindir)
apps_SCRIPTS = $(APPS)

polkitdir = $(libexecdir)
polkit_SCRIPTS = 	\
	blueman-mechanism

helpersdir = $(libexecdir)
helpers_SCRIPTS = blueman-rfcomm-watcher

ALL_APPS = $(APPS) $(polkit_SCRIPTS) $(helpers_SCRIPTS)

EXTRA_DIST = $(ALL_APPS) $(addsuffix .in, $(ALL_APPS))

CLEANFILES = $(ALL_APPS)

APPS =					\
	blueman-adapters	\
	blueman-applet		\
	blueman-manager		\
	blueman-services	\
	blueman-sendto		\
	blueman-assistant	\
	blueman-browse		\
	blueman-report
	
appsdir = $(bindir)
apps_SCRIPTS = $(APPS)

polkitdir = $(libexecdir)
polkit_SCRIPTS = 	\
	blueman-mechanism

helpersdir = $(libexecdir)
helpers_SCRIPTS = blueman-rfcomm-watcher
	
EXTRA_DIST = $(APPS) blueman-mechanism blueman-rfcomm-watcher

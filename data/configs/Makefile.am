dbusdir = $(sysconfdir)/dbus-1/system.d
dbus_DATA = org.blueman.Mechanism.conf

dbus_servicesdir = $(datadir)/dbus-1/system-services
dbus_services_DATA = org.blueman.Mechanism.service

dbus_sessdir = $(datadir)/dbus-1/services
dbus_sess_DATA = org.blueman.Applet.service

if SYSTEMD_SYSTEM_UNIT_DIR
systemd_systemdir = $(systemd_system_unit_dir)
systemd_system_DATA = blueman-mechanism.service
endif

if SYSTEMD_USER_UNIT_DIR
systemd_userdir = $(systemd_user_unit_dir)
systemd_user_DATA = blueman-applet.service
endif

if HAVE_POLKIT
@INTLTOOL_POLICY_RULE@ 
policykitactionsdir = $(datadir)/polkit-1/actions
policykitactions_in_files = org.blueman.policy.in
policykitactions_DATA = $(policykitactions_in_files:.policy.in=.policy)

policykitrulesdir = $(datadir)/polkit-1/rules.d
policykitrules_DATA = blueman.rules
endif

EXTRA_DIST = \
	blueman-applet.service.in		\
	blueman-mechanism.service.in		\
	org.blueman.Mechanism.conf		\
	org.blueman.Applet.service.in		\
	org.blueman.Mechanism.service.in	\
	org.blueman.policy.in			\
	blueman.rules

CLEANFILES =		\
	blueman-applet.service		\
	blueman-mechanism.service	\
	org.blueman.Mechanism.service	\
	org.blueman.policy		\
	org.blueman.Applet.service		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)


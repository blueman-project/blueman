dbusdir = $(sysconfdir)/dbus-1/system.d
dbus_DATA = org.blueman.Mechanism.conf

dbus_servicesdir = $(datadir)/dbus-1/system-services
dbus_services_DATA = org.blueman.Mechanism.service

dbus_sessdir = $(datadir)/dbus-1/services
dbus_sess_DATA = blueman-applet.service

if HAVE_POLKIT
@INTLTOOL_POLICY_RULE@ 
policykitactionsdir = $(datadir)/polkit-1/actions
policykitactions_in_files = org.blueman.policy.in
policykitactions_DATA = $(policykitactions_in_files:.policy.in=.policy)

policykitrulesdir = $(datadir)/polkit-1/rules.d
policykitrules_DATA = blueman.rules
endif

EXTRA_DIST = org.blueman.Mechanism.conf		\
	blueman-applet.service.in		\
	org.blueman.Mechanism.service.in	\
	org.blueman.policy.in			\
	blueman.rules

CLEANFILES =		\
	org.blueman.Mechanism.service	\
	org.blueman.policy		\
	blueman-applet.service		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)


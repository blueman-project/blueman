dbusdir = $(sysconfdir)/dbus-1/system.d
dbus_DATA = org.blueman.Mechanism.conf

dbus_servicesdir = $(datadir)/dbus-1/system-services
dbus_services_DATA = org.blueman.Mechanism.service

dbus_sessdir = $(datadir)/dbus-1/services
dbus_sess_DATA = org.blueman.Applet.service

if HAVE_SYSTEMD
systemd_systemdir = $(systemd_system_dir)
systemd_system_DATA = blueman-mechanism.service

systemd_userdir = $(systemd_user_dir)
systemd_user_DATA = blueman-applet.service
endif

if HAVE_POLKIT
@INTLTOOL_POLICY_RULE@ 
policykitdir = $(datadir)/polkit-1/actions
policykit_in_files = org.blueman.policy.in
policykit_DATA = $(policykit_in_files:.policy.in=.policy)
endif

EXTRA_DIST = \
	org.blueman.Mechanism.conf		\
	org.blueman.Applet.service.in		\
	org.blueman.Mechanism.service.in	\
	org.blueman.policy.in

if HAVE_SYSTEMD
EXTRA_DIST += \
	blueman-applet.service.in		\
	blueman-mechanism.service.in
endif

CLEANFILES = \
	org.blueman.Mechanism.service	\
	org.blueman.policy		\
	org.blueman.Applet.service		\
	$(BUILT_SOURCES)

if HAVE_SYSTEMD
CLEANFILES += \
	blueman-applet.service		\
	blueman-mechanism.service
endif

DISTCLEANFILES = \
	$(CLEANFILES)


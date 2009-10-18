dbusdir = $(sysconfdir)/dbus-1/system.d
dbus_DATA = org.blueman.Mechanism.conf

dbus_servicesdir = $(datadir)/dbus-1/system-services
dbus_services_DATA = org.blueman.Mechanism.service

dbus_sessdir = $(datadir)/dbus-1/services
dbus_sess_DATA = blueman-applet.service

if ENABLE_HAL	
hal_fdidir = $(datadir)/hal/fdi/information/20thirdparty
hal_fdi_DATA = 11-blueman-bnep.fdi
endif

@INTLTOOL_POLICY_RULE@ 
policykitdir = $(datadir)/polkit-1/actions
policykit_in_files = org.blueman.policy.in
policykit_DATA = $(policykit_in_files:.policy.in=.policy)


EXTRA_DIST = org.blueman.Mechanism.conf		\
	blueman-applet.service.in		\
	org.blueman.Mechanism.service.in	\
	org.blueman.policy.in			\
	11-blueman-bnep.fdi

CLEANFILES =		\
	org.blueman.Mechanism.service	\
	org.blueman.policy		\
	blueman-applet.service		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)


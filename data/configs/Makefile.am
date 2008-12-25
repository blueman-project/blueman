dbusdir = $(sysconfdir)/dbus-1/system.d
dbus_DATA = org.blueman.Mechanism.conf

dbus_servicesdir = $(datadir)/dbus-1/system-services
dbus_services_in_files = org.blueman.Mechanism.service.in
dbus_services_DATA = $(dbus_services_in_files:.service.in=.service)

$(dbus_services_DATA): $(dbus_services_in_files) Makefile
	@sed -e "s|\@pkglibdir\@|$(pkglibdir)|" $< > $@
	
dbus_sessdir = $(datadir)/dbus-1/services
dbus_sess_in_files = blueman-applet.service.in
dbus_sess_DATA = $(dbus_sess_in_files:.service.in=.service)

$(dbus_sess_DATA): $(dbus_sess_in_files) Makefile
	@sed -e "s|\@BINDIR\@|$(BINDIR)|" $< > $@

@INTLTOOL_POLICY_RULE@ 
policykitdir = $(datadir)/PolicyKit/policy
policykit_in_files = org.blueman.policy.in
policykit_DATA = $(policykit_in_files:.policy.in=.policy)


EXTRA_DIST =					\
	org.blueman.Mechanism.conf		\
	org.blueman.Mechanism.service.in	\
	$(dbus_sess_in_files)		\
	$(policykit_in_files)

CLEANFILES =		\
	org.blueman.Mechanism.service	\
	org.blueman.policy		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES)


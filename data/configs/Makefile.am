dbusdir = $(sysconfdir)/dbus-1/system.d
dbus_DATA = org.blueman.Mechanism.conf

dbus_servicesdir = $(datadir)/dbus-1/system-services
dbus_services_in_files = org.blueman.Mechanism.service.in
dbus_services_DATA = $(dbus_services_in_files:.service.in=.service)

$(dbus_services_DATA): $(dbus_services_in_files) Makefile
	@sed -e "s|\@pkglibdir\@|$(pkglibdir)|" $< > $@

policykitdir = $(datadir)/PolicyKit/policy
policykit_DATA = org.blueman.policy


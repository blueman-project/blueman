install:
	mkdir -p /usr/lib/blueman
	ln -f -s $(CURDIR)/org.blueman.Mechanism.conf /etc/dbus-1/system.d
	ln -f -s $(CURDIR)/org.blueman.Mechanism.service /usr/share/dbus-1/system-services
	ln -f -s $(CURDIR)/org.blueman.policy /usr/share/PolicyKit/policy
	ln -f -s $(CURDIR)/../../apps/blueman-mechanism /usr/lib/blueman

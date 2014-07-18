icons = hicolor_apps_16x16_blueman.png \
	hicolor_apps_22x22_blueman.png \
	hicolor_apps_24x24_blueman.png \
	hicolor_apps_32x32_blueman.png \
	hicolor_apps_48x48_blueman.png \
	hicolor_apps_64x64_blueman.png \
	hicolor_apps_72x72_blueman.png \
	hicolor_apps_96x96_blueman.png \
	hicolor_apps_128x128_blueman.png \
	hicolor_apps_192x192_blueman.png \
	hicolor_apps_256x256_blueman.png \
	hicolor_apps_scalable_blueman.svg

EXTRA_DIST = $(icons)

MAINTAINERCLEANFILES = Makefile.in

install-data-local:
	for i in $(icons); do \
		THEME=`echo $$i | cut -d_ -f1`; \
		CONTEXT=`echo $$i | cut -d_ -f2`; \
		SIZE=`echo $$i | cut -d_ -f3`; \
		FILE=`echo $$i | cut -d_ -f4`; \
		mkdir -p $(DESTDIR)$(datadir)/icons/$$THEME/$$SIZE/$$CONTEXT; \
		$(INSTALL_DATA) $(srcdir)/$$i $(DESTDIR)$(datadir)/icons/$$THEME/$$SIZE/$$CONTEXT/$$FILE; \
	done

uninstall-local:
	for i in $(icons); do \
		THEME=`echo $$i | cut -d_ -f1`; \
		CONTEXT=`echo $$i | cut -d_ -f2`; \
		SIZE=`echo $$i | cut -d_ -f3`; \
		FILE=`echo $$i | cut -d_ -f4`; \
		rm -f $(DESTDIR)$(datadir)/icons/$$THEME/$$SIZE/$$CONTEXT/$$FILE; \
	done


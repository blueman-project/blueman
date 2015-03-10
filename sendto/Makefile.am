#AM_CFLAGS = 

if HAVE_NST
nst_plugindir = $(libdir)/nautilus-sendto/plugins

nst_plugin_LTLIBRARIES = libnstblueman.la

libnstblueman_la_SOURCES = nautilus-bluetooth-sendto.c
libnstblueman_la_LDFLAGS = -module -avoid-version
libnstblueman_la_LIBADD = $(BLUEZ_LIBS) $(PYGOBJECT_LIBS) $(PYTHON_LIBS)
libnstblueman_la_CFLAGS = $(PYTHON_CFLAGS) $(BLUEZ_CFLAGS) $(PYGOBJECT_CFLAGS)

endif

if HAVE_CST
caja-bluetooth-sendto.c: nautilus-bluetooth-sendto.c
	$(SED) -e "s|nautilus|nautilus|" $< >$@

cst_plugindir = $(libdir)/caja-sendto/plugins

cst_plugin_LTLIBRARIES = libcstblueman.la

libcstblueman_la_SOURCES = caja-bluetooth-sendto.c
libcstblueman_la_LIBADD = $(CAJA_SENDTO_LIBS) $(PYGOBJECT_LIBS) $(PYTHON_LIBS)
libcstblueman_la_CFLAGS = $(CAJA_SENDTO_CFLAGS) $(PYTHON_CFLAGS) $(PYGOBJECT_CFLAGS)

endif
EXTRA_DIST = nautilus-bluetooth-sendto.c nautilus-sendto-plugin.h

CLEANFILES = caja-bluetooth-sendto.c

MAINTAINERCLEANFILES = Makefile.in 

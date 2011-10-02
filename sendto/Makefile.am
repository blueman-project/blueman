#AM_CFLAGS = 


if HAVE_NST
plugindir = $(libdir)/nautilus-sendto/plugins

plugin_LTLIBRARIES = libnstblueman.la

libnstblueman_la_SOURCES = nautilus-bluetooth-sendto.c
libnstblueman_la_LDFLAGS = -module -avoid-version
libnstblueman_la_LIBADD = $(BLUEZ_LIBS) @PYTHON_LIBS@
libnstblueman_la_CFLAGS = @PYTHON_INCLUDES@ $(BLUEZ_CFLAGS)

endif

EXTRA_DIST = nautilus-bluetooth-sendto.c nautilus-sendto-plugin.h

MAINTAINERCLEANFILES = Makefile.in 

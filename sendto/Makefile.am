#AM_CFLAGS = 


if HAVE_CST
plugindir = $(libdir)/caja-sendto/plugins

plugin_LTLIBRARIES = libnstblueman.la

libnstblueman_la_SOURCES = caja-bluetooth-sendto.c
libnstblueman_la_LDFLAGS = -module -avoid-version
libnstblueman_la_LIBADD = $(CAJA_SENDTO_LIBS) $(PYGOBJECT_LIBS) $(PYTHON_LIBS)
libnstblueman_la_CFLAGS = $(CAJA_SENDTO_CFLAGS) $(PYTHON_CFLAGS) $(PYGOBJECT_CFLAGS)

endif

EXTRA_DIST = caja-bluetooth-sendto.c

MAINTAINERCLEANFILES = Makefile.in 

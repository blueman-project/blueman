BUILT_SOURCES = _blueman.c

bluemanlibdir = $(pyexecdir)
bluemanlib_LTLIBRARIES = _blueman.la
_blueman_la_CFLAGS = $(BLUEZ_CFLAGS) $(PYGOBJECT_CFLAGS) $(PYTHON_CFLAGS) \
                     -DSN_API_NOT_YET_FROZEN
_blueman_la_LDFLAGS = -module -avoid-version -fPIC
_blueman_la_LIBADD = $(BLUEZ_LIBS) $(PYGOBJECT_LIBS) $(PYTHON_LIBS)
nodist__blueman_la_SOURCES = _blueman.c
_blueman_la_SOURCES = \
	libblueman.c	\
	libblueman.h

_blueman.c: _blueman.pyx
	$(CYTHONEXEC) -o $@ $<
	
EXTRA_DIST = _blueman.pyx meson.build
CLEANFILES = _blueman.c

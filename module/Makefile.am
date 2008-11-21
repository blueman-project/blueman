BUILT_SOURCES = Lib.c

bluemanlibdir = $(pyexecdir)/blueman
bluemanlib_LTLIBRARIES = Lib.la
Lib_la_CFLAGS = $(BLUEZ_CFLAGS) @PYTHON_INCLUDES@
Lib_la_LDFLAGS = -module -avoid-version -fPIC
Lib_la_LIBADD = $(BLUEZ_LIBS)
Lib_la_SOURCES = \
	Lib.c			\
	libblueman.c	\
	libblueman.h

Lib.c: Lib.pyx
	$(PYREXC) -o $@ $<
	
EXTRA_DIST = Lib.pyx

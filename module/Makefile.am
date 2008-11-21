BUILT_SOURCES = Lib.c

pyexec_LTLIBRARIES = libblueman.la
libblueman_la_CFLAGS = $(BLUEZ_CFLAGS) @PYTHON_INCLUDES@
libblueman_la_LIBADD = $(BLUEZ_LIBS)
libblueman_la_SOURCES = \
	Lib.c			\
	libblueman.c	\
	libblueman.h

Lib.c: Lib.pyx
	$(PYREXC) -o $@ $<
	
EXTRA_DIST = Lib.pyx

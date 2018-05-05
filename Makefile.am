SUBDIRS = 		\
	apps		\
	blueman		\
	data		\
	module		\
	po		\
	sendto

DIST_DOCS =			\
	CHANGELOG.md		\
	COPYING			\
	FAQ			\
	README.md

EXTRA_DIST = 			\
	${DIST_DOCS}		\
	intltool-extract.in	\
	intltool-update.in	\
	intltool-merge.in

DISTCLEANFILES = 		\
	intltool-extract 	\
	intltool-update		\
	intltool-merge

MAINTAINERCLEANFILES = 	\
	Makefile.in			\
	aclocal.m4			\
	configure			\
	config.h.in			\
	depcomp				\
	missing				\
	install-sh			\
	intltool-extract.in	\
	intltool-update.in	\
	intltool-merge.in

doc_DATA = ${DIST_DOCS}

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

# distcheck fails trying to install to the live filesystem
AM_DISTCHECK_CONFIGURE_FLAGS = \
    --with-systemdsystemunitdir='$$(prefix)/lib/systemd/system' \
    --with-systemduserunitdir='$$(prefix)/lib/systemd/user'

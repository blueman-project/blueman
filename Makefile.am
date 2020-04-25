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
	meson.build		\
	po/meson.build

MAINTAINERCLEANFILES = 	\
	Makefile.in			\
	aclocal.m4			\
	configure			\
	config.h.in			\
	config.rpath			\
	depcomp				\
	missing				\
	install-sh			\
	ABOUT-NLS			\
	config.rpath			\
	po/Makefile.in.in		\
	po/Makefile.in			\
	po/Makefile			\
	po/Makevars.template		\
	po/quot.sed			\
	po/remove-potcdate.sin		\
	po/Rules-quot			\
	po/blueman.pot			\
	po/boldquot.sed			\
	po/*.header			\
	po/stamp-po			\
	po/insert-header.sin		\
	$NULL

doc_DATA = ${DIST_DOCS}

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

# distcheck fails trying to install to the live filesystem
AM_DISTCHECK_CONFIGURE_FLAGS = \
    --with-systemdsystemunitdir='$$(prefix)/lib/systemd/system' \
    --with-systemduserunitdir='$$(prefix)/lib/systemd/user'

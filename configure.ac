AC_PREREQ(2.61)

AC_INIT(blueman, 0.99)
AC_CONFIG_HEADERS(config.h)
AM_INIT_AUTOMAKE(AC_PACKAGE_NAME, AC_PACKAGE_VERSION)

AM_MAINTAINER_MODE
AC_PROG_CC
AC_PROG_LIBTOOL
PKG_PROG_PKG_CONFIG

GETTEXT_PACKAGE="blueman"
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

AM_PATH_PYTHON(2.5)
AM_CHECK_PYTHON_HEADERS(,[AC_MSG_ERROR(Could not find Python headers)])

AC_ARG_VAR([PYREXC], [Pyrex compiler])
if test "x$PYREXC" = "x"; then
   AC_PATH_PROG([PYREXC],[pyrexc])
fi
AC_SUBST([PYREXC])
AC_MSG_CHECKING([for pyrexc executable])
AC_MSG_RESULT([${PYREXC}])
if test "x$PYREXC" = "x"; then
   AC_MSG_ERROR([Fatal: pyrexc not found.

Get Pyrex from
  * your system's packages (recommended)
  * upstream at http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/
])
fi


#--------------------------------------------------------------------
# Default paths for installation
#--------------------------------------------------------------------

if test "$prefix" = ""; then
  prefix=/usr/local
fi
if test "$prefix" = "NONE"; then
  prefix=/usr/local
fi
if test "$exec_prefix" = ""; then
  exec_prefix=${prefix}
fi
if test "$exec_prefix" = "NONE"; then
  exec_prefix=${prefix}
fi
if test "$exec_prefix" = '${prefix}'; then
  exec_prefix=${prefix}
fi
if test "$includedir" = ""; then
  includedir=${prefix}/include
fi
if test "$includedir" = "NONE"; then
  includedir=${prefix}/include
fi
if test "$includedir" = '${prefix}/include'; then
  includedir=${prefix}/include
fi
if test "$libdir" = ""; then
  libdir=${exec_prefix}/lib
fi
if test "$libdir" = "NONE"; then
  libdir=${exec_prefix}/lib
fi
if test "$libdir" = '${exec_prefix}/lib'; then
  libdir=${exec_prefix}/lib
fi
if test "$bindir" = ""; then
  bindir=${exec_prefix}/bin
fi
if test "$bindir" = "NONE"; then
  bindir=${exec_prefix}/bin
fi
if test "$bindir" = '${exec_prefix}/bin'; then
  bindir=${exec_prefix}/bin
fi
if test "$datadir" = ""; then
  datadir=${prefix}/share
fi
if test "$datadir" = "NONE"; then
  datadir=${prefix}/share
fi
if test "$datadir" = '${prefix}/share'; then
  datadir=${prefix}/share
fi
if test "$mandir" = ""; then
  mandir=${prefix}/man
fi
if test "$mandir" = "NONE"; then
  mandir=${prefix}/man
fi
if test "$sysconfdir" = "NONE"; then
  sysconfdir=/etc
fi
if test "$sysconfdir" = ""; then
  sysconfdir=/etc
fi
if test "$mandir" = '${prefix}/man'; then
  mandir=${prefix}/man
fi
if test "$libexecdir" = ""; then
  libexecdir=${exec_prefix}/libexec
fi
if test "$libexecdir" = "NONE"; then
  libexecdir=${exec_prefix}/libexec
fi
if test "$libexecdir" = '${exec_prefix}/libexec'; then
  libexecdir=${exec_prefix}/libexec
fi



dnl ----------------------------------
dnl - Various paths and other defines
dnl ----------------------------------
AC_SUBST(VERSION)
AC_SUBST(PACKAGE)

AS_AC_EXPAND(SYSCONFDIR, $sysconfdir)
AC_SUBST(SYSCONFDIR)
AS_AC_EXPAND(BINDIR, $bindir)
AC_SUBST(BINDIR)
AS_AC_EXPAND(DATADIR, $datarootdir)
AC_SUBST(DATADIR)
AS_AC_EXPAND(PYTHONDIR, $pythondir)
AC_SUBST(PYTHONDIR)

AS_AC_EXPAND(PKGLIBDIR, $libdir/blueman)
AC_SUBST(PKGLIBDIR)

AS_AC_EXPAND(LIBEXECDIR, $libexecdir)
AC_SUBST(LIBEXECDIR)

dnl AS_AC_EXPAND([PREFIX], $prefix)
AC_SUBST(prefix)



pkgdatadir="${DATADIR}/${PACKAGE}"
AC_SUBST(pkgdatadir)

AS_AC_EXPAND(LOCALEDIR, $datarootdir/locale)
AC_SUBST(LOCALEDIR)

dnl ---------------------------------
dnl dhcp config file location
dnl ---------------------------------

dhconfig='/etc/dhcp3/dhcpd.conf'
AC_ARG_WITH(dhcp_config,
[  --with-dhcp-config=PATH           set dhcp3 server configuration path],
dhconfig="$with_dhcp_config"
)
AC_SUBST(dhconfig)

dnl ---------------------------------

AM_CHECK_PYMOD(gtk,,,[AC_MSG_ERROR(Could not find Python module gtk >= 2.12)])

AC_MSG_CHECKING([if pygtk is >= 2.12])
if AC_RUN_LOG([$PYTHON -c '
import gtk, sys
(maj, mid, min) = gtk.pygtk_version
if maj != 2 or mid < 12:
	sys.exit(1)

']); then
  AC_MSG_RESULT([yes])
else
  AC_MSG_RESULT([no])
  AC_MSG_ERROR([pygtk must be version 2.12 or higher])
fi


AM_CHECK_PYMOD(pynotify,,,[AC_MSG_ERROR(Could not find Python module pynotify)])
AM_CHECK_PYMOD(dbus,,,[AC_MSG_ERROR(Could not find Python module dbus)])
AM_CHECK_PYMOD(gconf,,,[AC_MSG_ERROR(Could not find Python module gconf)])
AM_CHECK_PYMOD(gobject,,,[AC_MSG_ERROR(Could not find Python module gobject)])





PKG_CHECK_MODULES(BLUEZ,
		bluez	>= 4.21
		libstartup-notification-1.0 >= 0.9
		gdk-2.0 >= 2.12
		pygobject-2.0 >= 2.12
		gobject-2.0 >= 2.12
)
AC_SUBST(BLUEZ_CFLAGS)
AC_SUBST(BLUEZ_LIBS)


AC_OUTPUT([
Makefile
apps/Makefile
blueman/Makefile
blueman/Constants.py
blueman/bluez/Makefile
blueman/gui/Makefile
blueman/gui/applet/Makefile
blueman/gui/manager/Makefile
blueman/plugins/Makefile
blueman/plugins/services/Makefile
blueman/plugins/applet/Makefile
blueman/main/Makefile
blueman/main/applet/Makefile
blueman/ods/Makefile
data/Makefile
data/configs/Makefile
data/icons/Makefile
data/icons/hicolor/Makefile
data/icons/hicolor/16x16/Makefile
data/icons/hicolor/16x16/actions/Makefile
data/icons/hicolor/16x16/devices/Makefile
data/icons/hicolor/16x16/status/Makefile
data/icons/hicolor/32x32/Makefile
data/icons/hicolor/32x32/actions/Makefile
data/icons/hicolor/48x48/Makefile
data/icons/hicolor/48x48/actions/Makefile
data/icons/hicolor/48x48/devices/Makefile
data/icons/hicolor/48x48/status/Makefile
data/icons/hicolor/scalable/Makefile
data/icons/hicolor/scalable/devices/Makefile
data/icons/main_icon/Makefile
data/ui/Makefile
data/man/Makefile
data/configs/blueman-applet.service
data/configs/org.blueman.Mechanism.service
module/Makefile
po/Makefile.in
])


echo
echo $PACKAGE $VERSION
echo

echo Prefix : $prefix
echo

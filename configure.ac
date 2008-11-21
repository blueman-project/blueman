AC_PREREQ(2.61)

AC_INIT(blueman, 0.99)
AC_CONFIG_HEADERS(config.h)
AM_INIT_AUTOMAKE(AC_PACKAGE_NAME, AC_PACKAGE_VERSION)

AM_MAINTAINER_MODE
AC_PROG_CC
PKG_PROG_PKG_CONFIG

GETTEXT_PACKAGE="blueman"
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

AM_PATH_PYTHON(2.4)
AM_CHECK_PYTHON_HEADERS(,[AC_MSG_ERROR(Could not find Python headers)])

dnl ----------------------------------
dnl - Various paths and other defines
dnl ----------------------------------
AC_SUBST(VERSION)
AC_SUBST(PACKAGE)

AS_AC_EXPAND(SYSCONFDIR, $sysconfdir)
AC_SUBST(SYSCONFDIR)
AS_AC_EXPAND(BINDIR, $bindir)
AS_AC_EXPAND(DATADIR, $datarootdir)
AC_SUBST(DATADIR)
AS_AC_EXPAND(PYTHONDIR, $pythondir)
AC_SUBST(PYTHONDIR)

dnl ----------------------------------
dnl - Dependencies - TODO: split into sections
dnl ----------------------------------
PKG_CHECK_MODULES(BLUEMAN,
		bluez			>= 4.0
		gtk+-2.0		>= 2.12
		gconf-2.0		>= 2.20
		pygtk-2.0		>= 2.12
		pygobject-2.0	>= 2.12
		dbus-python		>= 0.80.2
		notify-python	>= 0.1.1
)
AC_SUBST(BLUEMAN_CFLAGS)
AC_SUBST(BLUEMAN_LIBS)

dnl - TODO: add checks for python modules

AC_OUTPUT([
Makefile
apps/Makefile
blueman/Makefile
blueman/Constants.py
blueman/bluez/Makefile
blueman/gui/Makefile
blueman/gui/applet/Makefile
blueman/gui/manager/Makefile
blueman/main/Makefile
blueman/main/applet/Makefile
blueman/main/manager/Makefile
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
po/Makefile.in
])


echo
echo $PACKAGE $VERSION
echo

echo Prefix : $prefix
echo

AC_PREREQ(2.61)

AC_INIT(blueman, 0.1svn)
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
dnl - Dependencies
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


AC_OUTPUT([
Makefile
])


echo
echo $PACKAGE $VERSION
echo

echo Prefix : $prefix
echo

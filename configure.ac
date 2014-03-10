AC_PREREQ(2.69)

AC_INIT(blueman, 1.23)
AC_CONFIG_HEADERS(config.h)
AM_INIT_AUTOMAKE(foreign)

AM_MAINTAINER_MODE
AC_PROG_CC
AC_PROG_LIBTOOL
PKG_PROG_PKG_CONFIG

GETTEXT_PACKAGE="blueman"
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

AM_PATH_PYTHON(2.6)
AM_CHECK_PYTHON_HEADERS(,[AC_MSG_ERROR(Could not find Python headers)])

AC_ENABLE_SHARED(yes)
AC_ENABLE_STATIC(no)

PYTHON_LIBS=`python-config --libs`
AC_SUBST(PYTHON_LIBS)

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


if test "$sysconfdir" = "\${prefix}/etc" \
    && { test "$prefix" = "NONE" || test "$prefix" = "/usr" \
      || test "$prefix" = "/usr/" ; } ; then
    if test "$( (uname -s) )" = "Linux" ; then
      sysconfdir=/etc
    fi
    (
    prefix=$ac_default_prefix
    sysconfdir=`eval echo "$sysconfdir"`
    AC_MSG_NOTICE([configuration directory is "$sysconfdir".])
    AC_MSG_NOTICE([use --sysconfdir to override.])
    )
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
deps_check=1
AC_ARG_WITH(no_runtime_deps_check,
[  --with-no-runtime-deps-check disable runtime dependency check (for package maintainers)],
deps_check=0
)

polkit_val="yes"
AC_ARG_ENABLE(polkit,
[  --enable-polkit=[yes/no] Enable policykit support],,enable_polkit=yes)
if test "x$enable_polkit" = "xyes"; then
        polkit_val="yes"
else
        polkit_val="no"
fi
AC_SUBST(polkit_val)

hal_en="no"
AC_ARG_ENABLE(hal,
[  --enable-hal=[yes/no] Enable/disable Hal support],,enable_hal=no)
if test "x$enable_hal" = "xyes"; then
        hal_en="yes"
else
        hal_en="no"
fi
AC_SUBST(hal_en)
AM_CONDITIONAL(ENABLE_HAL, test "x$hal_en" = "xyes")

have_nst=yes
AC_ARG_ENABLE(sendto,
[  --enable-sendto=[yes/no] Enable nautilus-sendto plugin build],,have_nst=yes)

AM_CONDITIONAL(HAVE_NST, test "x$have_nst" = "xyes")

dnl ----------------------------

if test $deps_check = 1; then

PKG_CHECK_MODULES(PYGTK, pygtk-2.0 >= 2.12.0)
PKG_CHECK_MODULES(PYNOTIFY, notify-python)
AM_CHECK_PYMOD(dbus,,,[AC_MSG_ERROR(Could not find Python module dbus)])
AM_CHECK_PYMOD(gobject,,,[AC_MSG_ERROR(Could not find Python module gobject)])

fi

PKG_CHECK_MODULES(BLUEZ,
		bluez	>= 4.61
		libstartup-notification-1.0 >= 0.9
		gtk+-2.0 >= 2.12
		pygobject-2.0 >= 2.12
		gobject-2.0 >= 2.12
		glib-2.0 >= 2.32
		gthread-2.0 >= 2.32
)
AC_SUBST(BLUEZ_CFLAGS)
AC_SUBST(BLUEZ_LIBS)


AC_OUTPUT([
Makefile
apps/Makefile
sendto/Makefile
blueman/Makefile
blueman/Constants.py
blueman/bluez/Makefile
blueman/gui/Makefile
blueman/gui/applet/Makefile
blueman/gui/manager/Makefile
blueman/plugins/Makefile
blueman/plugins/services/Makefile
blueman/plugins/applet/Makefile
blueman/plugins/mechanism/Makefile
blueman/plugins/manager/Makefile
blueman/plugins/config/Makefile
blueman/main/Makefile
blueman/main/applet/Makefile
blueman/ods/Makefile
blueman/iniparse/Makefile
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
data/icons/hicolor/scalable/actions/Makefile
data/icons/hicolor/scalable/status/Makefile
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
echo sysconfig dir : $sysconfdir
echo "HAL support enabled (deprecated): $hal_en"
echo Policykit-1 Enabled: $polkit_val
echo Nautilus sendto plugin enabled: $have_nst
echo Dhcpd 3 configuration file: $dhconfig
echo

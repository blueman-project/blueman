AC_PREREQ(2.69)

AC_INIT(blueman, 1.99.alpha1)
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

AM_PATH_PYTHON([2.7])
if test "${PYTHON_VERSION}" \< "3.0"; then
    PKG_CHECK_MODULES([PYTHON], [python-${PYTHON_VERSION}])
    AC_SUBST(PYTHON_LIBS)
    AC_SUBST(PYTHON_CFLAGS)
else
    AC_MSG_ERROR([Blueman does not support python 3])
fi

AC_ENABLE_SHARED(yes)
AC_ENABLE_STATIC(no)

AC_ARG_VAR([CYTHONEXEC], [Cython compiler])
if test "x$CYTHONEXEC" = "x"; then
   AC_PATH_PROG([CYTHONEXEC],[cython])
fi
AC_SUBST([CYTHONEXEC])
AC_MSG_CHECKING([for cython executable])
AC_MSG_RESULT([${CYTHONEXEC}])
if test "x$CYTHONEXEC" = "x"; then
   AC_MSG_ERROR(["Fatal: cython not found.

Get Cython from
  * your system's packages (recommended)
  * upstream at http://www.cython.org/
"])
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

icondir="${DATADIR}/icons"
AC_SUBST(icondir)

pixmapsdir="${DATADIR}/pixmaps"
AC_SUBST(pixmapsdir)

AS_AC_EXPAND(LOCALEDIR, $datarootdir/locale)
AC_SUBST(LOCALEDIR)

AS_AC_EXPAND(DOCDIR, $docdir)
AC_SUBST(DOCDIR)

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

AC_ARG_ENABLE(sendto,
[  --enable-sendto=[yes/no] Enable nautilus-sendto plugin build],have_nst=$enableval,have_nst=yes)

AM_CONDITIONAL(HAVE_NST, test "x$have_nst" = "xyes")

dnl ----------------------------

if test $deps_check = 1; then

AM_CHECK_PYMOD(dbus,,,[AC_MSG_ERROR(Could not find Python module dbus)])

fi


PKG_CHECK_MODULES(BLUEZ,
		bluez	>= 4.61
		libstartup-notification-1.0 >= 0.9
		gtk+-3.0
		glib-2.0 >= 2.32
		gthread-2.0 >= 2.32
)
AC_SUBST(BLUEZ_CFLAGS)
AC_SUBST(BLUEZ_LIBS)

PKG_CHECK_MODULES(GNOMEICONS, gnome-icon-theme,
		HAVE_GNOME_ICONS="yes", HAVE_GNOME_ICONS="no")

PKG_CHECK_MODULES(MATEICONS, mate-icon-theme,
		HAVE_MATE_ICONS="yes", HAVE_MATE_ICONS="no")

PKG_CHECK_MODULES(FAENZAICONS, faenza-icon-theme,
		HAVE_FAENZA_ICONS="yes", HAVE_FAENZA_ICONS="no")

if test "x$HAVE_GNOME_ICONS" = "xno" && test "x$HAVE_MATE_ICONS" = "xno" && test "xHAVE_FAENZA_ICONS" = "xno"; then
	AC_MSG_ERROR([Required icon themes not found.])
fi

PKG_CHECK_MODULES([PYGOBJECT],
                  [pygobject-2.0 >= 2.12],
                  [],
                  [PKG_CHECK_MODULES(PYGOBJECT, pygobject-3.0)]
)
AC_SUBST(PYGOBJECT_CFLAGS)
AC_SUBST(PYGOBJECT_LIBS)


AC_OUTPUT([
Makefile
apps/Makefile
sendto/Makefile
blueman/Makefile
blueman/Constants.py
blueman/bluez/Makefile
blueman/bluez/obex/Makefile
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
data/icons/hicolor/22x22/Makefile
data/icons/hicolor/22x22/status/Makefile
data/icons/hicolor/24x24/Makefile
data/icons/hicolor/24x24/status/Makefile
data/icons/hicolor/32x32/Makefile
data/icons/hicolor/32x32/actions/Makefile
data/icons/hicolor/32x32/status/Makefile
data/icons/hicolor/48x48/Makefile
data/icons/hicolor/48x48/actions/Makefile
data/icons/hicolor/48x48/devices/Makefile
data/icons/hicolor/48x48/status/Makefile
data/icons/hicolor/64x64/Makefile
data/icons/hicolor/64x64/status/Makefile
data/icons/hicolor/72x72/Makefile
data/icons/hicolor/72x72/status/Makefile
data/icons/hicolor/96x96/Makefile
data/icons/hicolor/96x96/status/Makefile
data/icons/hicolor/128x128/Makefile
data/icons/hicolor/128x128/status/Makefile
data/icons/hicolor/192x192/Makefile
data/icons/hicolor/192x192/status/Makefile
data/icons/hicolor/256x256/Makefile
data/icons/hicolor/256x256/status/Makefile
data/icons/hicolor/scalable/Makefile
data/icons/hicolor/scalable/devices/Makefile
data/icons/hicolor/scalable/actions/Makefile
data/icons/hicolor/scalable/status/Makefile
data/icons/main_icon/Makefile
data/icons/pixmaps/Makefile
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
echo Policykit-1 Enabled: $polkit_val
echo Nautilus sendto plugin enabled: $have_nst
echo Dhcpd 3 configuration file: $dhconfig
echo

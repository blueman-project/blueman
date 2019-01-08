AC_PREREQ(2.61)

AC_INIT([blueman], [2.0.8], [https://github.com/blueman-project/blueman/issues])
AC_CONFIG_HEADERS(config.h)
AM_INIT_AUTOMAKE([foreign dist-xz])

AM_MAINTAINER_MODE([enable])
AC_PROG_CC
AC_PROG_LIBTOOL
PKG_PROG_PKG_CONFIG

GETTEXT_PACKAGE="blueman"
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

AC_ENABLE_SHARED(yes)
AC_ENABLE_STATIC(no)

AM_PATH_PYTHON([2.7])
PYTHON_MAJOR_VERSION="$(echo ${PYTHON_VERSION} | cut -d . -f 1)"
PYTHON_MINOR_VERSION="$(echo ${PYTHON_VERSION} | cut -d . -f 2)"

if [test ${PYTHON_MAJOR_VERSION} -eq 3] && [test ${PYTHON_MINOR_VERSION} -lt 2];then
	AC_MSG_ERROR([Unsupported Python 3 version found (>=3.2 required)])
fi

PKG_CHECK_MODULES([PYTHON], [python-${PYTHON_VERSION}])
AC_SUBST(PYTHON_LIBS)
AC_SUBST(PYTHON_CFLAGS)

AC_ARG_ENABLE([runtime_deps_check],
  AS_HELP_STRING([--disable-runtime-deps-check], [Disable runtime dependency check (for package maintainers)]),
  [enable_runtime_deps_check=$enableval], [enable_runtime_deps_check=yes])

if test "x$enable_runtime_deps_check" = "xyes"; then
AM_CHECK_PYMOD([dbus],,,[AC_MSG_ERROR(Could not find Python module dbus)])
fi

PKG_CHECK_MODULES([PYGOBJECT],[pygobject-3.0])
AC_SUBST([PYGOBJECT_CFLAGS])
AC_SUBST([PYGOBJECT_LIBS])

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

AC_ARG_WITH([dhcp_config],
  AS_HELP_STRING([--with-dhcp-config=PATH], [Set dhcp3 server configuration path]),
  [dhconfig="$withval"], [dhconfig='/etc/dhcp3/dhcpd.conf'])
AC_SUBST([dhconfig])

dnl ---------------------------------


AC_ARG_ENABLE([polkit],
  AS_HELP_STRING([--enable-polkit], [Enable policykit support]),
  [enable_polkit=$enableval],[enable_polkit=yes])

AS_IF([test "x$enable_polkit" = "xyes"],
  [PKG_CHECK_MODULES([POLKIT], [polkit-agent-1], [have_polkit=yes], [have_polkit=no])],
  [have_polkit=no])

AM_CONDITIONAL([HAVE_POLKIT], [test "x$have_polkit" = "xyes"])

AC_SUBST([have_polkit])

AC_ARG_ENABLE([thunar-sendto],
  AS_HELP_STRING([--enable-thunar-sendto], [Enable thunar-sendto installation]),
  [have_thunar=$enableval], [have_thunar=yes])

AM_CONDITIONAL([HAVE_THUNAR], [test "x$have_thunar" = "xyes"])

AC_ARG_ENABLE(settings-integration,
  AS_HELP_STRING([--enable-settings-integration], [Enable settings manager integration with xfce and mate]),
  [have_settings=$enableval], [have_settings=yes])

AM_CONDITIONAL([HAVE_SETTINGS], [test "x$have_settings" = "xyes"])

dnl ----------------------------

PKG_CHECK_MODULES([BLUEZ], [bluez >= 4.61 gthread-2.0 >= 2.32])

AC_SUBST([BLUEZ_CFLAGS])
AC_SUBST([BLUEZ_LIBS])

PKG_CHECK_MODULES([GNOMEICONS],[gnome-icon-theme],
                  [HAVE_GNOME_ICONS="yes"], [HAVE_GNOME_ICONS="no"])

PKG_CHECK_MODULES([MATEICONS],[mate-icon-theme],
		  [HAVE_MATE_ICONS="yes"], [HAVE_MATE_ICONS="no"])

PKG_CHECK_MODULES([FAENZAICONS], [faenza-icon-theme],
		  [HAVE_FAENZA_ICONS="yes"], [HAVE_FAENZA_ICONS="no"])

if test "x$HAVE_GNOME_ICONS" = "xno" && test "x$HAVE_MATE_ICONS" = "xno" && test "xHAVE_FAENZA_ICONS" = "xno"; then
	AC_MSG_ERROR([Required icon themes not found.])
fi

# GSettings related settings
GLIB_GSETTINGS

AC_OUTPUT([
Makefile
apps/Makefile
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
blueman/plugins/mechanism/Rfcomm.py
blueman/plugins/manager/Makefile
blueman/main/Makefile
blueman/main/applet/Makefile
blueman/services/Makefile
blueman/services/meta/Makefile
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
echo Python version : $PYTHON_VERSION
echo Policykit-1 Enabled: $have_polkit
echo Thunar sendto installation enabled: $have_thunar
echo Settings menu integration enabled: $have_settings
echo Dhcpd 3 configuration file: $dhconfig
echo

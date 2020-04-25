#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PROJECT="blueman"

(test -f $srcdir/configure.ac) || {
    echo -n "**Error**: Directory \"\'$srcdir\'\" does not look like the"
    echo " top-level package directory"
    exit 1
}

if test -z "$AUTOGEN_SUBDIR_MODE" && test -z "$NOCONFIGURE"; then
    if test -z "$*"; then
        echo "I am going to run ./configure with no arguments - if you wish "
        echo "to pass any to it, please specify them on the $0 command line."
    fi
fi


autoreconf --verbose --force --install || exit $?

if test -z "$AUTOGEN_SUBDIR_MODE" && test -z "$NOCONFIGURE"; then
    $srcdir/configure --enable-maintainer-mode $AUTOGEN_CONFIGURE_ARGS "$@" || exit $?

    echo 
    echo "Now type 'make' to compile $PROJECT."
fi

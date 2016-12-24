# coding=utf-8
import os
import shlex
import subprocess
import sys

import gi
gi.require_version("Gdk", "3.0")
from gi.repository import GObject, GLib, Gdk, Gio

if sys.version_info.major == 2:
    from pipes import quote
else:
    from shlex import quote


def is_runnable_string(s):
    """Detects if the passed object is a string-like object that can be
    supplied to check_call in the subprocess module.
    """
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str) or isinstance(s, bytes)


def coerce_to_utf8(stringlikeobj):
    """Takes a string or a bytes literal and converts it to UTF-8.
    If the object is already unicode, or it isn't a string/bytes
    literal, it does nothing to the passed object.

    Will not raise UnicodeDecodeError if it is not possible to coerce
    the passed object to UTF-8.  It will simply mangle the conversion.
    """
    if bytes == str:
        # Python 2.7
        if isinstance(stringlikeobj, str):
            return stringlikeobj.decode("utf-8", errors='replace')
    else:
        # Python 3.x
        if isinstance(stringlikeobj, bytes):
            return stringlikeobj.decode("utf-8", errors='replace')
    return stringlikeobj


def coerce_to_str(unicodelikeobj):
    """Takes a Python 3 string or a Python 2 unicode object,
    and:

    * in Python 2, converts it to a plain Python 2 str, serializing it
      to UTF-8 if needed.
    * in Python 3, converts it to a Python 3 string literal.

    If the object is already a bytes / string literal, or it isn't a
    unicode object, it does nothing to the passed object.

    Think of this function as the antipode of `coerce_to_utf8`.

    This function *will* raise UnicodeDecodeError if a bytes literal
    is passed to it, but that literal contains invalid UTF-8 data.
    """
    if bytes == str:
        # Python 2.7
        if isinstance(unicodelikeobj, unicode):
            return unicodelikeobj.encode("utf-8")
    else:
        # Python 3.x
        if isinstance(unicodelikeobj, bytes):
            return unicodelikeobj.decode("utf-8")
    return unicodelikeobj


@GObject.type_register
class FileProcessor(GObject.Object):

    __gsignals__ = {
        # The started signal is invoked when the program starts
        # successfully.  After this, only the ended signal will
        # be emitted from this object, and only once.
        #
        # The started signal passes two things to registered callbacks:
        # 1. As is customary, the FileProcessor instance.
        # 2. The file name (not the complete path) of the file
        #    that was processed.
        'started': (
            GObject.SIGNAL_RUN_LAST,
            None,
            (str,)
        ),
        # The failed signal is invoked when the program fails to start.
        # After this, no more signals will be emitted from this object.
        #
        # The ended signal passes three things to registered callbacks:
        # 1. As is customary, the FileProcessor instance.
        # 2. The file name (not the complete path) of the file
        #    that was processed.
        # 3. An object that will be an Exception if the execution of the
        #    command failed.  It is customarily a GLib.Error.  Ordinarily,
        #    it would be a Python OSError, but there's no way to go back
        #    from a GError to an errno.
        'failed': (
            GObject.SIGNAL_RUN_LAST,
            None,
            (str, object)
        ),
        # The ended signal is invoked when the program finishes.
        # After this, no more signals will be emitted from this object.
        #
        # The ended signal passes three things to registered callbacks:
        # 1. As is customary, the FileProcessor instance.
        # 2. The file name (not the complete path) of the file
        #    that was processed.
        # 3. An object that may be an Exception if the execution of the
        #    command failed, or None if no error (startup or nonzero
        #    return code) took place during or after the execution of
        #    the command.
        #    The norm for any exception sent to the handler of this signal
        #    is a subprocess.CalledProcessError, signaling that the program
        #    exited with a non-zero return value (or was possibly killed
        #    by a signal, if its returncode attribute is negative).
        'ended': (
            GObject.SIGNAL_RUN_LAST,
            None,
            (str, object)
        ),
    }

    def __init__(self, command, filename, path):
        """Reference:

        command:  a string representing an executable in PATH or a full path,
                  or a list of strings representing a full command line as
                  subprocess.Popen() would expect.
        filename: just the filename of the file to process
        path:     the full path to the file to process

        You may connect to the signals of this object before you run start().
        Then the signals will trigger in the right order as per the signal
        documentation above.  If you connect to the signals after dispatching
        start(), then your program will miss some of the signals.

        Raises:
            ValueError: if the command is a string-like object, it contains
                        quotes, and they are unparsable in shell style.
            UnicodeDecodeError: if the string or list passed as a command,
                                or the path to the filename to process,
                                are bytes literals which contain invalid Unicode
                                data, and you are running under Python 3.
        """
        if is_runnable_string(command):
            self._strcmd = command
            self._listcmd = shlex.split(command)
        else:
            self._strcmd = " ".join(quote(arg) for arg in command)
            self._listcmd = command
        # Prepare the environment and the command line.  If the command line
        # or the environment are in an incorrect format, then we must serialize
        # them right now.
        self._listcmd = [coerce_to_str(s) for s in self._listcmd]
        self._env = [coerce_to_str("=".join(kv)) for kv in os.environ.items()]
        self._filename = filename
        self._path = coerce_to_str(path)
        GObject.Object.__init__(self)

    def get_command_line_as_utf8(self):
        """Returns the command line with the full path to process
        as a single UTF-8 string.

        Will not raise UnicodeDecodeError if the command passed
        to __init__ is a bytes literal or a Python 2.7 string
        that contains byte sequences not representable in UTF-8.
        What will happen is that invalid sequences will be transformed
        to 'unknown' characters.

        Therefore, this is intended for display purposes, rather than
        for use in os.system() or similar functions.
        """
        return coerce_to_utf8(self._strcmd) + u" " + coerce_to_utf8(self._path)

    def get_command_line_as_list(self):
        """Returns the command line with the full path to process
        as a properly-parsed list of string-like objects suitable for
        subprocess.check_call and similar functions.

        Every element in the list will be returned as a string literal
        in Python 3, or a plain str in Python 2.  If there are Unicode
        strings in the list under Python 2, they will be converted to
        str.  If there are bytes literals in the list under Python 3,
        they will be converted to Python 3 strings.

        This function *will* raise UnicodeDecodeError, if a bytes literal
        in the passed list contains invalid UTF-8 data.
        """
        return self._listcmd + [self._path]

    def start(self):
        """This method starts the program.

        From hereinonafter, the signals "started" and "ended" will be
        emitted, unless the signal "failed" is emitted, in which case
        the program never started because of an error.
        """
        # Look into the desktop app database for a suitable application
        # associated with the command being executed.
        appinfo = Gio.AppInfo.create_from_commandline(
            self._strcmd,
            None,
            Gio.AppInfoCreateFlags.NONE
        )

        # Set up the environment for the running program, including
        # desktop launch notifications, if they are supported.
        # This requires us to kill the previous DESKTOP_STARTUP_ID
        # that may be lingering in the environment.
        env = list(self._env)
        for elm in env[:]:
            if elm.startswith("DESKTOP_STARTUP_ID="):
                env.remove(elm)
        ctx = None
        notify_id = None
        try:
            ctx = Gdk.Display.get_app_launch_context(
                Gdk.Display.get_default()
            )
            notify_id = ctx.get_startup_notify_id(
                appinfo,
                [Gio.file_parse_name(self._path)]
            )
            if notify_id is not None:
                env.append('DESKTOP_STARTUP_ID=%s' % notify_id)
        except TypeError:  # Raised if Gdk.Display.get_default() returns None
            pass

        # Launch the program.
        cmd = self.get_command_line_as_list()
        try:
            pid, _, _, _ = GLib.spawn_async(
                cmd,
                flags=GLib.SPAWN_DO_NOT_REAP_CHILD | GLib.SPAWN_SEARCH_PATH,
                envp=env
            )
        except Exception as e:
            if ctx is not None and notify_id is not None:
                # The program failed to even start for some reason.
                ctx.launch_failed(notify_id)
            GLib.idle_add(lambda: self.emit("failed", self._filename, e))
            return

        # Signal that the program has started.
        GLib.idle_add(lambda: self.emit("started", self._filename))

        # Supervise the program.
        def on_child_exit(pid, retcode):
            try:
                GLib.spawn_check_exit_status(retcode)
                e = None
            except Exception as e:
                if str(e.domain) == 'g-exec-error-quark':
                    e = subprocess.CalledProcessError(-retcode, cmd)
                else:
                    e = subprocess.CalledProcessError(retcode >> 8, cmd)
            GLib.idle_add(lambda: self.emit("ended", self._filename, e))

        GLib.child_watch_add(pid, on_child_exit)

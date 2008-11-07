# errors.py - custom dbus bluez errors
#
# Copyright (C) 2008 Vinicius Gomes <vcgomes [at] gmail [dot] com>
# Copyright (C) 2008 Li Dongyang <Jerry87905 [at] gmail [dot] com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

class BluezDBusException(Exception):
    """
    Custom Bluez Dbus Exception class.
    """
    def __init__(self, reason):
        """ """
        self.reason = reason

    # __init__
    def __str__(self):
        """ """
        return self.reason
    # repr

class DBusFailedError(BluezDBusException):
    pass

class DBusInvalidArgumentsError(BluezDBusException):
    pass

class DBusNotAuthorizedError(BluezDBusException):
    pass

class DBusOutOfMemoryError(BluezDBusException):
    pass

class DBusNoSuchAdapterError(BluezDBusException):
    pass

class DBusNotReadyError(BluezDBusException):
    pass

class DBusNotAvailableError(BluezDBusException):
    pass

class DBusNotConnectedError(BluezDBusException):
    pass

class DBusConnectionAttemptFailedError(BluezDBusException):
    pass

class DBusAlreadyExistsError(BluezDBusException):
    pass

class DBusDoesNotExistError(BluezDBusException):
    pass

class DBusNoReplyError(BluezDBusException):
    pass

class DBusInProgressError(BluezDBusException):
    pass

class DBusNotSupportedError(BluezDBusException):
    pass

class DBusAuthenticationFailedError(BluezDBusException):
    pass

class DBusAuthenticationTimeoutError(BluezDBusException):
    pass

class DBusAuthenticationRejectedError(BluezDBusException):
    pass

class DBusAuthenticationCanceledError(BluezDBusException):
    pass

class DBusUnsupportedMajorClassError(BluezDBusException):
    pass

class DBusNotSupportedError(BluezDBusException):
    pass

class DBusServiceUnknownError(BluezDBusException):
    pass

class DBusMainLoopNotSupportedError(BluezDBusException):
    pass

class DBusMainLoopModuleNotFoundError(BluezDBusException):
    pass

class BluezUnavailableAgentMethodError(BluezDBusException):
    pass


__DICT_ERROR__ = {'org.bluez.Error.Failed:':DBusFailedError,
                  'org.bluez.Error.InvalidArguments:':DBusInvalidArgumentsError,
                  'org.bluez.Error.NotAuthorized:':DBusNotAuthorizedError,
                  'org.bluez.Error.OutOfMemory:':DBusOutOfMemoryError,
                  'org.bluez.Error.NoSuchAdapter:':DBusNoSuchAdapterError,
                  'org.bluez.Error.NotReady:':DBusNotReadyError,
                  'org.bluez.Error.NotAvailable:':DBusNotAvailableError,
                  'org.bluez.Error.NotConnected:':DBusNotConnectedError,
                  'org.bluez.serial.Error.ConnectionAttemptFailed:':DBusConnectionAttemptFailedError,
                  'org.bluez.Error.AlreadyExists:':DBusAlreadyExistsError,
                  'org.bluez.Error.DoesNotExist:':DBusDoesNotExistError,
                  'org.bluez.Error.InProgress:':DBusInProgressError,
                  'org.bluez.Error.NoReply:':DBusNoReplyError,
                  'org.bluez.Error.NotSupported:':DBusNotSupportedError,
                  'org.bluez.Error.AuthenticationFailed:':DBusAuthenticationFailedError,
                  'org.bluez.Error.AuthenticationTimeout:':DBusAuthenticationTimeoutError,
                  'org.bluez.Error.AuthenticationRejected:':DBusAuthenticationRejectedError,
                  'org.bluez.Error.AuthenticationCanceled:':DBusAuthenticationCanceledError,
                  'org.bluez.serial.Error.NotSupported:':DBusNotSupportedError,
                  'org.bluez.Error.UnsupportedMajorClass:':DBusUnsupportedMajorClassError,
                  'org.freedesktop.DBus.Error.ServiceUnknown:':DBusServiceUnknownError}

def parse_dbus_error(exception):
    """
    Return a custom exception based in the dbus exception that was raised.
    """
    global __DICT_ERROR__

    aux = "%s" % exception
    aux_splt = aux.split(None,1)
    try:
        return __DICT_ERROR__[aux_splt[0]](aux_splt[1])
    except KeyError:
        return exception
    # parse_dbus_error

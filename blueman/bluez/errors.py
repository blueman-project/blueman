# coding=utf-8


class BluezDBusException(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


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


class DBusServiceUnknownError(BluezDBusException):
    pass


class DBusMainLoopNotSupportedError(BluezDBusException):
    pass


class DBusMainLoopModuleNotFoundError(BluezDBusException):
    pass


class BluezUnavailableAgentMethodError(BluezDBusException):
    pass


__DICT_ERROR__ = {'org.bluez.Error.Failed': DBusFailedError,
                  'org.bluez.Error.InvalidArguments': DBusInvalidArgumentsError,
                  'org.bluez.Error.NotAuthorized': DBusNotAuthorizedError,
                  'org.bluez.Error.OutOfMemory': DBusOutOfMemoryError,
                  'org.bluez.Error.NoSuchAdapter': DBusNoSuchAdapterError,
                  'org.bluez.Error.NotReady': DBusNotReadyError,
                  'org.bluez.Error.NotAvailable': DBusNotAvailableError,
                  'org.bluez.Error.NotConnected': DBusNotConnectedError,
                  'org.bluez.serial.Error.ConnectionAttemptFailed': DBusConnectionAttemptFailedError,
                  'org.bluez.Error.AlreadyExists': DBusAlreadyExistsError,
                  'org.bluez.Error.DoesNotExist': DBusDoesNotExistError,
                  'org.bluez.Error.InProgress': DBusInProgressError,
                  'org.bluez.Error.NoReply': DBusNoReplyError,
                  'org.bluez.Error.NotSupported': DBusNotSupportedError,
                  'org.bluez.Error.AuthenticationFailed': DBusAuthenticationFailedError,
                  'org.bluez.Error.AuthenticationTimeout': DBusAuthenticationTimeoutError,
                  'org.bluez.Error.AuthenticationRejected': DBusAuthenticationRejectedError,
                  'org.bluez.Error.AuthenticationCanceled': DBusAuthenticationCanceledError,
                  'org.bluez.serial.Error.NotSupported': DBusNotSupportedError,
                  'org.bluez.Error.UnsupportedMajorClass': DBusUnsupportedMajorClassError,
                  'org.freedesktop.DBus.Error.ServiceUnknown': DBusServiceUnknownError}


def parse_dbus_error(exception):
    global __DICT_ERROR__

    gerror, dbus_error, message = exception.message.split(':', 2)
    try:
        return __DICT_ERROR__[dbus_error](message)
    except KeyError:
        return BluezDBusException(dbus_error + message)

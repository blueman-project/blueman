class PluginException(Exception):
    pass


class UnsupportedPlatformError(PluginException):
    pass


class PluginError(PluginException):
    pass


class PluginDependencyError(PluginError):
    pass

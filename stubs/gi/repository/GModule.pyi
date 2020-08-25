import builtins
import typing

from gi.repository import GLib


class Module():

    @staticmethod
    def build_path(directory: typing.Optional[builtins.str], module_name: builtins.str) -> builtins.str: ...

    def close(self) -> builtins.bool: ...

    @staticmethod
    def error() -> builtins.str: ...

    def make_resident(self) -> None: ...

    def name(self) -> builtins.str: ...

    @staticmethod
    def supported() -> builtins.bool: ...

    def symbol(self, symbol_name: builtins.str) -> typing.Tuple[builtins.bool, builtins.object]: ...


class ModuleFlags(GLib.Flags, builtins.int):
    LAZY = ...  # type: ModuleFlags
    LOCAL = ...  # type: ModuleFlags
    MASK = ...  # type: ModuleFlags


ModuleCheckInit = typing.Callable[[Module], builtins.str]
ModuleUnload = typing.Callable[[Module], None]


def module_build_path(directory: typing.Optional[builtins.str], module_name: builtins.str) -> builtins.str: ...


def module_error() -> builtins.str: ...


def module_supported() -> builtins.bool: ...



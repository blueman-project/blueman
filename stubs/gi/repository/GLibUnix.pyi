import builtins
import typing

from gi.repository import GLib



def error_quark() -> builtins.int: ...


def fd_add_full(priority: builtins.int, fd: builtins.int, condition: GLib.IOCondition, function: GLib.UnixFDSourceFunc, *user_data: typing.Optional[builtins.object]) -> builtins.int: ...


def fd_source_new(fd: builtins.int, condition: GLib.IOCondition) -> GLib.Source: ...


def get_passwd_entry(user_name: builtins.str) -> typing.Optional[builtins.object]: ...


def open_pipe(fds: builtins.int, flags: builtins.int) -> builtins.bool: ...


def set_fd_nonblocking(fd: builtins.int, nonblock: builtins.bool) -> builtins.bool: ...


def signal_add(priority: builtins.int, signum: builtins.int, handler: GLib.SourceFunc, *user_data: typing.Optional[builtins.object]) -> builtins.int: ...


def signal_source_new(signum: builtins.int) -> GLib.Source: ...

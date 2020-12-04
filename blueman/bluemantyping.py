from typing import Dict, Tuple, Union, TYPE_CHECKING
from gi.repository import GObject

if TYPE_CHECKING:
    from typing_extensions import Protocol

    class _HasGType(Protocol):
        __gtype__: GObject.GType

# Actually supported types are int, bool, str, float, and object but no subclasses, see
# https://github.com/GNOME/pygobject/blob/ac576400ecd554879c906791e6638d64bb8bcc2a/gi/pygi-type.c#L498
# (We shield the possibility to provide a str to avoid errors)
GSignals = Dict[str, Tuple[GObject.SignalFlags, None, Tuple[Union[None, type, GObject.GType, "_HasGType"], ...]]]

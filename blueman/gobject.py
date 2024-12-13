from typing import Any

from gi.types import GObjectMeta


class SingletonGObjectMeta(GObjectMeta):
    _instance: Any | None = None

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

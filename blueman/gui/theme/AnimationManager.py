"""Lightweight animation helper for Blueman Next.

GTK 3 ships a number of native animation primitives (``Gtk.Revealer``,
``Gtk.Stack`` transitions, ``Gtk.Spinner``, ``Gtk.ProgressBar``).  When
a custom animation is unavoidable (e.g. the Bluetooth radar or a
breathing status indicator) this module offers a thin wrapper around
``GLib.timeout_add`` that:

* Respects the application's reduced-motion preference.
* Tracks a numeric tick so widgets can interpolate their own state.
* Stops cleanly when the widget is hidden or destroyed.
* Pauses itself while the application is not visible to the user.

GTK does not provide a direct way to bind an animation to a widget's
lifecycle.  Callers should pass the widget as ``owner`` and call
:func:`stop_animation` from their ``destroy`` / ``unmap`` handler.
"""

from __future__ import annotations

import logging
import time
import weakref
from typing import Callable, Optional

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

log = logging.getLogger(__name__)


TickCallback = Callable[[int, float], bool]
"""Signature: ``(tick, frame_time_seconds) -> bool`` where the return
value matches ``GLib.timeout_add``: ``True`` to keep ticking, ``False``
to stop."""


_animations: dict[int, Optional[weakref.ReferenceType[Gtk.Widget]]] = {}
"""Registry of all currently running animations, keyed by source id.
Used by :func:`stop_all_animations` for shutdown and by the cleanup
helpers below."""


def start_animation(
    interval_ms: int,
    callback: TickCallback,
    *,
    owner: Optional[Gtk.Widget] = None,
) -> int:
    """Start a recurring timer.

    :param interval_ms: tick interval in milliseconds.
    :param callback: function called once per tick; must accept
      ``(tick_index, frame_time_seconds)`` and return ``True`` to
      continue, ``False`` to stop.
    :param owner: when provided, the animation is auto-stopped if the
      widget has been destroyed (``weakref``-based) and is paused
      when the widget is unmapped.
    :returns: the GLib source id (suitable for ``GLib.source_remove``).
    """
    from blueman.gui.theme.ThemeManager import ThemeManager

    if ThemeManager.get_default().reduced_motion():
        # Caller should display its static state.  We invoke the
        # callback once with tick=0 and frame_time=0 so the widget
        # paints a sensible initial frame, then stop.
        try:
            callback(0, 0.0)
        except Exception:
            log.exception("Initial animation frame failed")
        return 0

    tick = {"value": 0}
    started_at = time.monotonic()
    owner_ref = weakref.ref(owner) if owner is not None else None
    source = {"id": 0}

    def _tick() -> bool:
        if owner_ref is not None:
            widget = owner_ref()
            if widget is None:
                _animations.pop(source["id"], None)
                return False
            if not widget.get_mapped():
                return True  # pause, do not stop
        tick["value"] += 1
        try:
            keep_running = bool(callback(tick["value"], time.monotonic() - started_at))
        except Exception:
            log.exception("Animation tick callback failed")
            keep_running = False
        if not keep_running:
            _animations.pop(source["id"], None)
        return keep_running

    source_id = GLib.timeout_add(interval_ms, _tick)
    source["id"] = source_id
    _animations[source_id] = owner_ref
    return source_id


def stop_animation(source_id: int) -> None:
    """Stop a previously started animation if it is still running."""
    if not source_id:
        return
    if source_id in _animations:
        del _animations[source_id]
    try:
        GLib.source_remove(source_id)
    except Exception:
        pass


def stop_animation_safe(source_id_attr: str, owner: object) -> None:
    """Convenience helper for ``destroy`` handlers.

    Looks up ``owner.<source_id_attr>`` (an int) and stops it.  After
    stopping, the attribute is reset to ``0`` to prevent double-stop
    attempts.
    """
    sid = getattr(owner, source_id_attr, 0)
    if sid:
        stop_animation(sid)
        setattr(owner, source_id_attr, 0)


def stop_all_animations() -> None:
    """Stop every animation registered through this module.

    Intended for application shutdown; not safe to call concurrently
    with ``start_animation`` from other threads (GTK is single-threaded
    so this is fine in practice).
    """
    for sid in list(_animations.keys()):
        try:
            GLib.source_remove(sid)
        except Exception:
            pass
    _animations.clear()

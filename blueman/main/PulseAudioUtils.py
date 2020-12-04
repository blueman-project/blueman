from ctypes import *
from typing import Dict, TYPE_CHECKING, List, Callable, Mapping, Optional, Any

from gi.repository import GObject
from gi.repository import GLib
import weakref
import logging

from blueman.gobject import SingletonGObjectMeta
from blueman.bluemantyping import GSignals

try:
    libpulse = CDLL("libpulse.so.0")
    libpulse_glib = CDLL("libpulse-mainloop-glib.so.0")
except OSError:
    raise ImportError("Could not load pulseaudio shared library")

if TYPE_CHECKING:
    from ctypes import _FuncPointer, _NamedFuncPointer
    from typing_extensions import TypedDict

    class CardProfileInfo(TypedDict):
        name: str
        description: str
        n_sinks: int
        n_sources: int
        priority: int

    class CardInfo(TypedDict):
        name: str
        proplist: Dict[str, str]
        owner_module: int
        driver: str
        index: int
        profiles: List[CardProfileInfo]
        active_profile: str

pa_glib_mainloop_new = libpulse_glib.pa_glib_mainloop_new
pa_glib_mainloop_new.argtypes = [c_void_p]
pa_glib_mainloop_new.restype = c_void_p

pa_glib_mainloop_get_api = libpulse_glib.pa_glib_mainloop_get_api
pa_glib_mainloop_get_api.restype = c_void_p
pa_glib_mainloop_get_api.argtypes = [c_void_p]

PA_CONTEXT_UNCONNECTED = 0
PA_CONTEXT_CONNECTING = 1
PA_CONTEXT_AUTHORIZING = 2
PA_CONTEXT_SETTING_NAME = 3
PA_CONTEXT_READY = 4
PA_CONTEXT_FAILED = 5
PA_CONTEXT_TERMINATED = 6


class EventType:
    SINK = 0x0000
    SOURCE = 0x0001
    SINK_INPUT = 0x0002
    SOURCE_OUTPUT = 0x0003
    MODULE = 0x0004
    CLIENT = 0x0005
    SAMPLE_CACHE = 0x0006
    SERVER = 0x0007
    CARD = 0x0009
    FACILITY_MASK = 0x000F
    NEW = 0x0000
    CHANGE = 0x0010
    REMOVE = 0x0020
    TYPE_MASK = 0x0030


class NullError(Exception):
    pass


class PANotConnected(Exception):
    pass


class PaCardProfileInfo(Structure):
    pass


PaCardProfileInfo._fields_ = [
    ('name', c_char_p),
    ('description', c_char_p),
    ('n_sinks', c_uint32),
    ('n_sources', c_uint32),
    ('priority', c_uint32),
]


class PaCardInfo(Structure):
    pass


PaCardInfo._fields_ = [
    ('index', c_uint32),
    ('name', c_char_p),
    ('owner_module', c_uint32),
    ('driver', c_char_p),
    ('n_profiles', c_uint32),
    ('profiles', POINTER(PaCardProfileInfo)),
    ('active_profile', POINTER(PaCardProfileInfo)),
    ('proplist', c_void_p),
]
pa_context_notify_cb_t = CFUNCTYPE(None, c_void_p, py_object)

pa_context_index_cb_t = CFUNCTYPE(None, c_void_p, c_int, py_object)
pa_context_success_cb_t = pa_context_index_cb_t

pa_card_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(PaCardInfo), c_int, py_object)
pa_context_subscribe_cb_t = CFUNCTYPE(None, c_void_p, c_uint32, c_uint32, c_void_p)

pa_context_set_card_profile_by_name = libpulse.pa_context_set_card_profile_by_name
pa_context_set_card_profile_by_name.restype = c_void_p
pa_context_set_card_profile_by_name.argtypes = [c_void_p, c_char_p, c_char_p, pa_context_success_cb_t, py_object]

pa_context_set_card_profile_by_index = libpulse.pa_context_set_card_profile_by_index
pa_context_set_card_profile_by_index.restype = c_void_p
pa_context_set_card_profile_by_index.argtypes = [c_void_p, c_uint32, c_char_p, pa_context_success_cb_t, py_object]

pa_context_get_card_info_by_index = libpulse.pa_context_get_card_info_by_index
pa_context_get_card_info_by_index.restype = c_void_p
pa_context_get_card_info_by_index.argtypes = [c_void_p, c_uint32, pa_card_info_cb_t, py_object]

pa_context_get_card_info_list = libpulse.pa_context_get_card_info_list
pa_context_get_card_info_list.restype = c_void_p
pa_context_get_card_info_list.argtypes = [c_void_p, pa_card_info_cb_t, py_object]

pa_proplist_to_string_sep = libpulse.pa_proplist_to_string_sep
pa_proplist_to_string_sep.restype = POINTER(c_char)
pa_proplist_to_string_sep.argtypes = [c_void_p, c_char_p]

pa_context_subscribe = libpulse.pa_context_subscribe
pa_context_subscribe.restype = c_void_p
pa_context_subscribe.argtypes = [c_void_p, c_int, pa_context_success_cb_t, py_object]

pa_context_get_state = libpulse.pa_context_get_state
pa_context_get_state.restype = c_int
pa_context_get_state.argtypes = [c_void_p]

pa_xfree = libpulse.pa_xfree
pa_xfree.restype = None
pa_xfree.argtypes = [c_void_p]

pa_context_disconnect = libpulse.pa_context_disconnect
pa_context_disconnect.restype = None
pa_context_disconnect.argtypes = [c_void_p]

pa_context_unref = libpulse.pa_context_unref
pa_context_unref.restype = None
pa_context_unref.argtypes = [c_void_p]

pa_operation_unref = libpulse.pa_operation_unref
pa_operation_unref.restype = None
pa_operation_unref.argtypes = [c_void_p]

pa_context_set_state_callback = libpulse.pa_context_set_state_callback
pa_context_set_state_callback.restype = None
pa_context_set_state_callback.argtypes = [c_void_p, pa_context_notify_cb_t, py_object]

pa_context_connect = libpulse.pa_context_connect
pa_context_connect.restype = c_int
pa_context_connect.argtypes = [c_void_p, c_char_p, c_int, c_void_p]

pa_context_set_subscribe_callback = libpulse.pa_context_set_subscribe_callback
pa_context_set_subscribe_callback.restype = None
pa_context_set_subscribe_callback.argtypes = [c_void_p, pa_context_subscribe_cb_t, c_void_p]

pa_context_new = libpulse.pa_context_new
pa_context_new.restype = c_void_p
pa_context_new.argtypes = [c_void_p, c_char_p]


class PulseAudioUtils(GObject.GObject, metaclass=SingletonGObjectMeta):
    __gsignals__: GSignals = {
        'connected': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'disconnected': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'event': (GObject.SignalFlags.NO_HOOKS, None, (int, int)),
    }

    def check_connected(self) -> None:
        if not self.connected:
            raise PANotConnected("Connection to PulseAudio daemon is not established")

    @staticmethod
    def pa_context_event(pa_context: c_void_p, self: "PulseAudioUtils") -> None:
        if not self:
            return

        state = pa_context_get_state(pa_context)
        logging.info(state)
        if state == PA_CONTEXT_READY:
            self.connected = True
            self.emit("connected")
            mask = 0x0200 | 0x0010  # from enum pa_subscription_mask

            self.simple_callback(lambda x: logging.info(x),
                                 pa_context_subscribe,
                                 mask)
        else:
            if self.connected:
                self.emit("disconnected")
                self.connected = False

        if self.prev_state == PA_CONTEXT_READY and state == PA_CONTEXT_FAILED:
            logging.info("Pulseaudio probably crashed, restarting in 5s")
            GLib.timeout_add(5000, self.connect_pulseaudio)

        self.prev_state = state

    def __get_proplist(self, proplist: c_void_p) -> Dict[str, str]:
        if proplist:
            pla = pa_proplist_to_string_sep(proplist, b"|")
            pl = cast(pla, c_char_p)

            ls = [prop.decode("UTF-8") for prop in pl.value.split(b"|")] if pl.value else []
            del pl
            pa_xfree(pla)
        else:
            ls = []

        result = {}
        for item in ls:
            spl = [x.strip(" \"") for x in item.split("=")]
            if len(spl) == 2:
                result[spl[0]] = spl[1]

        return result

    if TYPE_CHECKING:
        class _ListCallbackInfo(TypedDict):
            cb_info: "_FuncPointer"
            handler: Callable[[Optional["pointer[PaCardInfo]"], bool], None]

    def __list_callback(self, _context: c_void_p, entry_info: "pointer[PaCardInfo]", eol: c_int,
                        info: "_ListCallbackInfo") -> None:
        if entry_info:
            info["handler"](entry_info, False)

        if eol:
            info["handler"](None, True)
            pythonapi.Py_DecRef(py_object(info))

    def __init_list_callback(self, func: Callable[..., c_void_p], cb_type: Callable[[Callable[[c_void_p,
                             "pointer[PaCardInfo]", c_int, "_ListCallbackInfo"], None]], "_FuncPointer"],
                             handler: Callable[[Optional["pointer[PaCardInfo]"], bool], None], *args: Any) -> None:
        info = {"cb_info": cb_type(self.__list_callback), "handler": handler}
        pythonapi.Py_IncRef(py_object(info))

        args += (info["cb_info"], py_object(info))
        op = func(self.pa_context, *args)
        pa_operation_unref(op)

    def simple_callback(self, handler: Callable[[int], None], func: "_NamedFuncPointer", *args: Any) -> None:

        def wrapper(_context: c_void_p, res: int, data: "_FuncPointer") -> None:
            if handler:
                handler(res)
            pythonapi.Py_DecRef(py_object(data))

        cb = pa_context_index_cb_t(wrapper)
        pythonapi.Py_IncRef(py_object(cb))

        args += (cb, py_object(cb))
        op = func(self.pa_context, *args)
        if not op:
            logging.info("Operation failed")
            logging.error(func.__name__)
        pa_operation_unref(op)

    def __card_info(self, card_info: "pointer[PaCardInfo]") -> "CardInfo":
        return {
            "name": card_info[0].name.decode("UTF-8"),
            "proplist": self.__get_proplist(card_info[0].proplist),
            "owner_module": card_info[0].owner_module,
            "driver": card_info[0].driver.decode("UTF-8"),
            "index": card_info[0].index,
            "profiles": [{
                "name": card_info[0].profiles[i].name.decode("UTF-8"),
                "description": card_info[0].profiles[i].description.decode("UTF-8"),
                "n_sinks": card_info[0].profiles[i].n_sinks,
                "n_sources": card_info[0].profiles[i].n_sources,
                "priority": card_info[0].profiles[i].priority,
            } for i in range(0, card_info[0].n_profiles)],
            "active_profile": card_info[0].active_profile[0].name.decode("UTF-8")
        }

    def list_cards(self, callback: Callable[[Mapping[str, "CardInfo"]], None]) -> None:
        self.check_connected()

        data: Dict[str, "CardInfo"] = {}

        def handler(entry_info: Optional["pointer[PaCardInfo]"], end: bool) -> None:
            if end:
                callback(data)
                return

            assert entry_info is not None
            entry = self.__card_info(entry_info)

            data[entry["name"]] = entry

        self.__init_list_callback(pa_context_get_card_info_list,
                                  pa_card_info_cb_t, handler)

    def get_card(self, card: int, callback: Callable[["CardInfo"], None]) -> None:
        self.check_connected()

        def handler(entry_info: Optional["pointer[PaCardInfo]"], end: bool) -> None:
            if end:
                return

            assert entry_info is not None
            callback(self.__card_info(entry_info))

        self.__init_list_callback(pa_context_get_card_info_by_index, pa_card_info_cb_t, handler, card)

    def set_card_profile(self, card: int, profile: str, callback: Callable[[int], None]) -> None:
        self.simple_callback(callback, pa_context_set_card_profile_by_index, card, profile.encode("UTF-8"))

    def __event_callback(self, _context: c_void_p, event_type: int, idx: int, _userdata: c_void_p) -> None:
        logging.info(f"{event_type} {idx}")
        self.emit("event", event_type, idx)

    def __init__(self) -> None:
        super().__init__()

        self.event_cb = pa_context_subscribe_cb_t(self.__event_callback)

        self.connected = False

        self.ctx_cb = pa_context_notify_cb_t(PulseAudioUtils.pa_context_event)

        mainloop = pa_glib_mainloop_new(None)
        self.pa_mainloop_api = pa_glib_mainloop_get_api(mainloop)

        self.pa_context = None

        self.prev_state = 0

        self.connect_pulseaudio()

        weakref.finalize(self, self._on_delete)

    def connect_pulseaudio(self) -> bool:
        if not self.connected:
            if self.pa_context:
                pa_context_unref(self.pa_context)

            self.pa_context = pa_context_new(self.pa_mainloop_api, b"Blueman")
            if not self.pa_context:
                raise NullError("PA Context returned NULL")

            self.weak = weakref.proxy(self)

            pa_context_set_state_callback(self.pa_context, self.ctx_cb, self.weak)
            pa_context_connect(self.pa_context, None, 0, None)

            pa_context_set_subscribe_callback(self.pa_context,
                                              self.event_cb,
                                              None)
        return False

    def _on_delete(self) -> None:
        logging.info("Destroying PulseAudioUtils instance")

        pa_context_disconnect(self.pa_context)
        pa_context_unref(self.pa_context)
        self.pa_context = None

        del self.ctx_cb

        del self.pa_mainloop_api

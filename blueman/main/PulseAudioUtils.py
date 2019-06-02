# coding=utf-8
from ctypes import *
from gi.repository import GObject
from gi.repository import GLib
from gi.types import GObjectMeta
import weakref
import logging

try:
    libpulse = CDLL("libpulse.so.0")
    libpulse_glib = CDLL("libpulse-mainloop-glib.so.0")
except OSError:
    raise ImportError("Could not load pulseaudio shared library")

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


class PaModuleInfo(Structure):
    _fields_ = [("index", c_uint),
                ("name", c_char_p),
                ("argument", c_char_p),
                ("n_used", c_int),
                ("proplist", c_void_p),
                ]


class PaSampleSpec(Structure):
    pass


PaSampleSpec._fields_ = [
    ('format', c_int),
    ('rate', c_uint32),
    ('channels', c_uint8),
]


class PaChannelMap(Structure):
    pass


PaChannelMap._fields_ = [
    ('channels', c_uint8),
    ('map', c_int * 32),
]


class PaCvolume(Structure):
    pass


PaCvolume._fields_ = [
    ('channels', c_uint8),
    ('values', c_uint32 * 32),
]


class PaSourceInfo(Structure):
    pass


PaSourceInfo._fields_ = [
    ('name', c_char_p),
    ('index', c_uint32),
    ('description', c_char_p),
    ('sample_spec', PaSampleSpec),
    ('channel_map', PaChannelMap),
    ('owner_module', c_uint32),
    ('volume', PaCvolume),
    ('mute', c_int),
    ('monitor_of_sink', c_uint32),
    ('monitor_of_sink_name', c_char_p),
    ('latency', c_uint64),
    ('driver', c_char_p),
    ('flags', c_int),
    ('proplist', c_void_p),
    ('configured_latency', c_ulong),
    # ('base_volume', pa_volume_t),
    # ('state', pa_source_state_t),
    # ('n_volume_steps', c_uint32),
    # ('card', c_uint32),
    # ('n_ports', c_uint32),
    # ('ports', POINTER(POINTER(pa_source_port_info))),
    # ('active_port', POINTER(pa_source_port_info)),
]


class PaSinkInfo(Structure):
    pass


PaSinkInfo._fields_ = [
    ('name', c_char_p),
    ('index', c_uint32),
    ('description', c_char_p),
    ('sample_spec', PaSampleSpec),
    ('channel_map', PaChannelMap),
    ('owner_module', c_uint32),
    ('volume', PaCvolume),
    ('mute', c_int),
    ('monitor_of_sink', c_uint32),
    ('monitor_of_sink_name', c_char_p),
    ('latency', c_uint64),
    ('driver', c_char_p),
    ('flags', c_int),
    ('proplist', c_void_p),
    ('configured_latency', c_ulong),
    # ('base_volume', pa_volume_t),
    # ('state', pa_source_state_t),
    # ('n_volume_steps', c_uint32),
    # ('card', c_uint32),
    # ('n_ports', c_uint32),
    # ('ports', POINTER(POINTER(pa_source_port_info))),
    # ('active_port', POINTER(pa_source_port_info)),
]


class PaSinkInputInfo(Structure):
    pass


PaSinkInputInfo._fields_ = [
    ('index', c_uint32),
    ('name', c_char_p),
    ('owner_module', c_uint32),
    ('client', c_uint32),
    ('sink', c_uint32),
    ('sample_spec', PaSampleSpec),
    ('channel_map', PaChannelMap),
    ('volume', PaCvolume),
    ('buffer_usec', c_uint64),
    ('sink_usec', c_uint64),
    ('resample_method', c_char_p),
    ('driver', c_char_p),
    ('mute', c_int),
    ('proplist', c_void_p),
]


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

pa_module_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(PaModuleInfo), c_int, py_object)
pa_source_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(PaSourceInfo), c_int, py_object)
pa_sink_input_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(PaSinkInputInfo), c_int, py_object)
pa_card_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(PaCardInfo), c_int, py_object)
pa_context_subscribe_cb_t = CFUNCTYPE(None, c_void_p, c_uint32, c_uint32, c_void_p)

pa_sink_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(PaSinkInfo), c_int, py_object)

pa_context_get_module_info_list = libpulse.pa_context_get_module_info_list
pa_context_get_module_info_list.restype = c_void_p
pa_context_get_module_info_list.argtypes = [c_void_p, pa_module_info_cb_t, py_object]

pa_context_set_card_profile_by_name = libpulse.pa_context_set_card_profile_by_name
pa_context_set_card_profile_by_name.restype = c_void_p
pa_context_set_card_profile_by_name.argtypes = [c_void_p, c_char_p, c_char_p, pa_context_success_cb_t, py_object]

pa_context_set_card_profile_by_index = libpulse.pa_context_set_card_profile_by_index
pa_context_set_card_profile_by_index.restype = c_void_p
pa_context_set_card_profile_by_index.argtypes = [c_void_p, c_uint32, c_char_p, pa_context_success_cb_t, py_object]

pa_context_get_card_info_by_index = libpulse.pa_context_get_card_info_by_index
pa_context_get_card_info_by_index.restype = c_void_p
pa_context_get_card_info_by_index.argtypes = [c_void_p, c_uint32, pa_card_info_cb_t, py_object]

pa_context_get_card_info_by_name = libpulse.pa_context_get_card_info_by_name
pa_context_get_card_info_by_name.restype = c_void_p
pa_context_get_card_info_by_name.argtypes = [c_void_p, c_char_p, pa_card_info_cb_t, py_object]

pa_context_get_card_info_list = libpulse.pa_context_get_card_info_list
pa_context_get_card_info_list.restype = c_void_p
pa_context_get_card_info_list.argtypes = [c_void_p, pa_card_info_cb_t, py_object]

pa_context_load_module = libpulse.pa_context_load_module
pa_context_load_module.restype = c_void_p
pa_context_load_module.argtypes = [c_void_p, c_char_p, c_char_p, pa_context_index_cb_t, py_object]

pa_context_unload_module = libpulse.pa_context_unload_module
pa_context_unload_module.restype = c_void_p
pa_context_unload_module.argtypes = [c_void_p, c_uint32, pa_context_success_cb_t, py_object]

pa_context_move_sink_input_by_index = libpulse.pa_context_move_sink_input_by_index
pa_context_move_sink_input_by_index.restype = c_void_p
pa_context_move_sink_input_by_index.argtypes = [c_void_p, c_uint32, c_uint32, pa_context_success_cb_t, py_object]

pa_context_get_sink_input_info_list = libpulse.pa_context_get_sink_input_info_list
pa_context_get_sink_input_info_list.restype = c_void_p
pa_context_get_sink_input_info_list.argtypes = [c_void_p, pa_sink_input_info_cb_t, py_object]

pa_context_get_sink_info_list = libpulse.pa_context_get_sink_info_list
pa_context_get_sink_info_list.restype = c_void_p
pa_context_get_sink_info_list.argtypes = [c_void_p, pa_sink_info_cb_t, py_object]

pa_context_get_sink_info_list = libpulse.pa_context_get_sink_info_list
pa_context_get_sink_info_list.restype = c_void_p
pa_context_get_sink_info_list.argtypes = [c_void_p, pa_sink_info_cb_t, py_object]

pa_context_get_source_info_list = libpulse.pa_context_get_source_info_list
pa_context_get_source_info_list.restype = c_void_p
pa_context_get_source_info_list.argtypes = [c_void_p, pa_source_info_cb_t, py_object]

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

pa_context_set_default_sink = libpulse.pa_context_set_default_sink
pa_context_set_default_sink.restype = c_void_p
pa_context_set_default_sink.argtypes = [c_void_p, c_char_p, pa_context_success_cb_t, py_object]

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

pa_get_library_version = libpulse.pa_get_library_version
pa_get_library_version.restype = c_char_p
pa_get_library_version.argtypes = []

pa_context_errno = libpulse.pa_context_errno
pa_context_errno.restype = c_int
pa_context_errno.argtypes = [c_void_p]


class PulseAudioUtilsMeta(GObjectMeta):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)

        return cls._instance


class PulseAudioUtils(GObject.GObject, metaclass=PulseAudioUtilsMeta):
    __gsignals__ = {
        'connected': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'disconnected': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'event': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    }

    def check_connected(self):
        if not self.connected:
            raise PANotConnected("Connection to PulseAudio daemon is not established")

    @staticmethod
    def pa_context_event(pa_context, self):
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
            GLib.timeout_add(5000, self.connect_rfcomm)

        self.prev_state = state

    def __get_proplist(self, proplist):
        if proplist:
            pla = pa_proplist_to_string_sep(proplist, b"|")
            pl = cast(pla, c_char_p)

            ls = [prop.decode("UTF-8") for prop in pl.value.split(b"|")]
            del pl
            pa_xfree(pla)
        else:
            ls = []

        proplist = {}
        for item in ls:
            spl = [x.strip(" \"") for x in item.split("=")]
            if len(spl) == 2:
                proplist[spl[0]] = spl[1]

        return proplist

    def __list_callback(self, context, entry_info, eol, info):
        if entry_info:
            info["handler"](entry_info, False)

        if eol:
            info["handler"](None, True)
            pythonapi.Py_DecRef(py_object(info))

    def __init_list_callback(self, func, cb_type, handler, *args):
        info = {"cb_info": cb_type(self.__list_callback), "handler": handler}
        pythonapi.Py_IncRef(py_object(info))

        args += (info["cb_info"], py_object(info))
        op = func(self.pa_context, *args)
        pa_operation_unref(op)

    def simple_callback(self, handler, func, *args):

        def wrapper(context, res, data):
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

    def list_sources(self, callback):
        self.check_connected()

        data = {}

        def handler(entry_info, end):
            if end:
                callback(data)
                return

            props = self.__get_proplist(entry_info[0].proplist)

            data[entry_info[0].index] = {
                "name": entry_info[0].name.decode("UTF-8"),
                "proplist": props,
                "description": entry_info[0].description.decode("UTF-8"),
                "owner_module": entry_info[0].owner_module,
                "driver": entry_info[0].driver.decode("UTF-8")
            }
            if end:
                callback(data)

        self.__init_list_callback(pa_context_get_source_info_list,
                                  pa_source_info_cb_t, handler)

    def list_sinks(self, callback, card_id=None):
        self.check_connected()

        data = {}

        def handler(entry_info, end):
            if end:
                callback(data)
                return
            props = self.__get_proplist(entry_info[0].proplist)

            data[entry_info[0].index] = {
                "name": entry_info[0].name.decode("UTF-8"),
                "proplist": props,
                "description": entry_info[0].description.decode("UTF-8"),
                "owner_module": entry_info[0].owner_module,
                "driver": entry_info[0].driver.decode("UTF-8")
            }

            if end:
                callback(data)

        if card_id is not None:
            self.__init_list_callback(pa_context_get_sink_info_list,
                                      pa_sink_info_cb_t, handler, card_id)
        else:
            self.__init_list_callback(pa_context_get_sink_info_list,
                                      pa_sink_info_cb_t, handler)

    def list_sink_inputs(self, callback):
        self.check_connected()

        data = {}

        def handler(entry_info, end):
            if end:
                callback(data)
                return

            props = self.__get_proplist(entry_info[0].proplist)

            data[entry_info[0].index] = {
                "name": entry_info[0].name.decode("UTF-8"),
                "proplist": props,
                "owner_module": entry_info[0].owner_module,
                "sink": entry_info[0].sink,
                "driver": entry_info[0].driver.decode("UTF-8")
            }

        self.__init_list_callback(pa_context_get_sink_input_info_list,
                                  pa_sink_input_info_cb_t, handler)

    def move_sink_input(self, input_id, sink_id, callback):
        self.check_connected()

        self.simple_callback(callback,
                             pa_context_move_sink_input_by_index,
                             int(input_id), int(sink_id))

    def set_default_sink(self, name, callback):
        self.check_connected()

        self.simple_callback(callback, pa_context_set_default_sink, name)

    # CARDS
    def __card_info(self, card_info):
        props = self.__get_proplist(card_info[0].proplist)
        stuff = {
            "name": card_info[0].name.decode("UTF-8"),
            "proplist": props,
            "owner_module": card_info[0].owner_module,
            "driver": card_info[0].driver.decode("UTF-8"),
            "index": card_info[0].index,
        }
        profiles = []
        for i in range(0, card_info[0].n_profiles):
            x = {
                "name": card_info[0].profiles[i].name.decode("UTF-8"),
                "description": card_info[0].profiles[i].description.decode("UTF-8"),
                "n_sinks": card_info[0].profiles[i].n_sinks,
                "n_sources": card_info[0].profiles[i].n_sources,
                "priority": card_info[0].profiles[i].priority,
            }
            profiles.append(x)

        stuff["profiles"] = profiles
        stuff["active_profile"] = card_info[0].active_profile[0].name.decode("UTF-8")

        return stuff

    def list_cards(self, callback):
        self.check_connected()

        data = {}

        def handler(entry_info, end):
            if end:
                callback(data)
                return

            entry = self.__card_info(entry_info)

            data[entry["name"]] = entry

        self.__init_list_callback(pa_context_get_card_info_list,
                                  pa_card_info_cb_t, handler)

    def get_card(self, card, callback):
        self.check_connected()

        def handler(entry_info, end):
            if end:
                return

            callback(self.__card_info(entry_info))

        if type(card) is str:
            fn = pa_context_get_card_info_by_name
        else:
            fn = pa_context_get_card_info_by_index

        self.__init_list_callback(fn,
                                  pa_card_info_cb_t, handler, card)

    def set_card_profile(self, card, profile, callback):
        profile = profile.encode("UTF-8")
        if type(card) is str:
            card = card.encode("UTF-8")
            fn = pa_context_set_card_profile_by_name
        else:
            fn = pa_context_set_card_profile_by_index

        self.simple_callback(callback, fn, card, profile)

    # #### Module API ####
    def list_module(self, callback):

        self.check_connected()
        data = {}

        def handler(entry_info, end):
            if end:
                callback(data)
                return

            props = self.__get_proplist(entry_info[0].proplist)
            data[entry_info[0].index] = {
                "name": entry_info[0].name.decode("UTF-8"),
                "argument": entry_info[0].argument.decode("UTF-8"),
                "n_used": entry_info[0].n_used,
                "proplist": props
            }

        self.__init_list_callback(pa_context_get_module_info_list,
                                  pa_module_info_cb_t, handler)

    def unload_module(self, index, callback):
        self.check_connected()

        self.simple_callback(callback, pa_context_unload_module, index)

    def load_module(self, name, args, callback):
        self.check_connected()

        def handler(res):
            if res < 0:
                callback(-pa_context_errno(self.pa_context))
            else:
                callback(res)

        self.simple_callback(handler, pa_context_load_module, name, args)

    #####################

    def __event_callback(self, context, event_type, idx, userdata):
        logging.info("%s %s" % (event_type, idx))
        self.emit("event", event_type, idx)

    def __init__(self):
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

    def connect_pulseaudio(self):
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

    def _on_delete(self):
        logging.info("Destroying PulseAudioUtils instance")

        pa_context_disconnect(self.pa_context)
        pa_context_unref(self.pa_context)
        self.pa_context = None

        del self.ctx_cb

        del self.pa_mainloop_api

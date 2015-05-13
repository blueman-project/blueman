from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from ctypes import *
from gi.repository import GObject
import weakref
from blueman.Functions import YELLOW, dprint

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


class pa_module_info(Structure):
    _fields_ = [("index", c_uint),
                ("name", c_char_p),
                ("argument", c_char_p),
                ("n_used", c_int),
                ("proplist", c_void_p),
    ]


class pa_sample_spec(Structure):
    pass


pa_sample_spec._fields_ = [
    ('format', c_int),
    ('rate', c_uint32),
    ('channels', c_uint8),
]


class pa_channel_map(Structure):
    pass


pa_channel_map._fields_ = [
    ('channels', c_uint8),
    ('map', c_int * 32),
]


class pa_cvolume(Structure):
    pass


pa_cvolume._fields_ = [
    ('channels', c_uint8),
    ('values', c_uint32 * 32),
]


class pa_source_info(Structure):
    pass


pa_source_info._fields_ = [
    ('name', c_char_p),
    ('index', c_uint32),
    ('description', c_char_p),
    ('sample_spec', pa_sample_spec),
    ('channel_map', pa_channel_map),
    ('owner_module', c_uint32),
    ('volume', pa_cvolume),
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


class pa_sink_info(Structure):
    pass


pa_sink_info._fields_ = [
    ('name', c_char_p),
    ('index', c_uint32),
    ('description', c_char_p),
    ('sample_spec', pa_sample_spec),
    ('channel_map', pa_channel_map),
    ('owner_module', c_uint32),
    ('volume', pa_cvolume),
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


class pa_sink_input_info(Structure):
    pass


pa_sink_input_info._fields_ = [
    ('index', c_uint32),
    ('name', c_char_p),
    ('owner_module', c_uint32),
    ('client', c_uint32),
    ('sink', c_uint32),
    ('sample_spec', pa_sample_spec),
    ('channel_map', pa_channel_map),
    ('volume', pa_cvolume),
    ('buffer_usec', c_uint64),
    ('sink_usec', c_uint64),
    ('resample_method', c_char_p),
    ('driver', c_char_p),
    ('mute', c_int),
    ('proplist', c_void_p),
]


class pa_card_profile_info(Structure):
    pass


pa_card_profile_info._fields_ = [
    ('name', c_char_p),
    ('description', c_char_p),
    ('n_sinks', c_uint32),
    ('n_sources', c_uint32),
    ('priority', c_uint32),
]


class pa_card_info(Structure):
    pass


pa_card_info._fields_ = [
    ('index', c_uint32),
    ('name', c_char_p),
    ('owner_module', c_uint32),
    ('driver', c_char_p),
    ('n_profiles', c_uint32),
    ('profiles', POINTER(pa_card_profile_info)),
    ('active_profile', POINTER(pa_card_profile_info)),
    ('proplist', c_void_p),
]
pa_context_notify_cb_t = CFUNCTYPE(None, c_void_p, py_object)

pa_context_index_cb_t = CFUNCTYPE(None, c_void_p, c_int, py_object)
pa_context_success_cb_t = pa_context_index_cb_t

pa_module_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_module_info), c_int, py_object)
pa_source_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_source_info), c_int, py_object)
pa_sink_input_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_sink_input_info), c_int, py_object)
pa_card_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_card_info), c_int, py_object)
pa_context_subscribe_cb_t = CFUNCTYPE(None, c_void_p, c_uint32, c_uint32, c_void_p)

pa_sink_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_sink_info), c_int, py_object)

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


class PulseAudioUtils(GObject.GObject):
    __gsignals__ = {
    str('connected'): (GObject.SignalFlags.NO_HOOKS, None, ()),
    str('disconnected'): (GObject.SignalFlags.NO_HOOKS, None, ()),
    str('event'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    }

    def check_connected(self):
        if not self.connected:
            raise PANotConnected("Connection to PulseAudio daemon is not established")

    @staticmethod
    def pa_context_event(pa_context, self):
        if not self:
            return

        state = pa_context_get_state(pa_context)
        dprint(state)
        if state == PA_CONTEXT_READY:
            self.connected = True
            self.emit("connected")
            MASK = 0x0200 | 0x0010  # from enum pa_subscription_mask

            self.simple_callback(lambda x: dprint(x),
                                 pa_context_subscribe,
                                 MASK)
        else:
            if self.connected:
                self.emit("disconnected")
                self.connected = False

        if self.prev_state == PA_CONTEXT_READY and state == PA_CONTEXT_FAILED:
            dprint("Pulseaudio probably crashed, restarting in 5s")
            GObject.timeout_add(5000, self.Connect)

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

    def __init_list_callback(self, function, cb_type, handler, *args):
        info = {"cb_info": cb_type(self.__list_callback), "handler": handler}
        pythonapi.Py_IncRef(py_object(info))

        args += (info["cb_info"], py_object(info))
        op = function(self.pa_context, *args)
        pa_operation_unref(op)

    def simple_callback(self, handler, function, *args):

        def wrapper(context, res, data):
            if handler:
                handler(res)
            pythonapi.Py_DecRef(py_object(data))

        cb = pa_context_index_cb_t(wrapper)
        pythonapi.Py_IncRef(py_object(cb))

        args += (cb, py_object(cb))
        op = function(self.pa_context, *args)
        if not op:
            dprint(YELLOW("Operation failed"))
            print(function.__name__)
        pa_operation_unref(op)


    def ListSources(self, callback):
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


    def ListSinks(self, callback, id=None):
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

        if id != None:
            self.__init_list_callback(pa_context_get_sink_info_list,
                                      pa_sink_info_cb_t, handler, id)
        else:
            self.__init_list_callback(pa_context_get_sink_info_list,
                                      pa_sink_info_cb_t, handler)

    def ListSinkInputs(self, callback):
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

    def MoveSinkInput(self, input_id, sink_id, callback):
        self.check_connected()

        self.simple_callback(callback,
                             pa_context_move_sink_input_by_index,
                             int(input_id), int(sink_id))

    def SetDefaultSink(self, name, callback):
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
        l = []
        for i in range(0, card_info[0].n_profiles):
            x = {
            "name": card_info[0].profiles[i].name.decode("UTF-8"),
            "description": card_info[0].profiles[i].description.decode("UTF-8"),
            "n_sinks": card_info[0].profiles[i].n_sinks,
            "n_sources": card_info[0].profiles[i].n_sources,
            "priority": card_info[0].profiles[i].priority,
            }
            l.append(x)

        stuff["profiles"] = l
        stuff["active_profile"] = card_info[0].active_profile[0].name.decode("UTF-8")

        return stuff

    def ListCards(self, callback):
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

    def GetCard(self, card, callback):
        self.check_connected()

        def handler(entry_info, end):
            if end:
                return

            callback(self.__card_info(entry_info))

        if hasattr(card, "format") and hasattr(card, "upper"):
            fn = pa_context_get_card_info_by_name
        else:
            fn = pa_context_get_card_info_by_index

        self.__init_list_callback(fn,
                                  pa_card_info_cb_t, handler, card)

    def SetCardProfile(self, card, profile, callback):
        profile = profile.encode("UTF-8")
        if hasattr(card, "format") and hasattr(card, "upper"):
            card = card.encode("UTF-8")
            fn = pa_context_set_card_profile_by_name
        else:
            fn = pa_context_set_card_profile_by_index

        self.simple_callback(callback, fn, card, profile)

    #### Module API #######
    #from gi.repository import Gtk
    def ListModules(self, callback):

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

    def UnloadModule(self, index, callback):
        self.check_connected()

        self.simple_callback(callback, pa_context_unload_module, index)

    def LoadModule(self, name, args, callback):
        self.check_connected()

        def handler(res):
            if res < 0:
                callback(-pa_context_errno(self.pa_context))
            else:
                callback(res)


        self.simple_callback(handler, pa_context_load_module, name, args)

    #####################

    def GetVersion(self):
        v = pa_get_library_version().decode("UTF-8")
        try:
            a = v.split("-")[0].split(".")
            a = map(lambda x: int(x), a)
        except:
            a = (0, 0, 0)
        return a

    inst = None

    def __new__(cls):
        if cls.inst:
            return PulseAudioUtils.inst
        else:
            return super(PulseAudioUtils, cls).__new__(cls)


    def __event_callback(self, context, event_type, idx, userdata):
        dprint(event_type, idx)
        self.emit("event", event_type, idx)

    def __init__(self):
        if PulseAudioUtils.inst != None:
            return

        PulseAudioUtils.inst = self
        GObject.GObject.__init__(self)

        self.event_cb = pa_context_subscribe_cb_t(self.__event_callback)

        self.connected = False

        self.ctx_cb = pa_context_notify_cb_t(PulseAudioUtils.pa_context_event)

        mainloop = pa_glib_mainloop_new(None)
        self.pa_mainloop_api = pa_glib_mainloop_get_api(mainloop)

        self.pa_context = None

        self.prev_state = 0

        self.Connect()


    def Connect(self):
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


    def __del__(self):
        dprint("Destroying PulseAudioUtils instance")

        pa_context_disconnect(self.pa_context)
        pa_context_unref(self.pa_context)
        self.pa_context = None

        del self.ctx_cb

        del self.pa_mainloop_api

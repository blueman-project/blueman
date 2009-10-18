from ctypes import *
import gobject
import weakref
import blueman.Functions

PA_CONTEXT_UNCONNECTED =  0
PA_CONTEXT_CONNECTING	= 1
PA_CONTEXT_AUTHORIZING	= 2
PA_CONTEXT_SETTING_NAME	= 3
PA_CONTEXT_READY	= 4
PA_CONTEXT_FAILED	= 5
PA_CONTEXT_TERMINATED	= 6
	
pa_context_notify_cb_t = CFUNCTYPE(None, c_void_p, py_object)
pa_context_index_cb_t = CFUNCTYPE(None, c_void_p, c_int, py_object)

class NullError(Exception):
	pass
	
class PANotConnected(Exception):
	pass
	
class pa_module_info(Structure):
	_fields_ = [("index", c_uint),
                    ("name", c_char_p),
                    ("argument", c_char_p),
                    ("n_used", c_uint),
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
    ('latency', c_ulong),
    ('driver', c_char_p),
    ('flags', c_int),
    ('proplist', c_void_p),
    ('configured_latency', c_ulong),
    #('base_volume', pa_volume_t),
    #('state', pa_source_state_t),
    #('n_volume_steps', uint32_t),
    #('card', uint32_t),
    #('n_ports', uint32_t),
    #('ports', POINTER(POINTER(pa_source_port_info))),
   # ('active_port', POINTER(pa_source_port_info)),
]

           
pa_module_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_module_info), c_int, py_object)
pa_source_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_source_info), c_int, py_object)

class PulseAudioUtils(gobject.GObject):
	__gsignals__ = {
		'connected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, ()),
		'disconnected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, ()),
	}
	
	def check_connected(self):
		if not self.connected:
			raise PANotConnected("Connection to PulseAudio daemon is not established")
	
	@staticmethod
	def pa_context_event(pa_context, self):
		if not self:
			return
			
		state = self.pa.pa_context_get_state(pa_context)
		dprint(state)
		if state == PA_CONTEXT_READY:
			self.connected = True
			self.emit("connected")
		else:
			if self.connected:
				self.emit("disconnected")
				self.connected = False
		
		if self.prev_state == PA_CONTEXT_READY and state == PA_CONTEXT_FAILED:
			dprint("Pulseaudio probably crashed, restarting in 5s")
			gobject.timeout_add(5000, self.Connect)
			
		self.prev_state = state
			
			
	def pa_get_module_info_cb(self, context, module_info, eol, info):

		if module_info:
			if module_info[0].proplist:
				pla = self.pa.pa_proplist_to_string_sep(module_info[0].proplist, "|")
				pl = cast(pla, c_char_p)
				ls = pl.value.split("|")
				del pl
				self.pa.pa_xfree(pla)
			else:
				ls = []
			
			proplist = {}
			for item in ls:
				spl = map(lambda x: x.strip(" \""), item.split("="))
				proplist[spl[0]] = spl[1]
				
			info["modules"][module_info[0].index] = {
				"name": module_info[0].name,
				"argument": module_info[0].argument,
				"n_used" : module_info[0].n_used,
				"proplist": proplist

			}


		if eol:
			if info["callback"]:
				info["callback"](info["modules"])
			pythonapi.Py_DecRef(py_object(info))
			
	def pa_get_source_info_cb(self, context, source_info, eol, info):
		if source_info:
			if source_info[0].proplist:
				pla = self.pa.pa_proplist_to_string_sep(source_info[0].proplist, "|")
				pl = cast(pla, c_char_p)
				ls = pl.value.split("|")

				del pl
				self.pa.pa_xfree(pla)
			else:
				ls = []
			
			proplist = {}
			for item in ls:
				spl = map(lambda x: x.strip(" \""), item.split("="))
				proplist[spl[0]] = spl[1]

			
			info["sources"][source_info[0].index] = {
				"name": source_info[0].name,
				"proplist": proplist,
				"description": source_info[0].description,
				"owner_module": source_info[0].owner_module,
				"driver": source_info[0].driver
			}

		if eol:
			if info["callback"]:
				info["callback"](info["sources"])
			pythonapi.Py_DecRef(py_object(info))
	
	def unload_module_cb(self, context, success, info):
		if info["callback"]:
			info["callback"](success)
		pythonapi.Py_DecRef(py_object(info))
	
	def pa_load_module_cb(self, context, idx, info):
		if info["callback"]:
			if idx < 0:
				info["callback"](-self.pa.pa_context_errno(context))
			else:
				info["callback"](idx)
				
		pythonapi.Py_DecRef(py_object(info))
	
	def ListSources(self, callback):
		self.check_connected()
		info = {"callback" : callback, "cb_info": pa_source_info_cb_t(self.pa_get_source_info_cb), "sources" : {} }
		pythonapi.Py_IncRef(py_object(info))
		
		
		self.pa.pa_operation_unref(self.pa.pa_context_get_source_info_list(self.pa_context, info["cb_info"], py_object(info)))
	
	def ListSinks(self, callback):
		self.check_connected()
		info = {"callback" : callback, "cb_info": pa_source_info_cb_t(self.pa_get_source_info_cb), "sources" : {} }
		pythonapi.Py_IncRef(py_object(info))
		
		self.pa.pa_operation_unref(self.pa.pa_context_get_sink_info_list(self.pa_context, info["cb_info"], py_object(info)))
			
#### Module API #######	
	def ListModules(self, callback):
		self.check_connected()
		info = {"callback" : callback, "cb_info": pa_module_info_cb_t(self.pa_get_module_info_cb), "modules" : {} }
		pythonapi.Py_IncRef(py_object(info))
		
		self.pa.pa_operation_unref(self.pa.pa_context_get_module_info_list(self.pa_context, info["cb_info"], py_object(info)))
				
	def UnloadModule(self, index, callback):
		self.check_connected()
		info = {"callback" : callback, "cb": pa_context_index_cb_t(self.unload_module_cb) }
		
		pythonapi.Py_IncRef(py_object(info))
		self.pa.pa_operation_unref(self.pa.pa_context_unload_module(self.pa_context, index, info["cb"], py_object(info)))		
	
	def LoadModule(self, name, args, callback):
		self.check_connected()
		info = {"callback": callback, "cb_index": pa_context_index_cb_t(self.pa_load_module_cb)}
		pythonapi.Py_IncRef(py_object(info))
		
		self.pa.pa_context_load_module.argtypes = (c_void_p, c_char_p, c_char_p, c_void_p, py_object)
		self.pa.pa_operation_unref(self.pa.pa_context_load_module(self.pa_context, name, args, info["cb_index"], py_object(info)))

#####################	

	def GetVersion(self):
		self.pa.pa_get_library_version.restype = c_char_p
		return self.pa.pa_get_library_version()
	
	def __init__(self):
		gobject.GObject.__init__(self)
		
		self.connected = False
		
		self.ctx_cb = pa_context_notify_cb_t(PulseAudioUtils.pa_context_event)

		self.pa = CDLL("libpulse.so.0")
		self.pa_m = CDLL("libpulse-mainloop-glib.so.0")
		self.g = CDLL("libglib-2.0.so.0")

		self.pa_mainloop = self.pa_m.pa_glib_mainloop_new(self.g.g_main_context_default())
		self.pa_mainloop_api = self.pa_m.pa_glib_mainloop_get_api(self.pa_mainloop)
		
		self.pa_context = None

		self.prev_state = 0
		
		self.Connect()
		
		
	def Connect(self):
		if not self.connected:
			if self.pa_context:
				self.pa.pa_context_unref(self.pa_context)
			
			self.pa_context = self.pa.pa_context_new (self.pa_mainloop_api, "Blueman")
			if not self.pa_context:
				raise NullError("PA Context returned NULL")
			
			self.weak = weakref.proxy(self)
			
			self.pa.pa_context_set_state_callback.argtypes = (c_void_p, pa_context_notify_cb_t, py_object)
			self.pa.pa_context_set_state_callback(self.pa_context, self.ctx_cb, self.weak)
			self.pa.pa_context_connect (self.pa_context, None, 0, None)
		
	def __del__(self):
		dprint("Destroying PulseAudioUtils instance")
		
		self.pa.pa_context_disconnect(self.pa_context)
		self.pa.pa_context_unref(self.pa_context)
		self.pa_context = None
		
		del self.ctx_cb
		
		self.pa_m.pa_glib_mainloop_free(self.pa_mainloop)
		del self.pa_mainloop
		
		del self.pa_mainloop_api
	
		


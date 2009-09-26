from ctypes import *
import gobject
import blueman.Functions

PA_CONTEXT_UNCONNECTED =  0
PA_CONTEXT_CONNECTING	= 1
PA_CONTEXT_AUTHORIZING	= 2
PA_CONTEXT_SETTING_NAME	= 3
PA_CONTEXT_READY	= 4
PA_CONTEXT_FAILED	= 5
PA_CONTEXT_TERMINATED	= 6
	
pa_context_notify_cb_t = CFUNCTYPE(None, c_void_p, c_void_p)
pa_context_index_cb_t = CFUNCTYPE(None, c_void_p, c_int, py_object)

class pa_module_info(Structure):
	_fields_ = [("index", c_uint),
                    ("name", c_char_p),
                    ("argument", c_char_p),
                    ("n_used", c_uint),
                    ("proplist", c_void_p),
                    ]
                    
pa_module_info_cb_t = CFUNCTYPE(None, c_void_p, POINTER(pa_module_info), c_int, py_object)

class PulseAudioUtils(gobject.GObject):
	__gsignals__ = {
		'connected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, ()),
		'disconnected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, ()),
	}
	
	def pa_context_event(self, pa_context, userdata):
		state = self.pa.pa_context_get_state(pa_context)
		dprint(state)
		if state == PA_CONTEXT_READY:
			self.connected = True
			self.emit("connected")
		else:
			if self.connected:
				self.emit("disconnected")
				self.connected = False
			
			
	def pa_get_module_info_cb(self, context, module_info, eol, info):

		if module_info:
			
			pla = self.pa.pa_proplist_to_string_sep(module_info[0].proplist, "|")
			pl = cast(pla, c_char_p)
			
			info["modules"][module_info[0].index] = {
				"name": module_info[0].name,
				"argument": module_info[0].argument,
				"n_used" : module_info[0].n_used,
				"proplist": pl.value.split("|")

			}
			del pl
			self.pa.pa_xfree(pla)

		if eol:
			info["callback"](info["modules"])
			pythonapi.Py_DecRef(py_object(info))
			
	
	def unload_module_cb(self, context, success, info):
		info["callback"](success)
		pythonapi.Py_DecRef(py_object(info))
	
	def pa_load_module_cb(self, context, idx, info):
		if idx < 0:
			info["callback"](-self.pa.pa_context_errno(context))
		else:
			info["callback"](idx)
		pythonapi.Py_DecRef(py_object(info))

#### Module API #######	
	def pa_list_modules(self, callback):
		info = {"callback" : callback, "cb_info": pa_module_info_cb_t(self.pa_get_module_info_cb), "modules" : {} }
		pythonapi.Py_IncRef(py_object(info))
		
		if self.connected:
			self.pa.pa_operation_unref(self.pa.pa_context_get_module_info_list(self.pa_context, info["cb_info"], py_object(info)))
				
	def pa_unload_module(self, index, callback):
		info = {"callback" : callback, "cb": pa_context_index_cb_t(self.unload_module_cb) }
		
		pythonapi.Py_IncRef(py_object(info))
		self.pa.pa_operation_unref(self.pa.pa_context_unload_module(self.pa_context, index, info["cb"], py_object(info)))		
	
	def pa_load_module(self, name, args, callback):
		info = {"callback": callback, "cb_index": pa_context_index_cb_t(self.pa_load_module_cb)}
		pythonapi.Py_IncRef(py_object(info))
		
		self.pa.pa_operation_unref(self.pa.pa_context_load_module(self.pa_context, name, args, info["cb_index"], py_object(info)))

#####################			
	
	def __init__(self):
		gobject.GObject.__init__(self)
		
		self.connected = False
		
		self.ctx_cb = pa_context_notify_cb_t(self.pa_context_event)
		pythonapi.Py_DecRef(py_object(self))

		self.pa = CDLL("libpulse.so.0")
		self.pa_m = CDLL("libpulse-mainloop-glib.so.0")
		self.g = CDLL("libglib-2.0.so.0")

		self.pa_mainloop = self.pa_m.pa_glib_mainloop_new(self.g.g_main_context_default())
		self.pa_mainloop_api = self.pa_m.pa_glib_mainloop_get_api(self.pa_mainloop)
		

		self.pa_context = self.pa.pa_context_new (self.pa_mainloop_api, "Blueman")
		
		self.pa.pa_context_set_state_callback(self.pa_context, self.ctx_cb, None);

		self.pa.pa_context_connect (self.pa_context, None, 0, None)
		
	def __del__(self):
		pythonapi.Py_IncRef(py_object(self))
		
		dprint("Destroying PulseAudioUtils instance")
		
		self.pa.pa_context_disconnect(self.pa_context)
		self.pa.pa_context_unref(self.pa_context)
		self.pa_context = None
		
		del self.ctx_cb
		
		self.pa_m.pa_glib_mainloop_free(self.pa_mainloop)
		del self.pa_mainloop
		
		del self.pa_mainloop_api
	
		


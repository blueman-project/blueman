# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Device import Device as BluezDevice
from blueman.main.Device import Device
from blueman.gui.Notification import Notification
from blueman.main.NetConf import have
from blueman.main.PulseAudioUtils import PulseAudioUtils
from subprocess import Popen, PIPE
import gobject

import dbus
from blueman.main.SignalTracker import SignalTracker

class SourceRedirector:
	def __init__(self, module_id, device_path, pa_utils):
		self.module_id = module_id
		self.pa_utils = pa_utils
		self.device = Device(device_path)
		self.signals = SignalTracker()
		self.bus = dbus.SystemBus()
		self.signals.Handle("dbus", self.bus, self.on_source_prop_change, "PropertyChanged", "org.bluez.AudioSource", path=device_path)
		
		self.pacat = None
		self.parec = None
		self.loopback_id = None
		
		dprint("Starting source redirector")
		def sources_cb(sources):
			for k, v in sources.iteritems():
				props = v["proplist"]
				if "bluetooth.protocol" in props:
					if props["bluetooth.protocol"] == "a2dp_source":
						if v["owner_module"] == self.module_id:
							dprint("Found source", k)
							self.start_redirect(k)
							return
			dprint("Source not found :(")
		
		self.pa_utils.ListSources(sources_cb)
		
	def start_redirect(self, source):

		def on_load(res):
			dprint("module-loopback load result", res)
			if res < 0:
				self.parec = Popen(["parec", "-d", str(source)], stdout=PIPE)
				self.pacat = Popen(["pacat", "--client-name=Blueman", "--stream-name=%s" % self.device.Address, "--property=application.icon_name=blueman"], stdin=self.parec.stdout)
			else:
				self.loopback_id = res
				
		self.pa_utils.LoadModule("module-loopback", "source=%d" % source, on_load)
		
	def on_source_prop_change(self, key, value):
		if key == "State":
			if value != "playing":
				if self.pacat:
					self.pacat.terminate()
				if self.parec:
					self.parec.terminate()
				if self.loopback_id:
					self.pa_utils.UnloadModule(self.loopback_id, lambda x: dprint("Loopback module unload result", x))
				
				self.signals.DisconnectAll()

				del self.pa_utils
				
	def __del__(self):
		dprint("Destroying redirector")
		
class Module(gobject.GObject):
	__gsignals__ = {
		'loaded' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, ()),
	}	
	def __init__(self):
		gobject.GObject.__init__(self)
		self.refcount = 0
		self.id = None
		
	def unload(self):
		dprint(self.id)
		pa = PulseAudioUtils()
		id = self.id
		pa.UnloadModule(self.id, lambda x: dprint("Unload %s result %s" % (id, x)))
		self.id = None
		self.refcount = 0
		
	def ref(self):
		self.refcount+=1
		
		dprint(self.id, self.refcount)
		
	def unref(self):
		self.refcount-=1
		
		dprint(self.id, self.refcount)
		
		if self.refcount <= 0 and self.id:
			self.unload()
			
	def load(self, args, cb):
		if self.id != None:
			self.unload()
		
		def load_cb(res):
			if res > 0:
				self.refcount = 1
				self.id = res
				if cb:
					cb(res)
				self.emit("loaded")
			else:
				self.refcount = 0
				self.id = None
		
		PulseAudioUtils().LoadModule("module-bluetooth-device",
									 args,
									 load_cb)

class PulseAudio(AppletPlugin):
	__author__ = "Walmis"
	__description__ = _("Automatically manages Pulseaudio Bluetooth sinks/sources.\n"
						"<b>Note:</b> Requires pulseaudio 0.9.15 or higher")
	__icon__ = "audio-card"
	__options__  = {
		"checked" : (bool, False),
		"make_default_sink": (bool, 
							  True, 
							  _("Make default sink"), 
							  _("Make the a2dp audio sink the default after connection")),
		"move_streams": (bool, 
						 True, 
						 _("Move streams"), 
						 _("Move existing audio streams to bluetooth device"))
	}
	def on_load(self, applet):
		self.signals = SignalTracker()
		if not self.get_option("checked"):
			self.set_option("checked", True)
			if not have("pactl"):
				applet.Plugins.SetConfig("PulseAudio", False)
				return
			
		self.bus = dbus.SystemBus()
		
		self.connected_sources = []
		self.connected_sinks = []
		self.connected_hs = []
		
		self.loaded_modules = {}
		
		self.pulse_utils = PulseAudioUtils()
		version = self.pulse_utils.GetVersion()
		dprint("PulseAudio version:", version)
		
		if int(version.split(".")[2]) < 15:
			raise Exception("PulseAudio too old, required 0.9.15 or higher")
		
		self.signals.Handle("dbus", 
							self.bus, 
							self.on_sink_prop_change, 
							"PropertyChanged", 
							"org.bluez.AudioSink", 
							path_keyword="device")
							
		self.signals.Handle("dbus", 
							self.bus, 
							self.on_source_prop_change, 
							"PropertyChanged", 
							"org.bluez.AudioSource", 
							path_keyword="device")
							
		self.signals.Handle("dbus", 
							self.bus, 
							self.on_hsp_prop_change, 
							"PropertyChanged", 
							"org.bluez.Headset", 
							path_keyword="device")
		

		self.signals.Handle(self.pulse_utils, "connected", self.on_pulse_connected)
		
	def on_pulse_connected(self, pa_utils):
		def modules_cb(modules):
			for k, v in modules.iteritems():
				if v["name"] == "module-bluetooth-discover":
					pa_utils.UnloadModule(k, lambda x: dprint("Unload module-bluetooth-discover result", x))
			
		self.pulse_utils.ListModules(modules_cb)			
	
	def on_unload(self):
		self.signals.DisconnectAll()
		
	def load_module(self, dev_path, args, cb=None):
		if not dev_path in self.loaded_modules:
			m = Module()
			m.load(args, cb)
			self.loaded_modules[dev_path] = m
		else:
			self.loaded_modules[dev_path].ref()
		
	def try_unload_module(self, dev_path):
		try:
			m = self.loaded_modules[dev_path]
			m.unref()
			if m.refcount == 0:
				del self.loaded_modules[dev_path]
		except Exception, e:
			dprint(e)
		
	def on_source_prop_change(self, key, value, device):
		dprint(key, value)
			
		if key == "State":
			if value == "connected":
				if not device in self.connected_sources:
					self.connected_sources.append(device)
					d = Device(device)
					self.load_module(device, "path=%s address=%s profile=a2dp_source source_properties=device.icon_name=blueman card_properties=device.icon_name=blueman" % (device, d.Address))
					
			elif value == "disconnected":
				self.try_unload_module(device)
				if device in self.connected_sources:
					self.connected_sources.remove(device)

			elif value == "playing":
				try:
					m = self.loaded_modules[device]
					def on_loaded(m):
						SourceRedirector(m.id, device, self.pulse_utils)
						m.disconnect(sig)
					
					if not m.id:
						sig = m.connect("loaded", on_loaded)
					else:
						SourceRedirector(m.id, device, self.pulse_utils)
					
				except Exception, e:
					dprint(e)
				
		
	def on_sink_prop_change(self, key, value, device):
		if key == "Connected" and value:
			if not device in self.connected_sinks:
				self.connected_sinks.append(device)
				gobject.timeout_add(500, self.setup_pa, device, "a2dp")
		
		elif key == "Connected" and not value:
			self.connected_sinks.remove(device)
			self.try_unload_module(device)
		
	def on_hsp_prop_change(self, key, value, device):
		if key == "Connected" and value:
			if not device in self.connected_hs:
				self.connected_hs.append(device)
				self.self.setup_pa(device, "hsp")
		
		elif key == "Connected" and not value:
			self.try_unload_module(device)
			if device in self.connected_hs:
				self.connected_hs.remove(device)
			
	def move_pa_streams(self, sink_id):
		def inputs_cb(inputs):
			for k, v in inputs.iteritems():
				dprint("moving stream", v["name"], "to sink", sink_id)
				self.pulse_utils.MoveSinkInput(k, sink_id, None)
		
		self.pulse_utils.ListSinkInputs(inputs_cb)
				
	def setup_pa_sinks(self, module_id):
		dprint("module", module_id)
		
		def sinks_cb(sinks):
			for k, v in sinks.iteritems():
				if v["owner_module"] == module_id:
					if self.get_option("make_default_sink"):
						dprint("Making sink", v["name"], "the default")
						self.pulse_utils.SetDefaultSink(v["name"], None)
					if self.get_option("move_streams"):
						self.move_pa_streams(k)
					
		
		self.pulse_utils.ListSinks(sinks_cb)
		
	def setup_pa(self, device_path, profile):
		device = BluezDevice(device_path)
		props = device.GetProperties()
		
		def load_cb(res):
			dprint("Load result", res)

			if res < 0:
				Notification(_("Bluetooth Audio"), 
							 _("Failed to initialize PulseAudio Bluetooth module. Bluetooth audio over PulseAudio will not work."), 
							 pixbuf=get_notification_icon("gtk-dialog-error"), 
							 status_icon=self.Applet.Plugins.StatusIcon)				
			else:
				Notification(_("Bluetooth Audio"), 
							 _("Successfully connected to a Bluetooth audio device. This device will now be available in the PulseAudio mixer"), 
							 pixbuf=get_notification_icon("audio-card"), 
							 status_icon=self.Applet.Plugins.StatusIcon)	
				if profile == "a2dp":			 
					self.setup_pa_sinks(res)
							 	
		if int(self.pulse_utils.GetVersion().split(".")[2]) >= 18:
			args = "address=%s profile=%s sink_properties=device.icon_name=blueman card_properties=device.icon_name=blueman"
		else:
			args = "address=%s profile=%s"

		self.load_module(device_path, args % (props["Address"], profile), load_cb)
		
		
		

# Copyright (C) 2009 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2009 Tadas Dailyda <tadas at dailyda dot com>
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

from blueman.plugins.ConfigPlugin import ConfigPlugin
from gi.repository import Gio, Glib

BLUEMAN_PATH = "/org/blueman"
BASE_KEY = "org.blueman"

class GSettings(ConfigPlugin):
	__priority__ = 0
	__plugin__ = "GSettings"

	def on_load(self, schema, path = ""):
		self.schema = schema
		if self.schema != "":
			self.schema = "/" + self.schema

		self.path = path
		if self.path != ""
			self.path = "." + self.path
		        self.settings = Gio.Settings.new_with_path(BASE_KEY + self.path, BLUEMAN_PATH + self.schema)
                else
                        self.settings = Gio.Settings.new(BLUEMAN_PATH + self.schema)

		self.settings.connect("changed", self.value_changed)

	# convert a GVariant to Python native value
	def gval2pyval(self, val):
		valtype = Glib.Variant.g_variant_get_type(val)
		if Glib.Variant.g_variant_type_equal(valtype, Glib.Variant.G_VARIANT_TYPE_STRING):
			return Glib.Variant.g_variant_get_string(val)
		elif Glib.Variant.g_variant_type_equal(valtype, Glib.Variant.G_VARIANT_TYPE_FLOAT):
			return Glib.Variant.g_variant_get_double(val)
		elif Glib.Variant.g_variant_type_equal(valtype, Glib.Variant.G_VARIANT_TYPE_INT):
			return Glib.Variant.g_variant_get_int32(val)
		elif Glib.Variant.g_variant_type_equal(valtype, Glib.Variant.G_VARIANT_TYPE_BOOLEAN):
			return Glib.Variant.g_variant_get_boolean(val)
		elif Glib.Variant.g_variant_type_equal(valtype, Glib.Variant.G_VARIANT_TYPE_ARRAY):
			x = []
			array = []
			Glib.Variant.g_variant_get(val, 'a', array):
			for item in array:
				x.append(self.gval2pyval(item))
			return x
		else:
			raise AttributeError("Cant get this type from GSettings: %s" % str(val.type))

	def value_changed(self, client, key, value):
		if Gio.Settings.g_settings_is_writable(self.settings,key):
			self.emit("property-changed", key, self.get(name))

	def set(self, key, value):
		func = None

		if type(value) == str:
			func = Gio.Settings.g_settings_set_string
		elif type(value) == int:
			func = Gio.Settings.g_settings_set_int
		elif type(value) == bool:
			func = Gio.Settings.g_settings_set_bool
		elif type(value) == float:
			func = Gio.Settings.g_settings_set_double
		elif type(value) == list:
			func = Gio.Settings.g_settings_set_value
		else:
			raise AttributeError("Cant set this type in GSettings: %s" % str(type(value)))

		func(self.settings, key, value)
		Gio.Settings.g_settings_apply(self.settings)

	def get(self, key):
		val = Gio.Settings.g_settings_get_val(self.settings,key)
		if val != None:
			return self.gval2pyval(val)
		else:
			return None

	def list_dirs(self):
		rets = Gio.Settings.g_settings_list_keys(self.settings)
		l = []
		for r in rets:
			l.append(r)

		return l

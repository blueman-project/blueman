/* -*- Mode: C; tab-width: 8; indent-tabs-mode: t; c-basic-offset: 8 -*- */

/*
 * Copyright (C) 2010 Valmantas Palikša
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more av.
 *
 * You should have received a copy of the GNU General Public
 * License along with this program; if not, write to the
 * Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301  USA.
 */

#include <config.h>
#include "Python.h"
#include <pygobject.h>

#include <glib/gi18n-lib.h>
#include <gtk/gtk.h>


#include <nautilus-sendto-plugin.h>

PyObject* self = NULL;
PyObject* module = NULL;
PyObject* gobject = NULL;

GtkWidget* combo = NULL;


static gboolean
init (NstPlugin *plugin)
{
	Py_Initialize();

	gobject = pygobject_init(2,1,0);

	module = PyImport_ImportModule("blueman.gui.NstBluetooth");
	if(!module) {
		PyErr_Print();
		return FALSE;
	}

	PyObject* class = PyObject_GetAttrString(module, "NstBluetooth");
	if(!class) {
		PyErr_Print();
		return FALSE;
	}

	Py_DECREF(class);

	self = PyInstance_New(class, NULL, NULL);
	if(!self) {
		PyErr_Print();
		return FALSE;
	}

	return PyInstance_Check(self);
}


static GtkWidget*
get_contacts_widget (NstPlugin *plugin)
{
	PyObject* result = PyObject_CallMethod(self, "get_contacts_widget", NULL);
	if(!result) {
		PyErr_Print();
		return NULL;
	}
		

	GtkWidget* res = ((PyGObject*)result)->obj;
	combo = res;

	g_object_ref(combo);


	Py_XDECREF(result);

	return combo;
}


static gboolean
send_files (NstPlugin *plugin,
	    GtkWidget *contact_widget,
	    GList *file_list)
{
	GList* node = file_list;

	PyObject* list = PyList_New(0);

	while(node) {
		char* filename = node->data;
		g_assert(filename != NULL);
		
		PyObject* str = PyString_FromString(filename);
		PyList_Append(list, str);
		Py_XDECREF(str);
		
		node = node->next;
	}

	PyObject* result = PyObject_CallMethod(self, "send_files", "O", list);
	if(!result) {
		PyErr_Print();
		return FALSE;
	}
	Py_DECREF(list);
	
	if(result == Py_None || result == Py_False) {
		Py_DECREF(result);
		return FALSE;
	}
	Py_DECREF(result);
	return TRUE;
}

static gboolean
validate_destination (NstPlugin *plugin,
		      GtkWidget *contact_widget,
		      char **error)
{
	return TRUE;
}

static gboolean
destroy (NstPlugin *plugin)
{
	g_object_unref(combo);
	combo = NULL;
	Py_Finalize();
	return TRUE;
}

static
NstPluginInfo plugin_info = {
	"blueman",
	"blueman",
	"Bluetooth (OBEX Push)",
	GETTEXT_PACKAGE,
	NAUTILUS_CAPS_NONE,
	init,
	get_contacts_widget,
	validate_destination,
	send_files,
	destroy
};

NST_INIT_PLUGIN (plugin_info)

/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Library General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA
 */
 
#pragma once

#include <Python.h>

#define MODEM_CAP_GSM         0x0001 /* GSM */
#define MODEM_CAP_IS707_A     0x0002 /* CDMA Circuit Switched Data */
#define MODEM_CAP_IS707_P     0x0004 /* CDMA Packet Switched Data */
#define MODEM_CAP_DS          0x0008 /* Data compression selection (v.42bis) */
#define MODEM_CAP_ES          0x0010 /* Error control selection (v.42) */
#define MODEM_CAP_FCLASS      0x0020 /* Group III Fax */
#define MODEM_CAP_MS          0x0040 /* Modulation selection */
#define MODEM_CAP_W           0x0080 /* Wireless commands */      
#define MODEM_CAP_IS856       0x0100 /* CDMA 3G EVDO rev 0 */
#define MODEM_CAP_IS856_A     0x0200 /* CDMA 3G EVDO rev A */ 

void probe_modem(char* device, PyObject* callback);
void set_probe_debug(gboolean);

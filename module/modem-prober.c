/*
 * modem_caps - probe Hayes-compatible modem capabilities
 *
 * Copyright (C) 2008 Dan Williams <dcbw@redhat.com>
 * Modifications by: Valmantas Palikša
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details:
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE 1
#endif

#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <getopt.h>
#include <time.h>

#include <glib.h>
#include <Python.h>

#include "modem-prober.h"

#if PY_MAJOR_VERSION >= 3
#define PyString_FromString PyUnicode_FromString
#endif

static gboolean verbose = FALSE;

void set_probe_debug(gboolean debug) {
	verbose = debug;
}

struct modem_caps {
	char *name;
	guint32 bits;
};

static struct modem_caps modem_caps[] = {
	{"+CGSM",     MODEM_CAP_GSM},
	{"+CIS707-A", MODEM_CAP_IS707_A},
	{"+CIS707",   MODEM_CAP_IS707_A},
	{"CIS707",    MODEM_CAP_IS707_A}, /* Qualcomm Gobi */
	{"+CIS707P",  MODEM_CAP_IS707_P},
	{"CIS-856",   MODEM_CAP_IS856},
	{"CIS-856-A", MODEM_CAP_IS856_A},
	{"CIS-856A",  MODEM_CAP_IS856_A}, /* Kyocera KPC680 */
	{"+DS",       MODEM_CAP_DS},
	{"+ES",       MODEM_CAP_ES},
	{"+MS",       MODEM_CAP_MS},
	{"+FCLASS",   MODEM_CAP_FCLASS},
	{NULL}
};

#define verbose(fmt, args...) \
if (verbose) { \
	g_print ("%s(): " fmt "\n", G_STRFUNC, ##args); \
}

static gboolean
modem_send_command (int fd, const char *cmd)
{
	int eagain_count = 1000;
	guint32 i;
	ssize_t written;

	verbose ("Sending: '%s'", cmd);

	for (i = 0; i < strlen (cmd) && eagain_count > 0;) {
		written = write (fd, cmd + i, 1);

		if (written > 0)
			i += written;
		else {
			/* Treat written == 0 as EAGAIN to ensure we break out of the
			 * for() loop eventually.
			 */
			if ((written < 0) && (errno != EAGAIN)) {
				g_printerr ("error writing command: %d\n", errno);
				return FALSE;
			}
			eagain_count--;
			g_usleep (G_USEC_PER_SEC / 10000);
		}
	}

	return eagain_count <= 0 ? FALSE : TRUE;
}

static int
find_terminator (const char *line, const char **terminators)
{
	int i;

	for (i = 0; terminators[i]; i++) {
		if (!strncasecmp (line, terminators[i], strlen (terminators[i])))
			return i;
	}
	return -1;
}

static const char *
find_response (const char *line, const char **responses, int *idx)
{
	int i;

	/* Don't look for a result again if we got one previously */
	for (i = 0; responses[i]; i++) {
		if (strstr (line, responses[i])) {
			*idx = i;
			return line;
		}
	}
	return NULL;
}

#define RESPONSE_LINE_MAX 128
#define SERIAL_BUF_SIZE 2048

/* Return values:
 *
 * -2:    timeout
 * -1:    read error or response not found
 * 0...N: response index in **needles array
 */
static int
modem_wait_reply (int fd,
                  guint32 timeout_secs,
                  const char **needles,
                  const char **terminators,
                  int *out_terminator,
                  char **out_response)
{
	char buf[SERIAL_BUF_SIZE + 1];
	int reply_index = -1, bytes_read;
	GString *result = g_string_sized_new (RESPONSE_LINE_MAX * 2);
	time_t end;
	const char *response = NULL;
	gboolean done = FALSE;

	*out_terminator = -1;
	end = time (NULL) + timeout_secs;
	do {
		bytes_read = read (fd, buf, SERIAL_BUF_SIZE);
		if (bytes_read < 0 && errno != EAGAIN) {
			g_string_free (result, TRUE);
			g_printerr ("read error: %d\n", errno);
			return -1;
		}

		if (bytes_read == 0)
			break; /* EOF */
		else if (bytes_read > 0) {
			char **lines, **iter, *tmp;

			buf[bytes_read] = 0;
			g_string_append (result, buf);

			verbose ("Got: '%s'", result->str);

			lines = g_strsplit_set (result->str, "\n\r", 0);

			/* Find response terminators */
			for (iter = lines; *iter && !done; iter++) {
				tmp = g_strstrip (*iter);
				if (tmp && strlen (tmp)) {
					*out_terminator = find_terminator (tmp, terminators);
					if (*out_terminator >= 0)
						done = TRUE;
				}
			}

			/* If the terminator is found, look for expected responses */
			if (done) {
				for (iter = lines; *iter && (reply_index < 0); iter++) {
					tmp = g_strstrip (*iter);
					if (tmp && strlen (tmp)) {
						response = find_response (tmp, needles, &reply_index);
						if (response) {
							g_free (*out_response);
							*out_response = g_strdup (response);
						}
					}
				}
			}
			g_strfreev (lines);
		}

		if (!done)
			g_usleep (1000);
	} while (!done && (time (NULL) < end) && (result->len <= SERIAL_BUF_SIZE));

	/* Handle timeout */
	if (*out_terminator < 0 && !*out_response)
		reply_index = -2;

	g_string_free (result, TRUE);
	return reply_index;
}

#define GCAP_TAG "+GCAP:"
#define GMM_TAG "+GMM:"

static int
parse_gcap (const char *buf)
{
	const char *p = buf + strlen (GCAP_TAG);
	char **caps, **iter;
	int ret = 0;

	caps = g_strsplit_set (p, " ,\t", 0);
	if (!caps)
		return 0;

	for (iter = caps; *iter; iter++) {
		struct modem_caps *cap = modem_caps;

		while (cap->name) {
			if (!strcmp(cap->name, *iter)) {
				ret |= cap->bits;
				break;
			}
			cap++;
		}
	}

	g_strfreev (caps);
	return ret;
}

static int
parse_gmm (const char *buf)
{
	const char *p = buf + strlen (GMM_TAG);
	char **gmm, **iter;
	gboolean gsm = FALSE;

	gmm = g_strsplit_set (p, " ,\t", 0);
	if (!gmm)
		return 0;

	/* BUSlink SCWi275u USB GPRS modem */
	for (iter = gmm; *iter && !gsm; iter++) {
		if (strstr (*iter, "GSM900") || strstr (*iter, "GSM1800") ||
		    strstr (*iter, "GSM1900") || strstr (*iter, "GSM850"))
			gsm = TRUE;
	}

	g_strfreev (gmm);
	return gsm ? MODEM_CAP_GSM : 0;
}

static int
g_timeval_subtract (GTimeVal *result, GTimeVal *x, GTimeVal *y)
{
	int nsec;

	/* Perform the carry for the later subtraction by updating y. */
	if (x->tv_usec < y->tv_usec) {
		nsec = (y->tv_usec - x->tv_usec) / G_USEC_PER_SEC + 1;
		y->tv_usec -= G_USEC_PER_SEC * nsec;
		y->tv_sec += nsec;
	}
	if (x->tv_usec - y->tv_usec > G_USEC_PER_SEC) {
		nsec = (x->tv_usec - y->tv_usec) / G_USEC_PER_SEC;
		y->tv_usec += G_USEC_PER_SEC * nsec;
		y->tv_sec -= nsec;
	}

	/* Compute the time remaining to wait.
	   tv_usec is certainly positive. */
	result->tv_sec = x->tv_sec - y->tv_sec;
	result->tv_usec = x->tv_usec - y->tv_usec;

	/* Return 1 if result is negative. */
	return x->tv_sec < y->tv_sec;
}

static int modem_probe_caps(int fd, glong timeout_ms)
{
	const char *gcap_responses[] = { GCAP_TAG, NULL };
	const char *terminators[] = { "OK", "ERROR", "ERR", "+CME ERROR", NULL };
	char *reply = NULL;
	int idx = -1, term_idx = -1, ret = 0;
	gboolean try_ati = FALSE;
	GTimeVal start, end;
	gboolean send_success;

	/* If a delay was specified, start a bit later */
	if (timeout_ms > 500) {
		g_usleep (500000);
		timeout_ms -= 500;
	}

	/* Standard response timeout case */
	timeout_ms += 3000;

	while (timeout_ms > 0) {
		GTimeVal diff;
		gulong sleep_time = 100000;

		g_get_current_time (&start);

		idx = term_idx = 0;
		send_success = modem_send_command (fd, "AT+GCAP\r\n");
		if (send_success)
			idx = modem_wait_reply (fd, 2, gcap_responses, terminators, &term_idx, &reply);
		else
			sleep_time = 300000;

		g_get_current_time (&end);
		g_timeval_subtract (&diff, &end, &start);
		timeout_ms -= (diff.tv_sec * 1000) + (diff.tv_usec / 1000);

		if (send_success) {
			if (0 == term_idx && 0 == idx) {
				/* Success */
				verbose ("GCAP response: %s", reply);
				ret = parse_gcap (reply);
				break;
			} else if (0 == term_idx && -1 == idx) {
				/* Just returned "OK" but no GCAP (Sierra) */
				try_ati = TRUE;
				break;
			} else if (3 == term_idx && -1 == idx) {
				/* No SIM (Huawei) */
				try_ati = TRUE;
				break;
			} else if (1 == term_idx || 2 == term_idx) {
				try_ati = TRUE;
			} else
				verbose ("timed out waiting for GCAP reply (idx %d, term_idx %d)", idx, term_idx);
			g_free (reply);
			reply = NULL;
		}

		g_usleep (sleep_time);
		timeout_ms -= sleep_time / 1000;
	}

	if (!ret && try_ati) {
		const char *ati_responses[] = { GCAP_TAG, NULL };

		/* Many cards (ex Sierra 860 & 875) won't accept AT+GCAP but
		 * accept ATI when the SIM is missing.  Often the GCAP info is
		 * in the ATI response too.
		 */
		g_free (reply);
		reply = NULL;

		verbose ("GCAP failed, trying ATI...");
		if (modem_send_command (fd, "ATI\r\n")) {
			idx = modem_wait_reply (fd, 3, ati_responses, terminators, &term_idx, &reply);
			if (0 == term_idx && 0 == idx) {
				verbose ("ATI response: %s", reply);
				ret = parse_gcap (reply);
			}
		}
	}

	g_free (reply);
	reply = NULL;

	/* Try an alternate method on some hardware (ex BUSlink SCWi275u) */
	if ((idx != -2) && !(ret & MODEM_CAP_GSM) && !(ret & MODEM_CAP_IS707_A)) {
		const char *gmm_responses[] = { GMM_TAG, NULL };

		if (modem_send_command (fd, "AT+GMM\r\n")) {
			idx = modem_wait_reply (fd, 5, gmm_responses, terminators, &term_idx, &reply);
			if (0 == term_idx && 0 == idx) {
				verbose ("GMM response: %s", reply);
				ret |= parse_gmm (reply);
			}
			g_free (reply);
		}
	}

	return ret;
}


struct thread_info {
	char* device;
	int caps;
	PyObject* callback;
};

static gboolean on_finished(gpointer data) {
	struct thread_info* info = data;
	if(PyCallable_Check(info->callback)) {
		PyObject* args, *rslt;
		
		if (info->caps < 0) {
			args = Py_BuildValue("(O)", Py_None);
			
		} else {
			PyObject* name;
			PyObject* caps = PyList_New(0);
			if (info->caps & MODEM_CAP_GSM) {
				name = PyString_FromString("GSM-07.07");
				PyList_Append(caps, name);
				Py_XDECREF(name);
			
				name = PyString_FromString("GSM-07.05");
				PyList_Append(caps, name);
				Py_XDECREF(name);
			}
			if (info->caps & MODEM_CAP_IS707_A) {
				name = PyString_FromString("IS-707-A");
				PyList_Append(caps, name);
				Py_XDECREF(name);
			}
			if (info->caps & MODEM_CAP_IS707_P) {
				name = PyString_FromString("IS-707-P");
				PyList_Append(caps, name);
				Py_XDECREF(name);
			}
			if (info->caps & MODEM_CAP_IS856) {
				name = PyString_FromString("IS-856");
				PyList_Append(caps, name);
				Py_XDECREF(name);
			}	
			if (info->caps & MODEM_CAP_IS856_A) {
				name = PyString_FromString("IS-856-A");
				PyList_Append(caps, name);
				Py_XDECREF(name);
			}	
			args = Py_BuildValue("(O)", caps);
			Py_XDECREF(caps);
		}
		rslt = PyObject_CallObject(info->callback, args);
		if(!rslt) {
			PyErr_PrintEx(0);		
		}
		
		Py_XDECREF(rslt);
		Py_XDECREF(args);
	}
	Py_DECREF(info->callback);
	g_free(info->device);
	g_free(info);

	return FALSE;
}

static gpointer do_probe(gpointer data) {
	struct thread_info* info = (struct thread_info*)data;
	char* device = info->device;

	struct termios orig, attrs;
	int fd, caps;
	
	if (device == NULL) {
		goto error;
	}

	fd = open (device, O_RDWR | O_EXCL | O_NONBLOCK);
	if (fd < 0) {
		//g_warning ("open(%s) failed: %d\n", device, errno);
		goto error;
	}

	if (tcgetattr (fd, &orig)) {
		//g_warning ("tcgetattr(%s): failed %d\n", device, errno);
		goto error;
	}

	memcpy (&attrs, &orig, sizeof (attrs));
	attrs.c_iflag &= ~(IGNCR | ICRNL | IUCLC | INPCK | IXON | IXANY | IGNPAR);
	attrs.c_oflag &= ~(OPOST | OLCUC | OCRNL | ONLCR | ONLRET);
	attrs.c_lflag &= ~(ICANON | XCASE | ECHO | ECHOE | ECHONL);
	attrs.c_lflag &= ~(ECHO | ECHOE);
	attrs.c_cc[VMIN] = 1;
	attrs.c_cc[VTIME] = 0;
	attrs.c_cc[VEOF] = 1;

	attrs.c_cflag &= ~(CBAUD | CSIZE | CSTOPB | CLOCAL | PARENB);
	attrs.c_cflag |= (B9600 | CS8 | CREAD | PARENB);
	
	tcsetattr (fd, TCSANOW, &attrs);
	caps = modem_probe_caps (fd, 0);
	tcsetattr (fd, TCSANOW, &orig);
	
	close(fd);

	info->caps = caps;
	g_idle_add(on_finished, info);
	
	return NULL;

error:
	info->caps = -1;
	g_idle_add(on_finished, info);
	if(fd > 0)
		close(fd);
	
	return NULL;
}

void probe_modem(char* device, PyObject* callback) {
	struct thread_info* info = g_new0(struct thread_info, 1);
	info->device = g_strdup(device);
	info->callback = callback;
	Py_INCREF(callback);
	g_thread_new("probe modem", do_probe, info);
}

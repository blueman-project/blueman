# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
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

import glib
import tty
import termios
import os
import subprocess
import gobject
import re

pppd_errors = {}
pppd_errors[1] = """An immediately fatal error of some kind  occurred, such as an essential system call failing, or running out of virtual memory."""
pppd_errors[2] = """An  error  was detected in processing the options given, such as two mutually exclusive options being used."""
pppd_errors[3] = """Pppd is not setuid-root and the invoking user is not root."""
pppd_errors[4] = """The kernel does not support PPP, for example, the  PPP kernel driver is not included or cannot be loaded."""
pppd_errors[5] = """Pppd terminated because it was sent a SIGINT, SIGTERM or SIGHUP signal."""
pppd_errors[6] = """The serial port could not be locked."""
pppd_errors[7] = """The serial port could not be opened."""
pppd_errors[8] = """The connect script failed (returned a non-zero exit status)."""
pppd_errors[9] = """The command specified as the argument to the  pty  option  could not be run."""
pppd_errors[10] = """The PPP negotiation failed, that is, it didn't reach the point where at least one network protocol (e.g. IP) was running."""
pppd_errors[11] = """The peer system failed (or refused) to authenticate itself."""
pppd_errors[12] = """The link was established successfully and terminated because  it was idle."""
pppd_errors[13] = """The link was established successfully and terminated because the connect time limit was reached."""
pppd_errors[14] = """Callback was negotiated  and  an  incoming  call  should  arrive shortly."""
pppd_errors[15] = """The link was terminated because the peer is not responding to echo requests."""
pppd_errors[16] = """The link was terminated by the modem hanging up."""
pppd_errors[17] = """The PPP negotiation failed because serial loopback was detected."""
pppd_errors[18] = """The init script failed (returned a non-zero exit status)."""
pppd_errors[19] = """We failed to authenticate ourselves to the peer."""


class PPPException(Exception):
	pass

class PPPConnection(gobject.GObject):
	__gsignals__ = {
		#arg: interface name eg. ppp0
		'connected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'error-occurred' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),

	}
	def __init__(self, port, number="*99#", apn="", user="", pwd=""):
		gobject.GObject.__init__(self)
		
		self.apn = apn
		self.number = number
		self.user = user
		self.pwd = pwd
		self.port = port
		self.interface = None
		
		self.pppd = None
		self.file = None
		
	def Connect(self):

		self.event = 1

		def common_callback(res, exception):
			if exception:
				self.emit("error-occurred", str(exception))
				
			elif self.event == 1:
				self.send_command("ATZ")
				self.wait_for_reply(common_callback, ["OK", "ERROR"])					

				
			elif self.event == 2:
				self.send_command("ATE1")
				self.wait_for_reply(common_callback)				
			
			elif self.event == 3:
				self.send_command("AT+GCAP")
				self.wait_for_reply(common_callback)				
			
			elif self.event == 4:
				if self.apn != "":
					self.send_command("AT+CGDCONT=1, \"IP\",\"%s\"" % self.apn)
					self.wait_for_reply(common_callback, ["OK", "ERROR", "ERR"])
				else:
					self.event+=1
					common_callback(None, None)
					return
			
			elif self.event == 5:
				self.send_command("ATD%s" % self.number)
				self.wait_for_reply(common_callback, ["CONNECT", "NO CARRIER", "BUSY", "NO ANSWER", "NO DIALTONE", "OK", "ERR", "ERROR"])
				
			elif self.event == 6:
				print "Starting pppd"
				self.pppd = subprocess.Popen(["/usr/sbin/pppd", "%s" % self.port, "defaultroute", "updetach", "usepeerdns"], bufsize=1, stdout=subprocess.PIPE)
				glib.io_add_watch(self.pppd.stdout, glib.IO_IN | glib.IO_ERR | glib.IO_HUP, self.on_pppd_stdout)
				glib.timeout_add(1000, self.check_pppd)				
				
				os.close(self.file)	
				
			
			self.event+=1
			
		self.file = os.open(self.port, os.O_RDWR | os.O_EXCL | os.O_NONBLOCK)
		tty.setraw(self.file)
		
		attrs = termios.tcgetattr(self.file)
		
		attrs[0] &= ~(termios.IGNCR | termios.ICRNL | termios.IUCLC | termios.INPCK | termios.IXON | termios.IXANY | termios.IGNPAR)
		attrs[1] &= ~(termios.OPOST | termios.OLCUC | termios.OCRNL | termios.ONLCR | termios.ONLRET)
		attrs[3] &= ~(termios.ICANON | termios.XCASE | termios.ECHO | termios.ECHOE | termios.ECHONL)
		attrs[3] &= ~(termios.ECHO | termios.ECHOE)
		attrs[6][termios.VMIN] = 1
		attrs[6][termios.VTIME] = 0
		attrs[6][termios.VEOF] = 1

		attrs[2] &= ~(termios.CBAUD | termios.CSIZE | termios.CSTOPB | termios.CLOCAL | termios.PARENB)
		attrs[2] |= (termios.B9600 | termios.CS8 | termios.CREAD | termios.PARENB)
		
		termios.tcsetattr(self.file, termios.TCSANOW, attrs)
		
		termios.tcflush(self.file, termios.TCIOFLUSH)
		
		self.send_command("AT")
		self.wait_for_reply(common_callback)	
		
	def on_pppd_stdout(self, source, cond):
		if cond & glib.IO_ERR or cond & glib.IO_HUP:
			return False

		line = source.readline()	
		m = re.match("Using interface (ppp[0-9]*)", line)
		if m:
			self.interface = m.groups(1)[0]
		
		print line
	
		return True
	
	def check_pppd(self):
		status = self.pppd.poll()	
		if status != None:
			if status == 0:
				self.emit("connected", self.interface)
			else:
				try:
					msg = "pppd exited: " + pppd_errors[int(status)]
				except KeyError:
					msg = "pppd exited with unknown error"
					
				self.emit("error-occurred", msg)
				
			print "pppd exited with status %d" % status
			return False
		return True

	def send_command(self, command):
		print "-->", command
		os.write(self.file, "%s\r\n" % command)
		termios.tcdrain(self.file)
		
	def on_data_ready(self, source, condition, terminators, on_done):
		if condition & glib.IO_ERR or condition & glib.IO_HUP:
			on_done(None, PPPException("Socket error"))
			return False

		self.buffer += os.read(self.file, 128)

		if self.buffer.endswith("\r\n"):
			for t in terminators:
				if t in self.buffer:
					self.term_found = True
					break;	

		
		if self.term_found:
			a = self.buffer.replace("\n", "\\n").replace("\r", "\\r")
			print "<-- \"", a, "\""	
			
			
			lines = self.buffer.split("\r\n")
			for l in lines:
				if l == "":
					lines.remove(l)

			on_done(lines, None)
			return False		
			
		return True
		
	def wait_for_reply(self, callback, terminators=["OK", "ERROR"]):
		def on_timeout():
			glib.source_remove(self.io_watch)
			callback(None, PPPException("Modem initialization timed out"))

			return False
			
			
		def on_done(ret, exception):
			glib.source_remove(self.timeout)
			callback(ret, exception)
			
		
		self.buffer = ""
		self.term_found = False
				
		self.io_watch = glib.io_add_watch(self.file, glib.IO_IN | glib.IO_ERR | glib.IO_HUP, self.on_data_ready, terminators, on_done)
		self.timeout = glib.timeout_add(15000, on_timeout)




		

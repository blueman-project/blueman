#
#
# dhcpconf.py
# (c) 2007 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#


import os
import re
import commands
from blueman.Constants import *
from blueman.Lib import create_bridge, destroy_bridge, BridgeException
import re
from commands import getstatusoutput
import dbus

def ip_chk(ip_str):
   pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
   r = re.match(pattern, ip_str)
   if r:
      return r.groups(1)
   else:
      return False
      
def netstatus():
	dhcp=0
	ip="0"
	masq=0
	type=0
	
	try:
		path = os.path.join( PREFIX, "bin/blueman-ifup")
		f=open(path)
		for line in f:
			m = re.match("^MASQ=(.*)", line)
			if m:
				masq = int(m.groups(1)[0])
		
			m = re.match("^DHCP=(.*)", line)
			if m:
				dhcp = int(m.groups(1)[0])
		
			m = re.match("^IP=(.*)", line)
			if m:
				ip = m.groups(1)[0]
		
			m = re.match("^TYPE=(.*)", line)
			if m:
				type = m.groups(1)[0]
			
		f.close()
	except IOError:
		pass
			
	return {"dhcp":dhcp, "ip":ip, "masq":masq, "type":type}
	
def nc_is_running():
	if os.path.exists("/var/run/blueman-dh-lock") or os.path.exists("/var/run/blueman-iptbl-lock"):
		return True
	else:
		return False


def have(t):
	cmd = "whereis %s" % t
	out = commands.getoutput(cmd)
	s = out.split(":")
	if len(s[1]) > 0:
		return True
	else:
		return False


class NetConf:
	def __init__(self, ipaddress, allow_nat = True, subnet = "255.255.255.0"):
		self.ip_address = ipaddress
		if ipaddress != None:
			self._ip_address_seg = re.match("(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", self.ip_address).groups(1)
		
			self._subnet_seg = re.match("(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", subnet).groups(1)
		

			self.ip_range_start = "%s.%s.%s.%s" % (self._ip_address_seg[0], self._ip_address_seg[1], self._ip_address_seg[2], int(self._ip_address_seg[3])+1)
			self.ip_range_end = "%s.%s.%s.254" % (self._ip_address_seg[0], self._ip_address_seg[1], self._ip_address_seg[2])
			self.ip_range_mask = "%s.%s.%s.0" % (self._ip_address_seg[0], self._ip_address_seg[1], self._ip_address_seg[2])
		
			self.allow_nat = allow_nat
			self.subnet = subnet
			
			self.server_type = self.get_type()
		
	##virtual funcs
	def get_dhcp_exec_config(self):
		raise Exception, "netconf::get_dhcp_exec_config() not overridden"
		#return ("dhcpd3", "args")
		
	def on_install(self):
		pass
		
	def on_uninstall(self):
		pass	
		
	def get_type(self):
		return None
	##/virtual funcs		
	
	
	def install(self):
		if self.ip_address == None:
			raise Exception, "netconf::install(): NULL ip address, cannot install"
			
		self._install_ifup()
		self.on_install()
		
		self.reload_settings()
		
	def uninstall(self):	
		self._uninstall_ifup()
		self._kill_dhcp()
		self._restore_iptables()
		try:
			destroy_bridge()
		except BridgeException, msg:
			dprint("Unable to destroy bridge:", msg)

	def reload_settings(self):
		self._kill_dhcp()
		self._restore_iptables()
		
		try:
			create_bridge()
		except BridgeException, msg:
			dprint("Unable to create bridge:", msg)
		
		self._execute_ifup()

		

	def _execute_ifup(self):		
		status = getstatusoutput("blueman-ifup pan1")
		if status[0] > 0:
			raise Exception, status[1]

		
	def _restore_iptables(self):
		if os.path.exists("/var/run/blueman-iptbl-lock"):
			f = open("/var/run/blueman-iptbl-lock")
			lines = []
			for line in f:
				lines.append(line)
			f.close()
			os.system("rm -f /var/run/blueman-iptbl-lock")
			
			for l in lines:
				os.system("iptables %s" % l)
			
			
			
			
	def _kill_dhcp(self):
		if os.path.exists("/var/run/blueman-dh-lock"):
			os.system("cat /var/run/blueman-dh-lock | xargs kill")
			os.system("rm -f /var/run/blueman-dh-lock")
	
		
	def _uninstall_ifup(self):
 		path = os.path.join( PREFIX, "bin/blueman-ifup")
 		f = open(path, "w");
 		f.write("#!/bin/bash\n")
 		f.write("MASQ=0\nIP=0\nDHCP=0\n\nif [ \"$1\" == \"pan0\" ]; then\n\tavahi-autoipd $1\nfi""")
 		f.close()
 		
 	def _install_ifup(self):
 		path = os.path.join( PREFIX, "bin/blueman-ifup")
 		f = open( path, "w" )
 		ifup = self._generate_ifup()
 		f.write(ifup)
 		f.close()
 		os.chmod(path, 0755)
 		
 					
	def _generate_ifup(self):
		dhserver, dh_args = self.get_dhcp_exec_config()
		
		ifup_script = """#!/bin/bash
#this script is generated automatically by blueman, for your own good, do not edit :)
MASQ=%s 
IP=%s
DHCP=1
TYPE=%s
PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin

if [ "$1" == "pan0" ]; then
	avahi-autoipd $1
fi

if [ "$1" == "pan1" ]; then
	python -c "from blueman.Lib import create_bridge; create_bridge('pan1')"

	ifconfig pan1 %s netmask 255.255.255.0 up || exit 1

	if ! [ -a /var/run/blueman-iptbl-lock ]; then
		
		if [ "$MASQ" == "1" ]; then
			echo 1 > /proc/sys/net/ipv4/ip_forward
			echo 1 | tee /proc/sys/net/ipv4/conf/*/forwarding
			
			rule="-s %s/255.255.255.0 -j MASQUERADE"
			iptables -t nat -A POSTROUTING $rule
			echo -t nat -D POSTROUTING $rule > /var/run/blueman-iptbl-lock
			
			iptables -t filter -I FORWARD -i pan1 -j ACCEPT
			echo -t filter -D FORWARD -i pan1 -j ACCEPT >> /var/run/blueman-iptbl-lock
			
			iptables -t filter -I FORWARD -o pan1 -j ACCEPT
			echo -t filter -D FORWARD -o pan1 -j ACCEPT >> /var/run/blueman-iptbl-lock
			
			iptables -t filter -I INPUT -i pan1 -j ACCEPT
			echo -t filter -D INPUT -i pan1 -j ACCEPT >> /var/run/blueman-iptbl-lock
		fi
	fi
	if ! [ -a /var/run/blueman-dh-lock ]; then
		%s %s || exit 1
		PID=`pidof -s -o %%PPID -x %s`
		echo $PID > /var/run/blueman-dh-lock

	fi
	
fi

""" % ( int(self.allow_nat), self.ip_address, self.server_type, self.ip_address, self.ip_range_mask, dhserver, dh_args, dhserver)
		return ifup_script


class NetConfDhcpd(NetConf):


	def __init__(self, ipaddress, allow_nat = True):
		NetConf.__init__(self, ipaddress, allow_nat)
		
		self.dhcp_config, self.existing_subnet = self._read_dhcp_config()
		


	def get_dhcp_exec_config(self):
		return ("dhcpd3", "pan1")
		
		
	def on_install(self):
		self._setup_dhcpd3()
		
	def on_uninstall(self):
		self._unsetup_dhcpd3()
		
	def get_type(self):
		return "dhcpd"
	
	
	def _read_dhcp_config(self):
		f = open(DHCP_CONFIG_FILE, "r")
		insection = False
		dhcp_config = ""
		existing_subnet = ""
		for line in f:
			if line == "#### BLUEMAN AUTOMAGIC SUBNET ####\n":
				insection = True
				
			if line == "#### END BLUEMAN AUTOMAGIC SUBNET ####\n":
				insection == False
				
			if not insection:
				dhcp_config += line
			else:
				existing_subnet += line
				
		f.close()
		
		return (dhcp_config, existing_subnet)
		

		
		
	
	
	def get_dns_servers(self):
		f = open("/etc/resolv.conf", "r")
		dns_servers = ""
		for line in f:
			server = re.search("^nameserver (.*)", line)
			if server:
				server = server.groups(1)[0]
				dns_servers += "%s, " % server;
			
		dns_servers = dns_servers.strip(", ")
		
		f.close()
		
		return dns_servers
		
	def _generate_subnet_config(self):
		dns = self.get_dns_servers()
		
		subnet = "#### BLUEMAN AUTOMAGIC SUBNET ####\n"
		subnet += "# Everything inside this section is destroyed after config change\n"
		subnet += """subnet %s netmask 255.255.255.0 {
				option domain-name-servers %s;
				option subnet-mask 255.255.255.0;
				%s
				range %s %s;
				}\n""" % (self.ip_range_mask, dns, "option routers %s" % self.ip_address if self.allow_nat else "" , self.ip_range_start, self.ip_range_end)
		
		subnet += "#### END BLUEMAN AUTOMAGIC SUBNET ####\n"
		
		
		return subnet
		

					
	
	def _setup_dhcpd3(self):
		subnet = self._generate_subnet_config()
		
		#if subnet != self.existing_subnet:
		f = open(DHCP_CONFIG_FILE, "w")
		f.write(self.dhcp_config)
		f.write(subnet)
		f.close()


 	
 	def _unsetup_dhcpd3(self):
		f = open(DHCP_CONFIG_FILE, "w")
		f.write(self.dhcp_config)
		f.close()
 	


class NetConfDnsMasq(NetConf):
	def __init__(self, ipaddress, allow_nat = True):
		NetConf.__init__(self, ipaddress, allow_nat)
		
	def get_dhcp_exec_config(self):
		if self.allow_nat:
			rtr = "--dhcp-option=option:router,%s" % self.ip_address
		else:
			rtr = "--dhcp-option=3 --dhcp-option=6" #no route and no dns
		x = ("dnsmasq", "--bind-interfaces --dhcp-range=%s,%s,60m --except-interface=lo --interface=pan1 %s" % (self.ip_range_start, self.ip_range_end, rtr))
		
		return x

	def get_type(self):
		return "dnsmasq"

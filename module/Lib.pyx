#!/usr/bin/python

cdef extern from "malloc.h":
	cdef void free(void *ptr)
	
cdef extern from "string.h":
	cdef char* strerror(int errnum)

cdef extern from "bluetooth/bluetooth.h":
	ctypedef struct bdaddr_t:
		unsigned char b[6]

	int ba2str(bdaddr_t *ba, char *str)
	int str2ba(char *str, bdaddr_t *ba)
	
cdef extern from "bluetooth/hci.h":	
	cdef struct hci_dev_stats:
		unsigned long int err_rx
		unsigned long int err_tx
		unsigned long int cmd_tx
		unsigned long int evt_rx
		unsigned long int acl_tx
		unsigned long int acl_rx
		unsigned long int sco_tx
		unsigned long int sco_rx
		unsigned long int byte_rx
		unsigned long int byte_tx


	cdef struct hci_dev_info:
		unsigned int dev_id
		char name[8]

		bdaddr_t bdaddr

		unsigned long int flags
		unsigned char type

		unsigned char features[8]

		unsigned long int pkt_type
		unsigned long int link_policy
		unsigned long int link_mode

		unsigned int acl_mtu
		unsigned int acl_pkts
		unsigned int sco_mtu
		unsigned int sco_pkts

		hci_dev_stats stat



cdef extern from "bluetooth/hci_lib.h":
	cdef int hci_devinfo(int dev_id, hci_dev_info *di)


cdef extern from "bluetooth/rfcomm.h":

	cdef struct rfcomm_dev_info:
		short id
		unsigned int flags
		unsigned short state
		bdaddr_t src
		bdaddr_t dst
		unsigned char channel
		
	cdef struct rfcomm_dev_list_req:
		unsigned short dev_num
		rfcomm_dev_info dev_info[0]
	

cdef extern from "libblueman.h":
	cdef struct conn_info_handles:
		unsigned int handle
		int dd
	

	cdef int connection_init(int dev_id, char *addr, conn_info_handles *ci)
	cdef int connection_get_rssi(conn_info_handles *ci, char *ret_rssi)
	cdef int connection_get_lq(conn_info_handles *ci, unsigned char *ret_lq)
	cdef int connection_get_tpl(conn_info_handles *ci, char *ret_tpl, unsigned char type)
	cdef int connection_close(conn_info_handles *ci)
	cdef int get_rfcomm_list(rfcomm_dev_list_req **ret)
	cdef float get_page_timeout(int hdev)
	cdef int _create_bridge(char* name)
	cdef int _destroy_bridge(char* name)

ERR = {
	-1:"Can't allocate memory",
	-2:"HCI device open failed",
	-3:"Not connected",
	-4:"Get connection info failed",
	-5:"Read RSSI failed",
	-6:"Read transmit power level request failed",
	-7:"Read Link quality failed",
	-8:"Getting rfcomm list failed",
	-9:"ERR_SOCKET_FAILED",
	-10:"ERR_CANT_READ_PAGE_TIMEOUT",
	-11:"ERR_READ_PAGE_TIMEOUT"
	}
	
RFCOMM_STATES = [
	"unknown",
	"connected",
	"clean",
	"bound",
	"listening",
	"connecting",
	"connecting",
	"config",
	"disconnecting",
	"closed"
]
RFCOMM_REUSE_DLC =	0
RFCOMM_RELEASE_ONHUP =	1
RFCOMM_HANGUP_NOW =	2
RFCOMM_TTY_ATTACHED =	3

def rfcomm_list():
	cdef rfcomm_dev_list_req *dl

	cdef char src[18]
	cdef char dst[18]

	
	res = get_rfcomm_list(&dl)
	if res < 0:
		raise Exception, ERR[res]
	
	devs = []
	for i from 0 <= i < dl.dev_num: 
		ba2str(&dl.dev_info[i].src, src)
		ba2str(&dl.dev_info[i].dst, dst)
		
		devs.append(
			{	"id": dl.dev_info[i].id,
				"channel": dl.dev_info[i].channel,
				"flags": dl.dev_info[i].flags,
				"state": RFCOMM_STATES[dl.dev_info[i].state],
				"src": src,
				"dst": dst	
			})

	free(dl)

	return devs
	
import exceptions
class BridgeException(exceptions.Exception):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)
		


def create_bridge(name="pan1"):
	err = _create_bridge(name)
	if err < 0:
		raise BridgeException(strerror(-err))
	
def destroy_bridge(name="pan1"):
	err = _destroy_bridge(name)
	if err < 0:
		raise BridgeException(strerror(-err))


cdef class conn_info:
	cdef conn_info_handles ci
	cdef int hci
	
	def __init__(self, addr, hci_name="hci0"):
		
				
		self.hci = int(hci_name[3:])
		res = connection_init(self.hci, addr, &self.ci)
		if res < 0:
			raise Exception, ERR[res]
			
	def deinit(self):
		connection_close(&self.ci)
			
	def get_rssi(self):
		cdef char rssi
		res = connection_get_rssi(&self.ci, &rssi)
		if res < 0:
			raise Exception, ERR[res]
		
		return rssi
		
	def get_lq(self):
		cdef unsigned char lq
		res = connection_get_lq(&self.ci, &lq)
		if res < 0:
			raise Exception, ERR[res]
		
		return lq
		
	def get_tpl(self, tp=0):
		cdef char tpl
		res = connection_get_tpl(&self.ci, &tpl, tp)
		if res < 0:
			raise Exception, ERR[res]
		
		return tpl			

def page_timeout(hci_name="hci0"):
	dev_id = int(hci_name[3:])
	ret = get_page_timeout(dev_id)
	if ret < 0:
		raise Exception, ERR[ret]
	else:
		return ret
		
def device_info(hci_name="hci0"):
	cdef hci_dev_info di
	cdef int ret
	
	dev_id = int(hci_name[3:])
	
	res = hci_devinfo(dev_id, &di)
	
	cdef char addr[32]
	ba2str(&di.bdaddr, addr)
	
	feats = []
	for i from 0 <= i < 8: 
		feats.append(di.features[i])
	
	x = [("err_rx", di.stat.err_rx),
	("err_tx",di.stat.err_tx),
	("cmd_tx",di.stat.cmd_tx),
	("evt_rx",di.stat.evt_rx),
	("acl_tx",di.stat.acl_tx),
	("acl_rx",di.stat.acl_rx),
	("sco_tx",di.stat.sco_tx),
	("sco_rx",di.stat.sco_rx),
	("byte_rx",di.stat.byte_rx),
	("byte_tx",di.stat.byte_tx)]
	
	z = [("dev_id", di.dev_id),
	("name", di.name),
	("bdaddr",addr),
	("flags",di.flags),
	("type",di.type),
	("features",feats),
	("pkt_type",di.pkt_type),
	("link_policy",di.link_policy),
	("link_mode",di.link_mode),
	("acl_mtu",di.acl_mtu),
	("acl_pkts",di.acl_pkts),
	("sco_mtu",di.sco_pkts),
	("stat", dict(x))]

	return dict(z)

cdef extern from "X11/X.h":
	ctypedef Time

cdef extern from "libsn/sn-launcher.h":
	cdef struct SnLauncherContext

	cdef void        sn_launcher_context_ref               (SnLauncherContext *context)
	cdef void        sn_launcher_context_unref             (SnLauncherContext *context)


	cdef void        sn_launcher_context_initiate          (SnLauncherContext *context, char *launcher_name, char *launchee_name, Time timestamp)
	cdef void        sn_launcher_context_complete          (SnLauncherContext *context)
	cdef char*       sn_launcher_context_get_startup_id    (SnLauncherContext *context)
	cdef int         sn_launcher_context_get_initiated     (SnLauncherContext *context)

	cdef void        sn_launcher_context_setup_child_process (SnLauncherContext *context)

	cdef void sn_launcher_context_set_name        (SnLauncherContext *context,
		                                   char        *name)
	cdef void sn_launcher_context_set_description (SnLauncherContext *context,
		                                   char        *description)
	cdef void sn_launcher_context_set_workspace   (SnLauncherContext *context,
		                                  int                workspace)
	cdef void sn_launcher_context_set_wmclass     (SnLauncherContext *context,
		                                   char        *klass)
	cdef void sn_launcher_context_set_binary_name (SnLauncherContext *context,
		                                   char        *name)
	cdef void sn_launcher_context_set_icon_name   (SnLauncherContext *context,
		                                   char        *name)

	cdef void sn_launcher_context_set_extra_property (SnLauncherContext *context,
		                                      char        *name,
		                                      char        *value)


	cdef void sn_launcher_context_get_initiated_time   (SnLauncherContext *context,
		                                       long              *tv_sec,
		                                       long              *tv_usec)
	cdef void sn_launcher_context_get_last_active_time (SnLauncherContext *context,
		                                       long              *tv_sec,
		                                       long              *tv_usec)

cdef extern SnLauncherContext* GetSnLauncherContext()


cdef class sn_launcher:
	cdef SnLauncherContext* ctx
	
	def __cinit__(self):
		self.ctx = GetSnLauncherContext()
		
		
	def __dealloc__(self):
		if self.ctx == NULL:
			raise Exception, "SnLauncherContext == NULL"
		sn_launcher_context_unref(self.ctx)

		
	def initiate(self, char* launcher_name, char* launchee_name, timestamp):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_initiate(self.ctx, launcher_name, launchee_name, timestamp)
		sn_launcher_context_unref(self.ctx)
	
	def complete(self):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_complete(self.ctx)
		sn_launcher_context_unref(self.ctx)
		
	def get_startup_id(self):
		cdef char* ret
		if self.ctx == NULL:
			raise Exception, "SnLauncherContext == NULL"
		sn_launcher_context_ref(self.ctx)
		ret = sn_launcher_context_get_startup_id(self.ctx)
		sn_launcher_context_unref(self.ctx)
		if ret != NULL:
			return ret
		else:
			return None
		
	def get_initiated(self):
		sn_launcher_context_ref(self.ctx)
		ret = bool(sn_launcher_context_get_initiated(self.ctx))
		sn_launcher_context_unref(self.ctx)
		return ret
	
	def setup_child_process(self):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_setup_child_process(self.ctx)
		sn_launcher_context_unref(self.ctx)
	
	def set_name(self, char* name):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_set_name(self.ctx, name)
		sn_launcher_context_unref(self.ctx)
		
	def set_description(self, char* descr):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_set_description(self.ctx, descr)
		sn_launcher_context_unref(self.ctx)
		
	def set_workspace(self, int workspace):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_set_workspace(self.ctx, workspace)
		sn_launcher_context_unref(self.ctx)
		
	def set_wmclass(self, char* klass):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_set_wmclass(self.ctx, klass)
		sn_launcher_context_unref(self.ctx)
		
	def set_binary_name(self, char* name):
		sn_launcher_context_ref(self.ctx)
		
		sn_launcher_context_set_binary_name(self.ctx, name)
		sn_launcher_context_unref(self.ctx)
		
	def set_icon_name(self, char* name):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_set_icon_name(self.ctx, name)
		sn_launcher_context_unref(self.ctx)
		
	def set_extra_property(self, char* key, char* value):
		sn_launcher_context_ref(self.ctx)
		sn_launcher_context_set_extra_property(self.ctx, key, value)
		sn_launcher_context_unref(self.ctx)
		
	def get_initiated_time(self):
		sn_launcher_context_ref(self.ctx)
		cdef long tv_sec
		cdef long tv_usec
		sn_launcher_context_get_initiated_time(self.ctx, &tv_sec, &tv_usec)
		sn_launcher_context_unref(self.ctx)
		return (tv_sec, tv_usec)
		
	def get_last_active_time(self):
		sn_launcher_context_ref(self.ctx)
		cdef long tv_sec
		cdef long tv_usec
		sn_launcher_context_get_last_active_time(self.ctx, &tv_sec, &tv_usec)
		sn_launcher_context_unref(self.ctx)
		return (tv_sec, tv_usec)








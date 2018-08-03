#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
#Comment out this import for cython version < 0.17
#We do not import any module here so no real loss.
#from __future__ import absolute_import
from __future__ import unicode_literals

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
    cdef int c_get_rfcomm_channel "get_rfcomm_channel" (unsigned short service_class, char* btd_addr)
    cdef int get_rfcomm_list(rfcomm_dev_list_req **ret)
    cdef int c_create_rfcomm_device "create_rfcomm_device" (char *local_address, char *remote_address, int channel)
    cdef int c_release_rfcomm_device "release_rfcomm_device" (int id)
    cdef float get_page_timeout(int hdev)
    cdef int _create_bridge(char* name)
    cdef int _destroy_bridge(char* name)
    cdef char* c_get_net_address "get_net_address" (char* iface, int i)
    cdef char** c_get_interface_list "get_interface_list" ()

cdef extern from "linux/sockios.h":
    cdef int SIOCGIFADDR
    cdef int SIOCGIFNETMASK

def get_net_address(py_iface):
    py_bytes_iface = py_iface.encode('UTF-8')
    cdef char* iface = py_bytes_iface
    cdef char* addr
    if iface != None:
        addr = c_get_net_address(iface, SIOCGIFADDR)
        if addr == NULL:
            return None
        else:
            return addr.decode("UTF-8")

def get_net_netmask(py_iface):
    py_bytes_iface = py_iface.encode("UTF-8")
    cdef char* iface = py_bytes_iface
    cdef char* addr
    if iface != None:
        addr = c_get_net_address(iface, SIOCGIFNETMASK)
        if addr == NULL:
            return None
        else:
            return addr.decode("UTF-8")

def get_net_interfaces():
    cdef char** ifaces
    cdef int i
    i = 0

    ifaces = c_get_interface_list()
    if ifaces == NULL:
        return []

    ret = []
    while 1:
        if ifaces[i] == NULL:
            break
        else:
            ret.append(ifaces[i].decode("UTF-8"))
            free(ifaces[i])
        i = i + 1

    free(ifaces)
    return ret

class RFCOMMError(Exception):
    pass

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
    -11:"ERR_READ_PAGE_TIMEOUT",
    -12: "Can't bind RFCOMM socket",
    -13: "Can't connect RFCOMM socket",
    -14: "Can't create RFCOMM TTY",
    -15: "Can't release RFCOMM TTY"
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
RFCOMM_REUSE_DLC =    0
RFCOMM_RELEASE_ONHUP =    1
RFCOMM_HANGUP_NOW =    2
RFCOMM_TTY_ATTACHED =    3

def get_rfcomm_channel(uuid, py_bdaddr):
    py_bytes = py_bdaddr.encode('UTF-8')
    cdef char* bdaddr = py_bytes

    if bdaddr is not None:
        return c_get_rfcomm_channel(uuid, bdaddr)

def rfcomm_list():
    cdef rfcomm_dev_list_req *dl

    cdef char src[18]
    cdef char dst[18]


    res = get_rfcomm_list(&dl)
    if res < 0:
        raise Exception, ERR[res]

    devs = []
    for 0 <= i < dl.dev_num:
        ba2str(&dl.dev_info[i].src, src)
        ba2str(&dl.dev_info[i].dst, dst)

        devs.append(
            {    "id": dl.dev_info[i].id,
                "channel": dl.dev_info[i].channel,
                "flags": dl.dev_info[i].flags,
                "state": RFCOMM_STATES[dl.dev_info[i].state],
                "src": src.decode("UTF-8"),
                "dst": dst.decode("UTF-8")
            })

    free(dl)

    return devs


def create_rfcomm_device(py_local_address, py_remote_address, channel):
    py_bytes_local_address = py_local_address.encode('UTF-8')
    py_bytes_remote_address = py_remote_address.encode('UTF-8')
    cdef char* local_address = py_bytes_local_address
    cdef char* remote_address = py_bytes_remote_address
    ret = c_create_rfcomm_device(local_address, remote_address, channel)
    if ret < 0:
        raise RFCOMMError(ERR[ret])
    return ret


def release_rfcomm_device(id):
    ret = c_release_rfcomm_device(id)
    if ret < 0:
        raise RFCOMMError(ERR[ret])
    return ret

try: from exceptions import Exception
except ImportError: pass

class BridgeException(Exception):
    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return strerror(self.errno)



def create_bridge(py_name="pan1"):
    py_bytes_name = py_name.encode("UTF-8")
    cdef char* name = py_bytes_name

    err = _create_bridge(name)
    if err < 0:
        raise BridgeException(-err)

def destroy_bridge(py_name="pan1"):
    py_bytes_name = py_name.encode("UTF-8")
    cdef char* name = py_bytes_name

    err = _destroy_bridge(name)
    if err < 0:
        raise BridgeException(-err)


cdef class conn_info:
    cdef conn_info_handles ci
    cdef int hci

    def __init__(self, py_addr, py_hci_name="hci0"):
        py_bytes_addr = py_addr.encode("UTF-8")
        cdef char* addr = py_bytes_addr

        py_bytes_hci_name = py_hci_name.encode("UTF-8")
        cdef char* hci_name = py_bytes_hci_name


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

def page_timeout(py_hci_name="hci0"):
    py_bytes_hci_name = py_hci_name.encode("UTF-8")
    cdef char* hci_name = py_bytes_hci_name

    dev_id = int(hci_name[3:])
    ret = get_page_timeout(dev_id)
    if ret < 0:
        raise Exception, ERR[ret]
    else:
        return ret

def device_info(py_hci_name="hci0"):
    py_bytes_hci_name = py_hci_name.encode("UTF-8")
    cdef char* hci_name = py_bytes_hci_name

    cdef hci_dev_info di
    cdef int ret

    dev_id = int(hci_name[3:])

    res = hci_devinfo(dev_id, &di)

    cdef char addr[32]
    ba2str(&di.bdaddr, addr)

    feats = []
    for 0 <= i < 8:
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
    ("name", di.name.decode("UTF-8")),
    ("bdaddr",addr.decode("UTF-8")),
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

cdef extern from "glib-object.h":
    ctypedef struct GObject

cdef extern from "pygobject.h":
    cdef GObject* pygobject_get(object)

cdef extern from "modem-prober.h":
    cdef void c_probe_modem "probe_modem" (char* device, object callback)
    cdef void c_set_probe_debug "set_probe_debug" (int debug)

def probe_modem(node, callback):

    if not callable(callback):
        raise TypeError, "callback must be callable"

    if node != None:
        c_probe_modem(node, callback)
    else:
        raise TypeError, "device node must not be None"

def set_probe_debug(enable):
    c_set_probe_debug(int(enable))

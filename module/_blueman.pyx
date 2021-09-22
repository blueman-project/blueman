#!/usr/bin/env python3
# coding=utf-8
#cython: language_level=3

cdef extern from "malloc.h":
    cdef void free(void *ptr)

cdef extern from "string.h":
    cdef char* strerror(int errnum)

cdef extern from "bluetooth/bluetooth.h":
    ctypedef struct bdaddr_t:
        unsigned char b[6]

    int ba2str(bdaddr_t *ba, char *str)

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
    cdef int c_get_rfcomm_channel "get_rfcomm_channel" (unsigned short service_class, char* btd_addr)
    cdef int get_rfcomm_list(rfcomm_dev_list_req **ret)
    cdef int c_create_rfcomm_device "create_rfcomm_device" (char *local_address, char *remote_address, int channel)
    cdef int c_release_rfcomm_device "release_rfcomm_device" (int id)
    cdef int _create_bridge(char* name)
    cdef int _destroy_bridge(char* name)


class RFCOMMError(Exception):
    pass

ERR = {
    -1:"Can't allocate memory",
    -8:"Getting rfcomm list failed",
    -9:"ERR_SOCKET_FAILED",
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
    if py_bdaddr is None:
        return

    py_bytes = py_bdaddr.encode('UTF-8')
    cdef char* bdaddr = py_bytes
    return c_get_rfcomm_channel(uuid, bdaddr)

def rfcomm_list():
    cdef rfcomm_dev_list_req *dl

    cdef char src[18]
    cdef char dst[18]


    res = get_rfcomm_list(&dl)
    if res < 0:
        raise RFCOMMError(ERR[res])

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

/*
 * Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
 * Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
 *
 * Licensed under the GNU General Public License Version 3
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <netinet/in.h>
#include <arpa/inet.h>
#include <ctype.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>
#include <linux/sockios.h>
#include <linux/if.h>
#include <linux/if_bridge.h>

#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/rfcomm.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>
#include <errno.h>

#include "libblueman.h"

static inline unsigned long __tv_to_jiffies(const struct timeval *tv)
{
        unsigned long long jif;

        jif = 1000000ULL * tv->tv_sec + tv->tv_usec;

        return jif/10000;
}
        
int _create_bridge(const char* name) {
	int sock;
	sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock < 0) {
		return -errno;
	}
	
	int err;

	err = ioctl(sock, SIOCBRADDBR, name);
	if (err < 0) {
		close(sock);
		return -errno;
	}
		
	
	struct timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 1000000 * (0 - tv.tv_sec);
        
        
        unsigned long args[5];
        struct ifreq ifr;
        
        args[0] = BRCTL_SET_BRIDGE_FORWARD_DELAY;
        args[1] = __tv_to_jiffies(&tv);
        args[2] = 0;
        args[3] = 0;
        args[4] = 0;
        
        memcpy(ifr.ifr_name, name, IFNAMSIZ);
        ifr.ifr_data = (char *) &args;
        
	ioctl(sock, SIOCDEVPRIVATE, &ifr);
	
	close(sock);
	return 0;
}
	
	
int _destroy_bridge(const char* name) {
	int sock;
	sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock < 0) {
		return -errno;
	}
	
	int err;
	
	struct ifreq req;
	memset(&req, 0, sizeof (struct ifreq));
	strncpy(req.ifr_name, name, IFNAMSIZ);
	
	err = ioctl(sock, SIOCGIFFLAGS, &req);
	if (err < 0) {
		close(sock);
		return -errno;
	}
	
	req.ifr_flags &= ~(IFF_UP | IFF_RUNNING);

	err = ioctl(sock, SIOCSIFFLAGS, &req);

	if (err < 0) {
		close(sock);
		return -errno;
	}

	err = ioctl(sock, SIOCBRDELBR, name);
	if (err < 0) {
		close(sock);
		return -errno;
	}
		
	close(sock);
	
	return 0;
}

int find_conn(int s, int dev_id, long arg)
{
	struct hci_conn_list_req *cl;
	struct hci_conn_info *ci;
	int i;
	int ret = 0;

	if (!(cl = malloc(10 * sizeof(*ci) + sizeof(*cl))))
		goto out;

	cl->dev_id = dev_id;
	cl->conn_num = 10;
	ci = cl->conn_info;

	if (ioctl(s, HCIGETCONNLIST, (void *) cl))
		goto out;

	for (i = 0; i < cl->conn_num; i++, ci++)
		if (!bacmp((bdaddr_t *) arg, &ci->bdaddr)) {
			ret = 1;
			goto out;
		}

out:
	free(cl);
	return ret;
}



int connection_init(int dev_id, char *addr, struct conn_info_handles *ci)
{
	struct hci_conn_info_req *cr = NULL;
	bdaddr_t bdaddr;
	
	int dd;
	int ret = 1;

	str2ba(addr, &bdaddr);

	if (dev_id < 0) {
		dev_id = hci_for_each_dev(HCI_UP, find_conn, (long) &bdaddr);
		if (dev_id < 0) {
			ret = ERR_NOT_CONNECTED;
			goto out;
		}
	}

	dd = hci_open_dev(dev_id);
	if (dd < 0) {
		ret = ERR_HCI_DEV_OPEN_FAILED;
		goto out;
	}

	cr = malloc(sizeof(*cr) + sizeof(struct hci_conn_info));
	if (!cr) {
		ret = ERR_CANNOT_ALLOCATE;
		goto out;
	}

	bacpy(&cr->bdaddr, &bdaddr);
	cr->type = ACL_LINK;
	if (ioctl(dd, HCIGETCONNINFO, (unsigned long) cr) < 0) {
		ret = ERR_GET_CONN_INFO_FAILED;
		goto out;
	}
	
	ci->dd = dd;
	ci->handle = cr->conn_info->handle;

out:
	if (cr)
		free(cr);
	
	return ret;
}

int connection_get_rssi(struct conn_info_handles *ci, int8_t *ret_rssi)
{
	int8_t rssi;
	if (hci_read_rssi(ci->dd, htobs(ci->handle), &rssi, 1000) < 0) {
		return ERR_READ_RSSI_FAILED;
	}
	*ret_rssi = rssi;
	return 1;

}

int connection_get_lq(struct conn_info_handles *ci, uint8_t *ret_lq)
{
	uint8_t lq;
	if (hci_read_link_quality(ci->dd, htobs(ci->handle), &lq, 1000) < 0) {
		return ERR_READ_LQ_FAILED;
	}
	*ret_lq = lq;
	return 1;
}

int connection_get_tpl(struct conn_info_handles *ci, int8_t *ret_tpl, uint8_t type)
{ 	
	int8_t level;
	if (hci_read_transmit_power_level(ci->dd, htobs(ci->handle), type, &level, 1000) < 0) {
		return ERR_READ_TPL_FAILED;
	}
	*ret_tpl = level;
	return 1;
}
	
int connection_close(struct conn_info_handles *ci)
{
	hci_close_dev(ci->dd);
	return 1;
}

int
get_rfcomm_channel(uint16_t service_class, char* btd_addr) {
    bdaddr_t target;
    sdp_session_t *session = 0;
    uuid_t service_uuid;
    int err;
    int port_num = 0;
    sdp_list_t *response_list = NULL, *search_list, *attrid_list;

    str2ba(btd_addr, &target);
    sdp_uuid16_create(&service_uuid, service_class);

    session = sdp_connect(BDADDR_ANY, &target, SDP_RETRY_IF_BUSY);

    if (!session) {
        printf("Failed to connect to sdp\n");
        return port_num;
    }

    search_list = sdp_list_append(NULL, &service_uuid);

    uint32_t range = 0x0000ffff;
    attrid_list = sdp_list_append(NULL, &range);

    err = sdp_service_search_attr_req(session, search_list, SDP_ATTR_REQ_RANGE, attrid_list, &response_list);

    if (err) {
        printf("Failed to search attributes\n");
        sdp_list_free(response_list, 0);
        sdp_list_free(search_list, 0);
        sdp_list_free(attrid_list, 0);
        return port_num;
    }
    // go through each of the service records
    sdp_list_t *r = response_list;
    for (; r; r = r->next) {
        sdp_record_t *rec = (sdp_record_t*) r->data;
        sdp_list_t *proto_list;

        // get a list of the protocol sequences
        if(sdp_get_access_protos(rec, &proto_list) == 0) {
            sdp_list_t *p = proto_list;

            // go through each protocol sequence
            for(; p ; p = p->next) {
                sdp_list_t *pds = (sdp_list_t*)p->data;

                // go through each protocol list of the protocol sequence
                for(; pds ; pds = pds->next) {

                    // check the protocol attributes
                    sdp_data_t *d = (sdp_data_t*)pds->data;
                    int proto = 0;
                    for(; d; d = d->next) {
                        switch(d->dtd) {
                        case SDP_UUID16:
                        case SDP_UUID32:
                        case SDP_UUID128:
                            proto = sdp_uuid_to_proto(&d->val.uuid);
                            break;
                        case SDP_UINT8:
                            if(proto == RFCOMM_UUID) {
                                port_num = d->val.int8;
                                printf("rfcomm channel: %d\n", port_num);
                            }
                            break;
                        }
                    }
                }
                sdp_list_free((sdp_list_t*)p->data, 0);
            }
            sdp_list_free(proto_list, 0);
        }
        sdp_record_free(rec);
    }
    sdp_close(session);
    return port_num;
}

int
get_rfcomm_list(struct rfcomm_dev_list_req **result)
{
	struct rfcomm_dev_list_req *dl;
	struct rfcomm_dev_info *di;
	int ctl = -1;
	int ret = 1;

	ctl = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_RFCOMM);
	if (ctl < 0) {
		ret = ERR_SOCKET_FAILED; //Can't open RFCOMM control socket
		goto out;
	}

	dl = malloc(sizeof(*dl) + RFCOMM_MAX_DEV * sizeof(*di));
	if (dl == NULL) {
		ret = ERR_CANNOT_ALLOCATE;
		goto out;
	}

	dl->dev_num = RFCOMM_MAX_DEV;
	di = dl->dev_info;

	if (ioctl(ctl, RFCOMMGETDEVLIST, (void *) dl) < 0) {
		ret = ERR_GET_RFCOMM_LIST_FAILED;
		free(dl);
		goto out;
	}

	*result = dl;
	
out:
	if (ctl >= 0)
		close(ctl);
	return ret;
}

int create_rfcomm_device(char *local_address, char *remote_address, int channel) {
    int sk, dev, ret;
    struct sockaddr_rc laddr, raddr;
    struct rfcomm_dev_req req;

    sk = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    if (sk < 0) {
        ret = ERR_SOCKET_FAILED;
        goto out;
    }

    laddr.rc_family = AF_BLUETOOTH;
    str2ba(local_address, &laddr.rc_bdaddr);
    laddr.rc_channel = 0;

    if (bind(sk, (struct sockaddr *) &laddr, sizeof(laddr)) < 0) {
        ret = ERR_BIND_FAILED;
        goto out;
    }

    raddr.rc_family = AF_BLUETOOTH;
    str2ba(remote_address, &raddr.rc_bdaddr);
    raddr.rc_channel = channel;

    if (connect(sk, (struct sockaddr *) &raddr, sizeof(raddr)) < 0) {
        ret = ERR_CONNECT_FAILED;
        goto out;
    }

    memset(&req, 0, sizeof(req));
    req.flags = (1 << RFCOMM_REUSE_DLC) | (1 << RFCOMM_RELEASE_ONHUP);
    bacpy(&req.src, &laddr.rc_bdaddr);
    bacpy(&req.dst, &raddr.rc_bdaddr);
    req.channel = raddr.rc_channel;
    req.dev_id = -1;

    dev = ioctl(sk, RFCOMMCREATEDEV, &req);
    if (dev < 0) {
        ret = ERR_CREATE_DEV_FAILED;
    } else {
        ret = dev;
    }

out:
    if (sk >= 0)
        close(sk);
    return ret;
}

int release_rfcomm_device(int id) {
    int sk;
    struct rfcomm_dev_req req;

    sk = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_RFCOMM);
    if (sk < 0)
        return ERR_SOCKET_FAILED;

    memset(&req, 0, sizeof(req));
    req.flags = (1 << RFCOMM_HANGUP_NOW);
    req.dev_id = id;

    if (ioctl(sk, RFCOMMRELEASEDEV, &req) < 0) {
        close(sk);
        return ERR_RELEASE_DEV_FAILED;
    } else {
        close(sk);
        return 0;
    }
}

float get_page_timeout(int hdev)
{
	struct hci_request rq;
	int s;
	float ret;

	if ((s = hci_open_dev(hdev)) < 0) {
		ret = ERR_HCI_DEV_OPEN_FAILED;
		goto out;
	}

	memset(&rq, 0, sizeof(rq));

	uint16_t timeout;
	read_page_timeout_rp rp;

	rq.ogf = OGF_HOST_CTL;
	rq.ocf = OCF_READ_PAGE_TIMEOUT;
	rq.rparam = &rp;
	rq.rlen = READ_PAGE_TIMEOUT_RP_SIZE;

	if (hci_send_req(s, &rq, 1000) < 0) {
		ret = ERR_CANT_READ_PAGE_TIMEOUT;
		goto out;
	}
	if (rp.status) {
		ret = ERR_READ_PAGE_TIMEOUT;
		goto out;
	}
	
	timeout = btohs(rp.timeout);
	ret = ((float)timeout * 0.625);

out:
	if (s >= 0)
		hci_close_dev(s);
	return ret;
}







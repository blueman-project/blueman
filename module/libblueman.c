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
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/sockios.h>
#include <linux/if.h>
#include <linux/if_bridge.h>

#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/rfcomm.h>
#include <errno.h>

#include "libblueman.h"

char* get_net_address(char* iface, int _ioctl) {
	int sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock < 0) {
		return NULL;
	}
		
	struct ifreq ifr;
	strncpy(ifr.ifr_name, iface, IFNAMSIZ);
	
	int err = ioctl(sock, _ioctl, &ifr);
	if (err < 0) {
		close(sock);
		return NULL;
	}
	
	return inet_ntoa(((struct sockaddr_in*) &ifr.ifr_addr)->sin_addr);
}

char** get_interface_list() {
	int sock = socket(AF_INET, SOCK_STREAM, 0);
	char** rets = NULL;
	
	struct ifconf ifc;
	ifc.ifc_len = 128 * sizeof(struct ifreq);
	ifc.ifc_req = malloc(ifc.ifc_len);
	
	int res = ioctl(sock, SIOCGIFCONF, &ifc);
	if(res < 0) {

	} else {
		int size = ifc.ifc_len/sizeof(struct ifreq);
	
		rets = malloc((size+1)*sizeof(char*));
		memset(rets, '\0', (size+1)*sizeof(char*));
	
		int i;
		for(i = 0; i < size; i++) {
			rets[i] = strdup(ifc.ifc_req[i].ifr_name);
		}
	}

	close(sock);
	free(ifc.ifc_req);
	return rets;
}

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
        ((unsigned long *)(&ifr.ifr_data))[0] = (unsigned long)args;
        
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
	if(dl == NULL) {
		ret = ERR_CANNOT_ALLOCATE;
		goto out;
	}

	dl->dev_num = RFCOMM_MAX_DEV;
	di = dl->dev_info;

	if (ioctl(ctl, RFCOMMGETDEVLIST, (void *) dl) < 0) {
		ret = ERR_GET_RFCOMM_LIST_FAILED;
		goto out;
	}

	*result = dl;
	
out:
	if (ctl >= 0)
		close(ctl);
	return ret;
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







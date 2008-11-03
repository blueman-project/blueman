#include <ctype.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/rfcomm.h>

#include "libblueman.h"

int find_conn(int s, int dev_id, long arg)
{
	struct hci_conn_list_req *cl;
	struct hci_conn_info *ci;
	int i;

	if (!(cl = malloc(10 * sizeof(*ci) + sizeof(*cl)))) {
		return 0;
	}
	cl->dev_id = dev_id;
	cl->conn_num = 10;
	ci = cl->conn_info;

	if (ioctl(s, HCIGETCONNLIST, (void *) cl)) {
		return 0;
	}

	for (i = 0; i < cl->conn_num; i++, ci++)
		if (!bacmp((bdaddr_t *) arg, &ci->bdaddr))
			return 1;

	return 0;
}



int connection_init(int dev_id, char *addr, struct conn_info_handles *ci) {
	
	struct hci_conn_info_req *cr;
	bdaddr_t bdaddr;
	
	int dd;

	str2ba(addr, &bdaddr);

	if (dev_id < 0) {
		dev_id = hci_for_each_dev(HCI_UP, find_conn, (long) &bdaddr);
		if (dev_id < 0) {
			return ERR_NOT_CONNECTED;
		}
	}

	dd = hci_open_dev(dev_id);
	if (dd < 0) {
		return ERR_HCI_DEV_OPEN_FAILED;
	}

	cr = malloc(sizeof(*cr) + sizeof(struct hci_conn_info));
	if (!cr) {
		return ERR_CANNOT_ALLOCATE;
	}

	bacpy(&cr->bdaddr, &bdaddr);
	cr->type = ACL_LINK;
	if (ioctl(dd, HCIGETCONNINFO, (unsigned long) cr) < 0) {
		return ERR_GET_CONN_INFO_FAILED;
	}
	
	ci->dd = dd;
	ci->handle = cr->conn_info->handle;

	free(cr);

	return 1;

}

int connection_get_rssi(struct conn_info_handles *ci, int8_t *ret_rssi) {
	int8_t rssi;
	if (hci_read_rssi(ci->dd, htobs(ci->handle), &rssi, 1000) < 0) {
		return ERR_READ_RSSI_FAILED;
	}
	*ret_rssi = rssi;
	return 1;

}

int connection_get_lq(struct conn_info_handles *ci, uint8_t *ret_lq) {
	uint8_t lq;
	if (hci_read_link_quality(ci->dd, htobs(ci->handle), &lq, 1000) < 0) {
		return ERR_READ_LQ_FAILED;
	}
	*ret_lq = lq;
	return 1;
}

int connection_get_tpl(struct conn_info_handles *ci, int8_t *ret_tpl, uint8_t type) { 	
	int8_t level;
	if (hci_read_transmit_power_level(ci->dd, htobs(ci->handle), type, &level, 1000) < 0) {
		return ERR_READ_TPL_FAILED;
	}
	*ret_tpl = level;
	return 1;
}
	
int connection_close(struct conn_info_handles *ci) {
	
	hci_close_dev(ci->dd);
	return 1;
}




int
get_rfcomm_list(struct rfcomm_dev_list_req **ret)
{

	int ctl;

	ctl = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_RFCOMM);
	if (ctl < 0) {
		return ERR_SOCKET_FAILED; //Can't open RFCOMM control socket
	}

	
	struct rfcomm_dev_list_req *dl;
	struct rfcomm_dev_info *di;
	

	dl = malloc(sizeof(*dl) + RFCOMM_MAX_DEV * sizeof(*di));
	if(dl == NULL) {
		return ERR_CANNOT_ALLOCATE;
	}


	dl->dev_num = RFCOMM_MAX_DEV;
	di = dl->dev_info;

	if (ioctl(ctl, RFCOMMGETDEVLIST, (void *) dl) < 0) {
		return ERR_GET_RFCOMM_LIST_FAILED;
	}

	*ret = dl;
	
	return 1;
	

}

float get_page_timeout(int hdev)
{
	struct hci_request rq;
	int s;

	if ((s = hci_open_dev(hdev)) < 0) {
		return ERR_HCI_DEV_OPEN_FAILED;
	}

	memset(&rq, 0, sizeof(rq));


	uint16_t timeout;
	read_page_timeout_rp rp;

	rq.ogf = OGF_HOST_CTL;
	rq.ocf = OCF_READ_PAGE_TIMEOUT;
	rq.rparam = &rp;
	rq.rlen = READ_PAGE_TIMEOUT_RP_SIZE;

	if (hci_send_req(s, &rq, 1000) < 0) {
		return ERR_CANT_READ_PAGE_TIMEOUT;
	}
	if (rp.status) {
		return ERR_READ_PAGE_TIMEOUT;
	}
	
	timeout = btohs(rp.timeout);
	return ((float)timeout * 0.625);

}


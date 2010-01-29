#pragma once
#define ERR_CANNOT_ALLOCATE -1
#define ERR_HCI_DEV_OPEN_FAILED -2
#define ERR_NOT_CONNECTED -3
#define ERR_GET_CONN_INFO_FAILED -4
#define ERR_READ_RSSI_FAILED -5
#define ERR_READ_TPL_FAILED -6
#define ERR_READ_LQ_FAILED -7
#define ERR_GET_RFCOMM_LIST_FAILED -8
#define ERR_SOCKET_FAILED -9
#define ERR_CANT_READ_PAGE_TIMEOUT -10
#define ERR_READ_PAGE_TIMEOUT -11

struct conn_info_handles {
	unsigned int handle;
	int dd;
};

int find_conn(int s, int dev_id, long arg);
int connection_init(int dev_id, char *addr, struct conn_info_handles *ci);
int connection_get_rssi(struct conn_info_handles *ci, int8_t *ret_rssi);
int connection_get_lq(struct conn_info_handles *ci, uint8_t *ret_lq);
int connection_get_tpl(struct conn_info_handles *ci, int8_t *ret_tpl, uint8_t type);
int connection_close(struct conn_info_handles *ci);
int get_rfcomm_list(struct rfcomm_dev_list_req **result);
float get_page_timeout(int hdev);

int _create_bridge(const char* name);
int _destroy_bridge(const char* name);
char* get_net_address(char* iface, int _ioctl);
char** get_interface_list();

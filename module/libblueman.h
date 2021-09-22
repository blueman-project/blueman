#pragma once
#define ERR_CANNOT_ALLOCATE -1
#define ERR_GET_RFCOMM_LIST_FAILED -8
#define ERR_SOCKET_FAILED -9
#define ERR_BIND_FAILED -12
#define ERR_CONNECT_FAILED -13
#define ERR_CREATE_DEV_FAILED -14
#define ERR_RELEASE_DEV_FAILED -15

int get_rfcomm_channel(uint16_t uuid, char* btd_addr);
int get_rfcomm_list(struct rfcomm_dev_list_req **result);
int create_rfcomm_device(char *local_address, char *remote_address, int channel);
int release_rfcomm_device(int id);

int _create_bridge(const char* name);
int _destroy_bridge(const char* name);

/*
 * Unit + fuzz tests for module/libblueman.c.
 *
 * The translation unit under test is #included directly so the tests can reach
 * its static helpers (__tv_to_jiffies, find_conn). Every libc and libbluetooth
 * call it makes is redirected with ld --wrap to a controllable mock, so each
 * success and error path is exercised without a Bluetooth adapter or root.
 *
 * Build/run is driven by run_tests.sh (ASan + gcov). See that script.
 */
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Pull in the code under test (gives access to static functions). */
#include "../../module/libblueman.c"

/* ------------------------------------------------------------------ */
/* Minimal test harness                                               */
/* ------------------------------------------------------------------ */
static int g_failures = 0;
static int g_checks = 0;

#define CHECK(cond) do { \
	g_checks++; \
	if (!(cond)) { \
		g_failures++; \
		fprintf(stderr, "  FAIL %s:%d: %s\n", __func__, __LINE__, #cond); \
	} \
} while (0)

#define RUN(test) do { \
	reset_mocks(); \
	fprintf(stderr, "RUN  %s\n", #test); \
	test(); \
} while (0)

/* ------------------------------------------------------------------ */
/* Mock state                                                         */
/* ------------------------------------------------------------------ */
typedef int (*ioctl_hook_t)(int fd, unsigned long request, void *arg);

static struct {
	/* sockets */
	int socket_ret;        /* fd to hand out, or <0 to fail */
	int socket_opens;
	int socket_closes;
	/* ioctl/bind/connect */
	ioctl_hook_t ioctl_hook;
	int bind_ret;
	int connect_ret;
	/* malloc fault injection: fail the Nth wrapped malloc (1-based), 0 = never */
	int malloc_fail_at;
	int malloc_calls;
	/* str2ba */
	int str2ba_ret;
	int str2ba_calls;
	int str2ba_fail_at;   /* fail the Nth str2ba call (1-based), 0 = use str2ba_ret */
	/* hci */
	int hci_dev_id_ret;
	int hci_open_ret;
	int hci_closes;
	int hci_rssi_ret;
	int hci_rssi_val;
	int hci_tpl_ret;
	int hci_tpl_val;
	/* sdp */
	void *sdp_session_ret;
	int sdp_search_ret;
	int sdp_uuid_to_proto_ret;
	int sdp_nodes_alloced;
	int sdp_nodes_freed;
	int sdp_records_freed;
	int sdp_session_closed;
	sdp_list_t *sdp_response;   /* handed back by search_attr_req */
	sdp_list_t *sdp_protos;     /* handed back by get_access_protos */
	int sdp_get_protos_ret;
} M;

extern void *__real_malloc(size_t size);

static void reset_mocks(void)
{
	memset(&M, 0, sizeof(M));
	M.socket_ret = 100;        /* a plausible fd */
	M.hci_dev_id_ret = 0;
	M.hci_open_ret = 7;
	M.sdp_session_ret = (void *) 0x1;
	M.sdp_uuid_to_proto_ret = RFCOMM_UUID;
	M.sdp_get_protos_ret = 0;
}

/* ------------------------------------------------------------------ */
/* libc wraps                                                         */
/* ------------------------------------------------------------------ */
int __wrap_socket(int domain, int type, int protocol)
{
	(void) domain; (void) type; (void) protocol;
	if (M.socket_ret < 0) {
		errno = EACCES;
		return -1;
	}
	M.socket_opens++;
	return M.socket_ret;
}

int __wrap_close(int fd)
{
	(void) fd;
	M.socket_closes++;
	return 0;
}

int __wrap_ioctl(int fd, unsigned long request, ...)
{
	va_list ap;
	void *arg;
	va_start(ap, request);
	arg = va_arg(ap, void *);
	va_end(ap);
	if (M.ioctl_hook)
		return M.ioctl_hook(fd, request, arg);
	return 0;
}

int __wrap_bind(int fd, const struct sockaddr *addr, socklen_t len)
{
	(void) fd; (void) addr; (void) len;
	return M.bind_ret;
}

int __wrap_connect(int fd, const struct sockaddr *addr, socklen_t len)
{
	(void) fd; (void) addr; (void) len;
	return M.connect_ret;
}

void *__wrap_malloc(size_t size)
{
	M.malloc_calls++;
	if (M.malloc_fail_at && M.malloc_calls == M.malloc_fail_at)
		return NULL;
	return __real_malloc(size);
}

/* ------------------------------------------------------------------ */
/* libbluetooth wraps                                                 */
/* ------------------------------------------------------------------ */
int __wrap_str2ba(const char *str, bdaddr_t *ba)
{
	(void) str;
	M.str2ba_calls++;
	if (M.str2ba_fail_at && M.str2ba_calls == M.str2ba_fail_at)
		return -1;
	if (M.str2ba_ret < 0)
		return -1;
	memset(ba, 0, sizeof(*ba));
	return 0;
}

int __wrap_hci_for_each_dev(int flag, int (*func)(int, int, long), long arg)
{
	(void) flag; (void) func; (void) arg;
	return M.hci_dev_id_ret;
}

int __wrap_hci_open_dev(int dev_id)
{
	(void) dev_id;
	return M.hci_open_ret;
}

int __wrap_hci_close_dev(int dd)
{
	(void) dd;
	M.hci_closes++;
	return 0;
}

int __wrap_hci_read_rssi(int dd, uint16_t handle, int8_t *rssi, int to)
{
	(void) dd; (void) handle; (void) to;
	if (M.hci_rssi_ret < 0)
		return -1;
	*rssi = (int8_t) M.hci_rssi_val;
	return 0;
}

int __wrap_hci_read_transmit_power_level(int dd, uint16_t handle, uint8_t type,
					 int8_t *level, int to)
{
	(void) dd; (void) handle; (void) type; (void) to;
	if (M.hci_tpl_ret < 0)
		return -1;
	*level = (int8_t) M.hci_tpl_val;
	return 0;
}

sdp_session_t *__wrap_sdp_connect(const bdaddr_t *src, const bdaddr_t *dst, uint32_t flags)
{
	(void) src; (void) dst; (void) flags;
	return (sdp_session_t *) M.sdp_session_ret;
}

int __wrap_sdp_close(sdp_session_t *session)
{
	(void) session;
	M.sdp_session_closed++;
	return 0;
}

sdp_list_t *__wrap_sdp_list_append(sdp_list_t *list, void *d)
{
	sdp_list_t *node = __real_malloc(sizeof(sdp_list_t));
	M.sdp_nodes_alloced++;
	node->data = d;
	node->next = list;
	return node;
}

int __wrap_sdp_service_search_attr_req(sdp_session_t *session, const sdp_list_t *search,
				       sdp_attrreq_type_t reqtype, const sdp_list_t *attrids,
				       sdp_list_t **rsp)
{
	(void) session; (void) search; (void) reqtype; (void) attrids;
	if (M.sdp_search_ret)
		return M.sdp_search_ret;
	*rsp = M.sdp_response;
	return 0;
}

int __wrap_sdp_get_access_protos(const sdp_record_t *rec, sdp_list_t **protos)
{
	(void) rec;
	if (M.sdp_get_protos_ret)
		return M.sdp_get_protos_ret;
	*protos = M.sdp_protos;
	return 0;
}

int __wrap_sdp_uuid_to_proto(uuid_t *uuid)
{
	(void) uuid;
	return M.sdp_uuid_to_proto_ret;
}

void __wrap_sdp_list_free(sdp_list_t *list, sdp_free_func_t f)
{
	(void) f;
	while (list) {
		sdp_list_t *next = list->next;
		free(list);
		M.sdp_nodes_freed++;
		list = next;
	}
}

void __wrap_sdp_record_free(sdp_record_t *rec)
{
	free(rec);
	M.sdp_records_freed++;
}

/* ------------------------------------------------------------------ */
/* helpers to build fake SDP structures                               */
/* ------------------------------------------------------------------ */
static sdp_list_t *node(void *data, sdp_list_t *next)
{
	sdp_list_t *n = __real_malloc(sizeof(sdp_list_t));
	M.sdp_nodes_alloced++;
	n->data = data;
	n->next = next;
	return n;
}

/* ================================================================== */
/* __tv_to_jiffies                                                    */
/* ================================================================== */
static void test_tv_to_jiffies(void)
{
	struct timeval z = { 0, 0 };
	CHECK(__tv_to_jiffies(&z) == 0);
	struct timeval one = { 0, 10000 };  /* 10000 usec / 10000 = 1 */
	CHECK(__tv_to_jiffies(&one) == 1);
	struct timeval sec = { 1, 0 };      /* 1000000 / 10000 = 100 */
	CHECK(__tv_to_jiffies(&sec) == 100);
}

/* ================================================================== */
/* _create_bridge                                                     */
/* ================================================================== */
static int ioctl_ok(int fd, unsigned long req, void *arg)
{
	(void) fd; (void) req; (void) arg;
	return 0;
}
static unsigned long g_fail_req;
static int ioctl_fail_one(int fd, unsigned long req, void *arg)
{
	(void) fd; (void) arg;
	return (req == g_fail_req) ? -1 : 0;
}

static void test_create_bridge_success(void)
{
	M.ioctl_hook = ioctl_ok;
	CHECK(_create_bridge("pan1") == 0);
	CHECK(M.socket_opens == 1 && M.socket_closes == 1);
}

static void test_create_bridge_socket_fail(void)
{
	M.socket_ret = -1;
	CHECK(_create_bridge("pan1") < 0);
	CHECK(M.socket_closes == 0);
}

static void test_create_bridge_addbr_fail(void)
{
	g_fail_req = SIOCBRADDBR;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(_create_bridge("pan1") < 0);
	CHECK(M.socket_opens == 1 && M.socket_closes == 1);  /* no fd leak on error */
}

static void test_create_bridge_setdelay_fail(void)
{
	g_fail_req = SIOCDEVPRIVATE;
	M.ioctl_hook = ioctl_fail_one;
	/* forward-delay failure is non-fatal (legacy SIOCDEVPRIVATE interface);
	 * the bridge was already created, so the call still succeeds */
	CHECK(_create_bridge("pan1") == 0);
	CHECK(M.socket_opens == 1 && M.socket_closes == 1);
}

/* ================================================================== */
/* _destroy_bridge                                                    */
/* ================================================================== */
static void test_destroy_bridge_success(void)
{
	M.ioctl_hook = ioctl_ok;
	CHECK(_destroy_bridge("pan1") == 0);
	CHECK(M.socket_opens == 1 && M.socket_closes == 1);
}

static void test_destroy_bridge_socket_fail(void)
{
	M.socket_ret = -1;
	CHECK(_destroy_bridge("pan1") < 0);
}

static void test_destroy_bridge_getflags_fail(void)
{
	g_fail_req = SIOCGIFFLAGS;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(_destroy_bridge("pan1") < 0);
	CHECK(M.socket_closes == 1);
}

static void test_destroy_bridge_setflags_fail(void)
{
	g_fail_req = SIOCSIFFLAGS;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(_destroy_bridge("pan1") < 0);
	CHECK(M.socket_closes == 1);
}

static void test_destroy_bridge_delbr_fail(void)
{
	g_fail_req = SIOCBRDELBR;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(_destroy_bridge("pan1") < 0);
	CHECK(M.socket_closes == 1);
}

/* ================================================================== */
/* find_conn                                                          */
/* ================================================================== */
static struct hci_conn_info g_match_ci;  /* zeroed bdaddr matches str2ba mock */

static int ioctl_connlist(int fd, unsigned long req, void *arg)
{
	(void) fd;
	if (req == HCIGETCONNLIST) {
		struct hci_conn_list_req *cl = arg;
		cl->conn_num = 1;
		memset(&cl->conn_info[0], 0, sizeof(struct hci_conn_info));
		return 0;
	}
	return 0;
}

static int ioctl_connlist_nomatch(int fd, unsigned long req, void *arg)
{
	(void) fd;
	if (req == HCIGETCONNLIST) {
		struct hci_conn_list_req *cl = arg;
		cl->conn_num = 1;
		memset(&cl->conn_info[0], 0, sizeof(struct hci_conn_info));
		cl->conn_info[0].bdaddr.b[0] = 0xAA;  /* won't match the zeroed target */
		return 0;
	}
	return 0;
}

static void test_find_conn_match(void)
{
	bdaddr_t want;
	memset(&want, 0, sizeof(want));
	M.ioctl_hook = ioctl_connlist;
	CHECK(find_conn(5, 0, (long)(intptr_t) &want) == 1);
}

static void test_find_conn_no_match(void)
{
	bdaddr_t want;
	memset(&want, 0, sizeof(want));
	M.ioctl_hook = ioctl_connlist_nomatch;
	CHECK(find_conn(5, 0, (long)(intptr_t) &want) == 0);
}

static void test_find_conn_ioctl_fail(void)
{
	bdaddr_t want;
	memset(&want, 0, sizeof(want));
	g_fail_req = HCIGETCONNLIST;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(find_conn(5, 0, (long)(intptr_t) &want) == 0);
}

static int ioctl_connlist_hostile(int fd, unsigned long req, void *arg)
{
	(void) fd;
	if (req == HCIGETCONNLIST) {
		struct hci_conn_list_req *cl = arg;
		int i;
		/* claim more connections than the 10 entries find_conn allocated;
		 * without the clamp the scan loop would read out of bounds (ASan) */
		cl->conn_num = 12;
		for (i = 0; i < 10; i++) {
			memset(&cl->conn_info[i], 0, sizeof(struct hci_conn_info));
			cl->conn_info[i].bdaddr.b[0] = 0xAA;  /* no match */
		}
		return 0;
	}
	return 0;
}

static void test_find_conn_hostile_conn_num(void)
{
	bdaddr_t want;
	memset(&want, 0, sizeof(want));
	M.ioctl_hook = ioctl_connlist_hostile;
	CHECK(find_conn(5, 0, (long)(intptr_t) &want) == 0);
}

static void test_find_conn_malloc_fail(void)
{
	bdaddr_t want;
	memset(&want, 0, sizeof(want));
	M.malloc_fail_at = 1;
	CHECK(find_conn(5, 0, (long)(intptr_t) &want) == 0);
}

/* ================================================================== */
/* connection_init / rssi / tpl / close                               */
/* ================================================================== */
static int ioctl_conninfo(int fd, unsigned long req, void *arg)
{
	(void) fd;
	if (req == HCIGETCONNINFO) {
		struct hci_conn_info_req *cr = arg;
		cr->conn_info->handle = 42;
		return 0;
	}
	return 0;
}

static void test_connection_init_success(void)
{
	struct conn_info_handles ci;
	M.ioctl_hook = ioctl_conninfo;
	CHECK(connection_init(0, "00:11:22:33:44:55", &ci) == 1);
	CHECK(ci.dd == M.hci_open_ret);
	CHECK(ci.handle == 42);
	CHECK(M.hci_closes == 0);  /* kept open for the caller */
}

static void test_connection_init_bad_address(void)
{
	struct conn_info_handles ci;
	M.str2ba_ret = -1;
	CHECK(connection_init(0, "bogus", &ci) == ERR_INVALID_ADDRESS);
}

static void test_connection_init_not_connected(void)
{
	struct conn_info_handles ci;
	M.hci_dev_id_ret = -1;  /* hci_for_each_dev finds nothing */
	CHECK(connection_init(-1, "00:11:22:33:44:55", &ci) == ERR_NOT_CONNECTED);
	CHECK(M.hci_closes == 0);
}

static void test_connection_init_open_fail(void)
{
	struct conn_info_handles ci;
	M.hci_open_ret = -1;
	CHECK(connection_init(0, "00:11:22:33:44:55", &ci) == ERR_HCI_DEV_OPEN_FAILED);
}

static void test_connection_init_malloc_fail(void)
{
	struct conn_info_handles ci;
	M.malloc_fail_at = 1;
	CHECK(connection_init(0, "00:11:22:33:44:55", &ci) == ERR_CANNOT_ALLOCATE);
	CHECK(M.hci_closes == 1);  /* device closed on the malloc-failure path */
}

static void test_connection_init_conninfo_fail(void)
{
	struct conn_info_handles ci;
	g_fail_req = HCIGETCONNINFO;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(connection_init(0, "00:11:22:33:44:55", &ci) == ERR_GET_CONN_INFO_FAILED);
	CHECK(M.hci_closes == 1);  /* device closed on the ioctl-failure path (leak fix) */
}

static void test_connection_get_rssi(void)
{
	struct conn_info_handles ci = { .handle = 1, .dd = 2 };
	int8_t rssi = 0;
	M.hci_rssi_val = -57;
	CHECK(connection_get_rssi(&ci, &rssi) == 1);
	CHECK(rssi == -57);
	M.hci_rssi_ret = -1;
	CHECK(connection_get_rssi(&ci, &rssi) == ERR_READ_RSSI_FAILED);
}

static void test_connection_get_tpl(void)
{
	struct conn_info_handles ci = { .handle = 1, .dd = 2 };
	int8_t tpl = 0;
	M.hci_tpl_val = 4;
	CHECK(connection_get_tpl(&ci, &tpl, 0) == 1);
	CHECK(tpl == 4);
	M.hci_tpl_ret = -1;
	CHECK(connection_get_tpl(&ci, &tpl, 0) == ERR_READ_TPL_FAILED);
}

static void test_connection_close(void)
{
	struct conn_info_handles ci = { .handle = 1, .dd = 2 };
	CHECK(connection_close(&ci) == 1);
	CHECK(M.hci_closes == 1);
	CHECK(ci.dd == -1);  /* descriptor invalidated */
}

static void test_connection_close_idempotent(void)
{
	/* a second close (or a close before init, dd == -1) must be a no-op */
	struct conn_info_handles ci = { .handle = 1, .dd = 2 };
	CHECK(connection_close(&ci) == 1);
	CHECK(connection_close(&ci) == 1);
	CHECK(M.hci_closes == 1);
}

/* ================================================================== */
/* get_rfcomm_list                                                    */
/* ================================================================== */
static int ioctl_devlist_ok(int fd, unsigned long req, void *arg)
{
	(void) fd; (void) req; (void) arg;
	return 0;
}

static void test_get_rfcomm_list_success(void)
{
	struct rfcomm_dev_list_req *dl = NULL;
	M.ioctl_hook = ioctl_devlist_ok;
	CHECK(get_rfcomm_list(&dl) == 1);
	CHECK(dl != NULL);
	CHECK(dl->dev_num == RFCOMM_MAX_DEV);
	free(dl);
	CHECK(M.socket_opens == 1 && M.socket_closes == 1);
}

static void test_get_rfcomm_list_socket_fail(void)
{
	struct rfcomm_dev_list_req *dl = NULL;
	M.socket_ret = -1;
	CHECK(get_rfcomm_list(&dl) == ERR_SOCKET_FAILED);
}

static void test_get_rfcomm_list_malloc_fail(void)
{
	struct rfcomm_dev_list_req *dl = NULL;
	M.malloc_fail_at = 1;
	CHECK(get_rfcomm_list(&dl) == ERR_CANNOT_ALLOCATE);
	CHECK(M.socket_closes == 1);
}

static void test_get_rfcomm_list_ioctl_fail(void)
{
	struct rfcomm_dev_list_req *dl = NULL;
	g_fail_req = RFCOMMGETDEVLIST;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(get_rfcomm_list(&dl) == ERR_GET_RFCOMM_LIST_FAILED);
	CHECK(M.socket_closes == 1);  /* socket closed, dl freed */
}

/* ================================================================== */
/* create_rfcomm_device                                               */
/* ================================================================== */
static int ioctl_createdev(int fd, unsigned long req, void *arg)
{
	(void) fd; (void) arg;
	if (req == RFCOMMCREATEDEV)
		return 3;  /* device id */
	return 0;
}

static void test_create_rfcomm_success(void)
{
	M.ioctl_hook = ioctl_createdev;
	CHECK(create_rfcomm_device("00:00:00:00:00:00", "11:11:11:11:11:11", 1) == 3);
	CHECK(M.socket_opens == 1 && M.socket_closes == 1);
}

static void test_create_rfcomm_socket_fail(void)
{
	M.socket_ret = -1;
	CHECK(create_rfcomm_device("00:00:00:00:00:00", "11:11:11:11:11:11", 1) == ERR_SOCKET_FAILED);
}

static void test_create_rfcomm_bad_local(void)
{
	M.str2ba_ret = -1;
	CHECK(create_rfcomm_device("bad", "11:11:11:11:11:11", 1) == ERR_INVALID_ADDRESS);
	CHECK(M.socket_closes == 1);
}

static void test_create_rfcomm_bad_remote(void)
{
	M.str2ba_fail_at = 2;  /* local ok, remote invalid */
	CHECK(create_rfcomm_device("00:00:00:00:00:00", "bad", 1) == ERR_INVALID_ADDRESS);
	CHECK(M.socket_closes == 1);
}

static void test_create_rfcomm_bind_fail(void)
{
	M.bind_ret = -1;
	CHECK(create_rfcomm_device("00:00:00:00:00:00", "11:11:11:11:11:11", 1) == ERR_BIND_FAILED);
	CHECK(M.socket_closes == 1);
}

static void test_create_rfcomm_connect_fail(void)
{
	M.connect_ret = -1;
	CHECK(create_rfcomm_device("00:00:00:00:00:00", "11:11:11:11:11:11", 1) == ERR_CONNECT_FAILED);
	CHECK(M.socket_closes == 1);
}

static void test_create_rfcomm_createdev_fail(void)
{
	g_fail_req = RFCOMMCREATEDEV;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(create_rfcomm_device("00:00:00:00:00:00", "11:11:11:11:11:11", 1) == ERR_CREATE_DEV_FAILED);
	CHECK(M.socket_closes == 1);
}

/* ================================================================== */
/* release_rfcomm_device                                              */
/* ================================================================== */
static void test_release_rfcomm_success(void)
{
	M.ioctl_hook = ioctl_ok;
	CHECK(release_rfcomm_device(3) == 0);
	CHECK(M.socket_closes == 1);
}

static void test_release_rfcomm_socket_fail(void)
{
	M.socket_ret = -1;
	CHECK(release_rfcomm_device(3) == ERR_SOCKET_FAILED);
}

static void test_release_rfcomm_ioctl_fail(void)
{
	g_fail_req = RFCOMMRELEASEDEV;
	M.ioctl_hook = ioctl_fail_one;
	CHECK(release_rfcomm_device(3) == ERR_RELEASE_DEV_FAILED);
	CHECK(M.socket_closes == 1);
}

/* ================================================================== */
/* get_rfcomm_channel                                                 */
/* ================================================================== */
static void test_get_rfcomm_channel_connect_fail(void)
{
	M.sdp_session_ret = NULL;
	CHECK(get_rfcomm_channel(0x1101, "00:11:22:33:44:55") == 0);
}

static void test_get_rfcomm_channel_bad_address(void)
{
	M.str2ba_ret = -1;
	CHECK(get_rfcomm_channel(0x1101, "bad") == 0);
}

static void test_get_rfcomm_channel_search_fail(void)
{
	M.sdp_search_ret = -1;
	CHECK(get_rfcomm_channel(0x1101, "00:11:22:33:44:55") == 0);
	/* search_list + attrid_list must still be freed (no leak) */
	CHECK(M.sdp_nodes_alloced == M.sdp_nodes_freed);
	CHECK(M.sdp_session_closed == 1);
}

static void test_get_rfcomm_channel_extracts_channel(void)
{
	/* Build: response_list -> [rec]; get_access_protos -> protos -> [pds];
	 * pds -> [d(uuid16), d(uint8=channel 5)] */
	static sdp_data_t d_uuid, d_chan;
	memset(&d_uuid, 0, sizeof(d_uuid));
	memset(&d_chan, 0, sizeof(d_chan));
	d_uuid.dtd = SDP_UUID16;
	d_uuid.next = &d_chan;
	d_chan.dtd = SDP_UINT8;
	d_chan.val.int8 = 5;
	d_chan.next = NULL;

	sdp_record_t *rec = __real_malloc(sizeof(sdp_record_t));
	M.sdp_response = node(rec, NULL);

	sdp_list_t *pds = node(&d_uuid, NULL);
	M.sdp_protos = node(pds, NULL);

	CHECK(get_rfcomm_channel(0x1101, "00:11:22:33:44:55") == 5);
	/* every list node freed, record freed, session closed: no leaks */
	CHECK(M.sdp_nodes_alloced == M.sdp_nodes_freed);
	CHECK(M.sdp_records_freed == 1);
	CHECK(M.sdp_session_closed == 1);
}

static void test_get_rfcomm_channel_no_rfcomm_proto(void)
{
	static sdp_data_t d_uuid;
	memset(&d_uuid, 0, sizeof(d_uuid));
	d_uuid.dtd = SDP_UUID16;
	d_uuid.next = NULL;

	sdp_record_t *rec = __real_malloc(sizeof(sdp_record_t));
	M.sdp_response = node(rec, NULL);
	sdp_list_t *pds = node(&d_uuid, NULL);
	M.sdp_protos = node(pds, NULL);
	M.sdp_uuid_to_proto_ret = 0;  /* not RFCOMM */

	CHECK(get_rfcomm_channel(0x1101, "00:11:22:33:44:55") == 0);
	CHECK(M.sdp_nodes_alloced == M.sdp_nodes_freed);
}

static void test_get_rfcomm_channel_get_protos_fail(void)
{
	sdp_record_t *rec = __real_malloc(sizeof(sdp_record_t));
	M.sdp_response = node(rec, NULL);
	M.sdp_get_protos_ret = -1;  /* sdp_get_access_protos fails -> record skipped */

	CHECK(get_rfcomm_channel(0x1101, "00:11:22:33:44:55") == 0);
	CHECK(M.sdp_nodes_alloced == M.sdp_nodes_freed);
	CHECK(M.sdp_records_freed == 1);
}

/* ================================================================== */
/* Fuzz: string handling must not over-read under ASan                */
/* ================================================================== */
static void fuzz_bridge_names(void)
{
	/* Names shorter than IFNAMSIZ allocated to their exact length so any
	 * read past the terminator lands in an ASan redzone. Validates the
	 * strncpy fix (the old memcpy(.., IFNAMSIZ) would over-read here). */
	const char *samples[] = { "", "a", "br0", "pan1", "verylonginterfacename1234567890" };
	M.ioctl_hook = ioctl_ok;
	for (unsigned i = 0; i < sizeof(samples) / sizeof(samples[0]); i++) {
		size_t n = strlen(samples[i]);
		char *name = __real_malloc(n + 1);
		memcpy(name, samples[i], n + 1);
		reset_mocks();
		M.ioctl_hook = ioctl_ok;
		(void) _create_bridge(name);
		reset_mocks();
		M.ioctl_hook = ioctl_ok;
		(void) _destroy_bridge(name);
		free(name);
	}
	CHECK(1);  /* reaching here under ASan with no abort is the assertion */
}

static void fuzz_addresses(void)
{
	const char *addrs[] = { "", "x", "00:11:22:33:44:55", "::::::::::::::::::::",
				"not-an-address-but-quite-long-indeed" };
	for (unsigned i = 0; i < sizeof(addrs) / sizeof(addrs[0]); i++) {
		struct conn_info_handles ci;
		reset_mocks();
		M.ioctl_hook = ioctl_conninfo;
		(void) connection_init(0, addrs[i], &ci);
		reset_mocks();
		M.ioctl_hook = ioctl_createdev;
		(void) create_rfcomm_device(addrs[i], addrs[i], 1);
		reset_mocks();
		M.sdp_session_ret = NULL;
		(void) get_rfcomm_channel(0x1101, addrs[i]);
	}
	CHECK(1);
}

/* ================================================================== */
int main(void)
{
	RUN(test_tv_to_jiffies);

	RUN(test_create_bridge_success);
	RUN(test_create_bridge_socket_fail);
	RUN(test_create_bridge_addbr_fail);
	RUN(test_create_bridge_setdelay_fail);

	RUN(test_destroy_bridge_success);
	RUN(test_destroy_bridge_socket_fail);
	RUN(test_destroy_bridge_getflags_fail);
	RUN(test_destroy_bridge_setflags_fail);
	RUN(test_destroy_bridge_delbr_fail);

	RUN(test_find_conn_match);
	RUN(test_find_conn_no_match);
	RUN(test_find_conn_ioctl_fail);
	RUN(test_find_conn_hostile_conn_num);
	RUN(test_find_conn_malloc_fail);

	RUN(test_connection_init_success);
	RUN(test_connection_init_bad_address);
	RUN(test_connection_init_not_connected);
	RUN(test_connection_init_open_fail);
	RUN(test_connection_init_malloc_fail);
	RUN(test_connection_init_conninfo_fail);
	RUN(test_connection_get_rssi);
	RUN(test_connection_get_tpl);
	RUN(test_connection_close);
	RUN(test_connection_close_idempotent);

	RUN(test_get_rfcomm_list_success);
	RUN(test_get_rfcomm_list_socket_fail);
	RUN(test_get_rfcomm_list_malloc_fail);
	RUN(test_get_rfcomm_list_ioctl_fail);

	RUN(test_create_rfcomm_success);
	RUN(test_create_rfcomm_socket_fail);
	RUN(test_create_rfcomm_bad_local);
	RUN(test_create_rfcomm_bad_remote);
	RUN(test_create_rfcomm_bind_fail);
	RUN(test_create_rfcomm_connect_fail);
	RUN(test_create_rfcomm_createdev_fail);

	RUN(test_release_rfcomm_success);
	RUN(test_release_rfcomm_socket_fail);
	RUN(test_release_rfcomm_ioctl_fail);

	RUN(test_get_rfcomm_channel_connect_fail);
	RUN(test_get_rfcomm_channel_bad_address);
	RUN(test_get_rfcomm_channel_search_fail);
	RUN(test_get_rfcomm_channel_extracts_channel);
	RUN(test_get_rfcomm_channel_no_rfcomm_proto);
	RUN(test_get_rfcomm_channel_get_protos_fail);

	RUN(fuzz_bridge_names);
	RUN(fuzz_addresses);

	fprintf(stderr, "\n%d checks, %d failures\n", g_checks, g_failures);
	return g_failures ? 1 : 0;
}

#include "rpc-negotiate.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <sys/socket.h>
#include <unistd.h>

#undef NDEBUG
#include <assert.h>

static int tests_passed = 0;
static int tests_failed = 0;

#define TEST(name) void test_##name(void)
#define RUN_TEST(name)                    \
	do {                               \
		printf("Running %s... ", #name); \
		test_##name();             \
		printf("PASSED\n");        \
		tests_passed++;            \
	} while (0)

static void test_encode_decode_roundtrip(void)
{
	rpc_negotiate_header_t req;
	memset(&req, 0, sizeof(req));
	memcpy(req.magic, RPC_NEG_MAGIC, RPC_NEG_MAGIC_LEN);
	req.version = RPC_NEG_VERSION;
	req.capability = RPC_CAP_ENCRYPT | RPC_CAP_SM | RPC_CAP_VER_MATCH;

	uint8_t wire[RPC_NEG_HEADER_LEN];
	assert(rpc_negotiate_encode(&req, wire, sizeof(wire)) ==
	       RPC_NEG_HEADER_LEN);

	rpc_negotiate_header_t out;
	memset(&out, 0, sizeof(out));
	assert(rpc_negotiate_decode(&out, wire, sizeof(wire)) == 0);
	assert(memcmp(out.magic, RPC_NEG_MAGIC, RPC_NEG_MAGIC_LEN) == 0);
	assert(out.version == RPC_NEG_VERSION);
	assert(out.capability ==
	       (RPC_CAP_ENCRYPT | RPC_CAP_SM | RPC_CAP_VER_MATCH));
	assert(out.result == 0);
}

static void test_decode_rejects_bad_magic(void)
{
	uint8_t wire[RPC_NEG_HEADER_LEN];
	memset(wire, 0, sizeof(wire));
	memcpy(wire, "XXXX-NEG1", RPC_NEG_MAGIC_LEN);

	rpc_negotiate_header_t out;
	assert(rpc_negotiate_decode(&out, wire, sizeof(wire)) != 0);
	(void)out;
}

static void test_decode_rejects_bad_version(void)
{
	rpc_negotiate_header_t req;
	memset(&req, 0, sizeof(req));
	memcpy(req.magic, RPC_NEG_MAGIC, RPC_NEG_MAGIC_LEN);
	req.version = 0xFE;
	req.capability = 0;

	uint8_t wire[RPC_NEG_HEADER_LEN];
	assert(rpc_negotiate_encode(&req, wire, sizeof(wire)) ==
	       RPC_NEG_HEADER_LEN);

	rpc_negotiate_header_t out;
	assert(rpc_negotiate_decode(&out, wire, sizeof(wire)) != 0);
	(void)out;
	(void)wire;
}

/* ---- 判定逻辑（对齐 PRD 实现决策） ---- */

static void test_decide_disabled_always_plain(void)
{
	/* 开关关闭 → 明文，无论双方能力 */
	assert(rpc_decide_transport(0, 1, 1, 1, 1) == RPC_TRANSPORT_PLAIN);
	assert(rpc_decide_transport(0, 1, 0, 1, 0) == RPC_TRANSPORT_PLAIN);
	assert(rpc_decide_transport(0, 0, 0, 0, 0) == RPC_TRANSPORT_PLAIN);
}

static void test_decide_default_sm_upgrade(void)
{
	/* 开关开启 + 默认国密（sm_ready=1）+ 双方国密 → 升级国密 */
	assert(rpc_decide_transport(1, 1, 0, 1, 0) ==
	       RPC_TRANSPORT_TLS_SM);
	assert(rpc_decide_transport(1, 1, 1, 1, 1) ==
	       RPC_TRANSPORT_TLS_SM);
}

static void test_decide_sm_missing_enc004(void)
{
	/* 开关开启 + 国密就绪 + 目标缺国密 → ENC-004 */
	assert(rpc_decide_transport(1, 1, 0, 0, 0) == RPC_TRANSPORT_REJECT);
	assert(rpc_decide_transport(1, 1, 1, 0, 1) == RPC_TRANSPORT_REJECT);
}

static void test_decide_explicit_tls_upgrade(void)
{
	/* 显式常规套件（sm_ready=0, tls_ready=1）+ 双方常规 → 升级常规 */
	assert(rpc_decide_transport(1, 0, 1, 0, 1) ==
	       RPC_TRANSPORT_TLS_GENERIC);
	assert(rpc_decide_transport(1, 0, 1, 1, 1) ==
	       RPC_TRANSPORT_TLS_GENERIC);
}

static void test_decide_tls_missing_enc004(void)
{
	/* 显式常规 + 目标缺常规 → ENC-004 */
	assert(rpc_decide_transport(1, 0, 1, 0, 0) == RPC_TRANSPORT_REJECT);
}

static void test_decide_no_algo_enc004(void)
{
	/* 开关开启但本端无任何算法就绪 → ENC-004 */
	assert(rpc_decide_transport(1, 0, 0, 0, 0) == RPC_TRANSPORT_REJECT);
	assert(rpc_decide_transport(1, 0, 0, 1, 1) == RPC_TRANSPORT_REJECT);
}

/* ---- 协商 IO（socketpair 双线程配对） ---- */

struct neg_pair_args {
	int fd;
	int tls_enable;
	int sm_ready;
	int tls_ready;
	int result;
	int upgrade;
};

static void *client_pair(void *arg)
{
	struct neg_pair_args *a = (struct neg_pair_args *)arg;
	int up = -99;
	a->result = rpc_negotiate_client(a->fd, a->tls_enable, a->sm_ready,
					 a->tls_ready, &up);
	a->upgrade = up;
	return NULL;
}

static void *server_pair(void *arg)
{
	struct neg_pair_args *a = (struct neg_pair_args *)arg;
	int up = -99;
	a->result = rpc_negotiate_server(a->fd, a->tls_enable, a->sm_ready,
					 a->tls_ready, &up);
	a->upgrade = up;
	return NULL;
}

static void run_pair(int c_enable, int c_sm, int c_tls, int s_enable,
		     int s_sm, int s_tls, int expect_cli, int expect_srv)
{
	int sv[2];
	assert(socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == 0);

	struct neg_pair_args cli, srv;
	memset(&cli, 0, sizeof(cli));
	memset(&srv, 0, sizeof(srv));
	cli.fd = sv[0];
	cli.tls_enable = c_enable;
	cli.sm_ready = c_sm;
	cli.tls_ready = c_tls;
	srv.fd = sv[1];
	srv.tls_enable = s_enable;
	srv.sm_ready = s_sm;
	srv.tls_ready = s_tls;

	pthread_t ct, st;
	assert(pthread_create(&ct, NULL, client_pair, &cli) == 0);
	assert(pthread_create(&st, NULL, server_pair, &srv) == 0);
	assert(pthread_join(ct, NULL) == 0);
	assert(pthread_join(st, NULL) == 0);
	close(sv[0]);
	close(sv[1]);

	assert(cli.result == expect_cli);
	assert(srv.result == expect_srv);
}

static void test_neg_io_plain(void)
{
	/* 双方开关关闭 → 明文 */
	run_pair(0, 1, 0, 0, 1, 0, RPC_TRANSPORT_PLAIN, RPC_TRANSPORT_PLAIN);
}

static void test_neg_io_sm_upgrade(void)
{
	/* 双方开关开启 + 默认国密就绪 → 升级国密 */
	run_pair(1, 1, 0, 1, 1, 0, RPC_TRANSPORT_TLS_SM,
		 RPC_TRANSPORT_TLS_SM);
}

static void test_neg_io_tls_upgrade(void)
{
	/* 双方显式常规套件 → 升级常规 */
	run_pair(1, 0, 1, 1, 0, 1, RPC_TRANSPORT_TLS_GENERIC,
		 RPC_TRANSPORT_TLS_GENERIC);
}

static void test_neg_io_sm_missing_reject(void)
{
	/* 客户端要求国密，服务端无能力 → 服务端 REJECT，客户端 REJECT */
	run_pair(1, 1, 0, 1, 0, 0, RPC_TRANSPORT_REJECT,
		 RPC_TRANSPORT_REJECT);
}

static void test_neg_io_client_plain_server_encrypt(void)
{
	/* 客户端开关关闭（明文），服务端开关开启 → 明文（客户端决定） */
	run_pair(0, 1, 0, 1, 1, 0, RPC_TRANSPORT_PLAIN,
		 RPC_TRANSPORT_PLAIN);
}

static void *server_pair_err(void *arg)
{
	struct neg_pair_args *a = (struct neg_pair_args *)arg;
	int up = -99;
	a->result = rpc_negotiate_server(a->fd, a->tls_enable, a->sm_ready,
					 a->tls_ready, &up);
	a->upgrade = up;
	return NULL;
}

static void test_neg_server_bad_header(void)
{
	/* 客户端发损坏协商头（坏 magic）→ 服务端 RPC_NEG_ERR_VER，
	 * 验证 rpc-server 损坏头拒绝（ENC-004）的判定依据 */
	int sv[2];
	assert(socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == 0);

	struct neg_pair_args srv;
	memset(&srv, 0, sizeof(srv));
	srv.fd = sv[1];
	srv.tls_enable = 1;
	srv.sm_ready = 1;
	srv.tls_ready = 0;

	pthread_t st;
	assert(pthread_create(&st, NULL, server_pair_err, &srv) == 0);
	usleep(50000);

	uint8_t bad[RPC_NEG_HEADER_LEN];
	memset(bad, 0xAB, sizeof(bad));
	memcpy(bad, "NON-NEG1", 8);
	write(sv[0], bad, sizeof(bad));

	assert(pthread_join(st, NULL) == 0);
	close(sv[0]);
	close(sv[1]);

	assert(srv.result == RPC_NEG_ERR_VER);
}

static void test_neg_server_half_header_timeout(void)
{
	/* 客户端只发 1 字节后保持连接静默 → 服务端读头剩余字节超时
	 * （RPC_NEG_ERR_TIMEOUT），即"存量明文客户端"判定路径（非损坏头） */
	int sv[2];
	assert(socketpair(AF_UNIX, SOCK_STREAM, 0, sv) == 0);

	struct neg_pair_args srv;
	memset(&srv, 0, sizeof(srv));
	srv.fd = sv[1];
	srv.tls_enable = 1;
	srv.sm_ready = 1;
	srv.tls_ready = 0;

	pthread_t st;
	assert(pthread_create(&st, NULL, server_pair_err, &srv) == 0);
	usleep(50000);

	write(sv[0], "A", 1);

	assert(pthread_join(st, NULL) == 0);
	close(sv[0]);
	close(sv[1]);

	assert(srv.result == RPC_NEG_ERR_TIMEOUT);
}

int main(void)
{
	RUN_TEST(encode_decode_roundtrip);
	RUN_TEST(decode_rejects_bad_magic);
	RUN_TEST(decode_rejects_bad_version);
	RUN_TEST(decide_disabled_always_plain);
	RUN_TEST(decide_default_sm_upgrade);
	RUN_TEST(decide_sm_missing_enc004);
	RUN_TEST(decide_explicit_tls_upgrade);
	RUN_TEST(decide_tls_missing_enc004);
	RUN_TEST(decide_no_algo_enc004);
	RUN_TEST(neg_io_plain);
	RUN_TEST(neg_io_sm_upgrade);
	RUN_TEST(neg_io_tls_upgrade);
	RUN_TEST(neg_io_sm_missing_reject);
	RUN_TEST(neg_io_client_plain_server_encrypt);
	RUN_TEST(neg_server_bad_header);
	RUN_TEST(neg_server_half_header_timeout);

	printf("rpc_negotiate_test: %d passed, %d failed\n", tests_passed,
	       tests_failed);
	return tests_failed == 0 ? 0 : 1;
}
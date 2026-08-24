#include <cassert>
#include <cstdio>
#include <cstring>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

#include "rpc-protocol.h"
#include "rpc-io.h"
#include "rpc-config.h"
#include "tls_cert.h"

/* ---- helpers ---- */

static void test_handshake_codec()
{
	msg_handshake_t in = {};
	msg_handshake_t net = {};
	msg_handshake_t out = {};
	in.flags = HS_FLAG_MTLS_REQUEST;
	in.algorithm = HS_ALG_AES_256_GCM_SHA384;
	strncpy(in.ca_cn, "Test CA", sizeof(in.ca_cn) - 1);
	msg_handshake_hton(&in, &net);
	assert(net.uiMT == htonl(MT_HANDSHAKE));
	msg_handshake_ntoh(&out, &net);
	assert(out.uiMT == MT_HANDSHAKE);
	assert(out.flags == HS_FLAG_MTLS_REQUEST);
	assert(out.algorithm == HS_ALG_AES_256_GCM_SHA384);
	assert(strcmp(out.ca_cn, "Test CA") == 0);
	printf("[PASS] handshake codec\n");
}

static void test_handshake_resp_codec()
{
	msg_handshake_resp_t in = {};
	msg_handshake_resp_t net = {};
	msg_handshake_resp_t out = {};
	in.result = HS_OK_MTLS;
	in.algorithm = HS_ALG_SM4_GCM_SM3;
	strncpy(in.ca_cn, "MyCA", sizeof(in.ca_cn) - 1);
	msg_handshake_resp_hton(&in, &net);
	assert(net.uiMT == htonl(MT_HANDSHAKE_RESP));
	msg_handshake_resp_ntoh(&out, &net);
	assert(out.uiMT == MT_HANDSHAKE_RESP);
	assert(out.result == HS_OK_MTLS);
	assert(out.algorithm == HS_ALG_SM4_GCM_SM3);
	assert(strcmp(out.ca_cn, "MyCA") == 0);
	printf("[PASS] handshake_resp codec\n");
}

static void test_algorithm_mapping()
{
	assert(hs_algorithm_from_name("TLS_AES_256_GCM_SHA384") ==
	       HS_ALG_AES_256_GCM_SHA384);
	assert(hs_algorithm_from_name("TLS_SM4_GCM_SM3") == HS_ALG_SM4_GCM_SM3);
	assert(hs_algorithm_from_name("sm2") == HS_ALG_SM4_GCM_SM3);
	assert(hs_algorithm_from_name("ed25519") == HS_ALG_AES_256_GCM_SHA384);
	assert(strcmp(hs_algorithm_name(HS_ALG_AES_256_GCM_SHA384),
		      "TLS_AES_256_GCM_SHA384") == 0);
	assert(strcmp(hs_algorithm_name(HS_ALG_SM4_GCM_SM3), "TLS_SM4_GCM_SM3") ==
	       0);
	printf("[PASS] algorithm mapping\n");
}

/* ---- 模拟服务端循环内握手逻辑 ---- */

static int server_handle_one(rpc_io_t *io)
{
	char buf[MSG_BUFF_LEN];
	int n = rpc_recv_io(io, buf, sizeof(buf), 0);
	if (n <= 0)
		return -1;
	msg_base_t *base = (msg_base_t *)buf;
	if (ntohl(base->uiMT) == MT_HANDSHAKE) {
		msg_handshake_t hs = {};
		msg_handshake_ntoh(&hs, (msg_handshake_t *)buf);
		bool want = (hs.flags & HS_FLAG_MTLS_REQUEST) != 0;
		if (g_rpc_config->mtls_enabled && !want) {
			msg_handshake_resp_t eh = {}, en = {};
			eh.result = HS_ERR_MTLS_REQUIRED;
			msg_handshake_resp_hton(&eh, &en);
			rpc_send_io(io, &en, sizeof(en), 0);
			return -1;
		}
		if (want && g_rpc_config->mtls_enabled) {
			/* 简化：不做真实 TLS，直接回 OK_MTLS */
			msg_handshake_resp_t rh = {}, rn = {};
			rh.result = HS_OK_MTLS;
			rh.algorithm = hs_algorithm_from_name(
				g_rpc_config->tls_algorithm);
			msg_handshake_resp_hton(&rh, &rn);
			rpc_send_io(io, &rn, sizeof(rn), 0);
			return 1; /* handshake done */
		}
		msg_handshake_resp_t rh = {}, rn = {};
		rh.result = HS_OK_PLAIN;
		msg_handshake_resp_hton(&rh, &rn);
		rpc_send_io(io, &rn, sizeof(rn), 0);
		return 1;
	}
	if (g_rpc_config->mtls_enabled) {
		msg_handshake_resp_t eh = {}, en = {};
		eh.result = HS_ERR_MTLS_REQUIRED;
		msg_handshake_resp_hton(&eh, &en);
		rpc_send_io(io, &en, sizeof(en), 0);
		return -1;
	}
	/* 明文业务：回显 GET_TIME */
	if (ntohl(base->uiMT) == MT_GET_TIME) {
		msg_get_time_resp_t resp = {}, net = {};
		resp.timestamp = 12345;
		msg_get_time_resp_hton(&resp, &net);
		rpc_send_io(io, &net, sizeof(net), 0);
		return 0;
	}
	return -1;
}

static void test_plain_both_disabled()
{
	rpc_config cfg = {};
	g_rpc_config = &cfg;
	cfg.mtls_enabled = 0;

	int fds[2];
	assert(socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);

	pid_t pid = fork();
	if (pid == 0) {
		close(fds[0]);
		rpc_io_t io;
		rpc_io_init_plain(&io, fds[1]);
		/* 循环内处理：首包是 GET_TIME，非 HANDSHAKE，且 mtls 关闭 → 直接处理 */
		assert(server_handle_one(&io) == 0);
		rpc_io_cleanup(&io);
		close(fds[1]);
		_exit(0);
	}
	close(fds[1]);
	g_rpc_config = &cfg;
	rpc_io_t cio;
	rpc_io_init_plain(&cio, fds[0]);
	assert(rpc_handshake_client_negotiate(&cio) == 0);
	assert(cio.tssl == nullptr);
	msg_get_time_t req = {}, net = {};
	msg_get_time_hton(&req, &net);
	assert(rpc_send_io(&cio, &net, sizeof(net), 0) > 0);
	char buf[MSG_BUFF_LEN];
	int n = rpc_recv_io(&cio, buf, sizeof(buf), 0);
	assert(n > 0);
	msg_get_time_resp_t resp = {};
	msg_get_time_resp_ntoh(&resp, (msg_get_time_resp_t *)buf);
	assert(resp.uiMT == MT_GET_TIME_RESP);
	assert(resp.timestamp == 12345);
	rpc_io_cleanup(&cio);
	close(fds[0]);
	int st = 0;
	waitpid(pid, &st, 0);
	assert(WIFEXITED(st) && WEXITSTATUS(st) == 0);
	g_rpc_config = nullptr;
	printf("[PASS] plain both disabled\n");
}

static void test_server_mtls_reject_plain()
{
	rpc_config scfg = {};
	scfg.mtls_enabled = 1;
	rpc_config ccfg = {};
	ccfg.mtls_enabled = 0;

	int fds[2];
	assert(socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);

	pid_t pid = fork();
	if (pid == 0) {
		close(fds[0]);
		g_rpc_config = &scfg;
		rpc_io_t io;
		rpc_io_init_plain(&io, fds[1]);
		int ret = server_handle_one(&io);
		assert(ret != 0);
		rpc_io_cleanup(&io);
		close(fds[1]);
		_exit(0);
	}
	close(fds[1]);
	g_rpc_config = &ccfg;
	rpc_io_t cio;
	rpc_io_init_plain(&cio, fds[0]);
	assert(rpc_handshake_client_negotiate(&cio) == 0);
	msg_get_time_t req = {}, net = {};
	msg_get_time_hton(&req, &net);
	assert(rpc_send_io(&cio, &net, sizeof(net), 0) > 0);
	char buf[MSG_BUFF_LEN];
	int n = rpc_recv_io(&cio, buf, sizeof(buf), 0);
	assert(n > 0);
	msg_handshake_resp_t host = {};
	msg_handshake_resp_ntoh(&host, (msg_handshake_resp_t *)buf);
	assert(host.result == HS_ERR_MTLS_REQUIRED);
	rpc_io_cleanup(&cio);
	close(fds[0]);
	int st = 0;
	waitpid(pid, &st, 0);
	assert(WIFEXITED(st) && WEXITSTATUS(st) == 0);
	g_rpc_config = nullptr;
	printf("[PASS] server mTLS reject plain\n");
}

static void test_client_handshake_server_plain()
{
	rpc_config scfg = {};
	scfg.mtls_enabled = 0;
	rpc_config ccfg = {};
	ccfg.mtls_enabled = 1;
	strncpy(ccfg.tls_algorithm, "TLS_AES_256_GCM_SHA384",
		sizeof(ccfg.tls_algorithm) - 1);

	int fds[2];
	assert(socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);

	pid_t pid = fork();
	if (pid == 0) {
		close(fds[0]);
		g_rpc_config = &scfg;
		rpc_io_t io;
		rpc_io_init_plain(&io, fds[1]);
		int ret = server_handle_one(&io);
		assert(ret == 1);
		rpc_io_cleanup(&io);
		close(fds[1]);
		_exit(0);
	}
	close(fds[1]);
	g_rpc_config = &ccfg;
	rpc_io_t cio;
	rpc_io_init_plain(&cio, fds[0]);
	int ret = rpc_handshake_client_negotiate(&cio);
	assert(ret == 0);
	assert(cio.tssl == nullptr);
	rpc_io_cleanup(&cio);
	close(fds[0]);
	int st = 0;
	waitpid(pid, &st, 0);
	assert(WIFEXITED(st) && WEXITSTATUS(st) == 0);
	g_rpc_config = nullptr;
	printf("[PASS] client handshake server plain\n");
}

int main()
{
	test_handshake_codec();
	test_handshake_resp_codec();
	test_algorithm_mapping();
	test_plain_both_disabled();
	test_server_mtls_reject_plain();
	test_client_handshake_server_plain();
	printf("rpc_own_handshake_test: ALL PASS\n");
	return 0;
}

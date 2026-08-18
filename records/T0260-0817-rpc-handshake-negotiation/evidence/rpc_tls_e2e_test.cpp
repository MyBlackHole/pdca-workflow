/* 端到端：真实 TCP + 协商（国密升级）+ TLS 握手 + 加密数据往返。
 * 验证 PRD"同连接内升级 TLS（国密）"与数据面加密。 */

#include "rpc-negotiate.h"
#include "rpc-io.h"
#include "../tls_cert.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#undef NDEBUG
#include <assert.h>

static const char *get_cert_dir(void)
{
	const char *dir = getenv("CERT_DIR");
	if (dir)
		return dir;
	return "/home/black/Public/aio/aio-tools/6200/F/139/libs/tests/certs";
}

static int create_listen(int port)
{
	int fd = socket(AF_INET, SOCK_STREAM, 0);
	assert(fd >= 0);
	struct sockaddr_in addr = { 0 };
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = inet_addr("127.0.0.1");
	addr.sin_port = htons(port);
	int opt = 1;
	setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
	assert(bind(fd, (struct sockaddr *)&addr, sizeof(addr)) == 0);
	assert(listen(fd, 1) == 0);
	return fd;
}

static int connect_to(int port)
{
	int fd = socket(AF_INET, SOCK_STREAM, 0);
	assert(fd >= 0);
	struct sockaddr_in addr = { 0 };
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = inet_addr("127.0.0.1");
	addr.sin_port = htons(port);
	assert(connect(fd, (struct sockaddr *)&addr, sizeof(addr)) == 0);
	return fd;
}

static void *server_thread(void *arg)
{
	int listen_fd = *(int *)arg;
	int cfd = accept(listen_fd, NULL, NULL);
	close(listen_fd);
	if (cfd < 0)
		return (void *)(long)-1;

	/* 服务端协商：开关开 + 国密就绪 → 期望升级国密 */
	int upgrade = -1;
	int neg = rpc_negotiate_server(cfd, 1, 1, 0, &upgrade);
	if (neg != RPC_TRANSPORT_TLS_SM)
		return (void *)(long)-2;

	SSL *ssl = tls_cert_server_handshake(cfd, NULL);
	if (!ssl)
		return (void *)(long)-3;

	char buf[128] = { 0 };
	int n = rpc_ssl_recv(ssl, buf, sizeof(buf), 0);
	if (n < 0)
		return (void *)(long)-4;
	if (strncmp(buf, "hello-client", 12) != 0)
		return (void *)(long)-5;

	const char *resp = "hello-server";
	if (rpc_ssl_send(ssl, (void *)resp, strlen(resp), 0) < 0)
		return (void *)(long)-6;

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(cfd);
	return (void *)(long)0;
}

static void test_e2e_sm_upgrade(void)
{
	tls_cert_cleanup();

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CHECK_NAME", "Server", 1);
	char ca_path[256], cert_path[256], key_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(cert_path, sizeof(cert_path), "%s/server.crt", get_cert_dir());
	snprintf(key_path, sizeof(key_path), "%s/server.key", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", cert_path, 1);
	setenv("RPC_TLS_SERVER_KEY", key_path, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);

	int port = 14446;
	int listen_fd = create_listen(port);

	pthread_t tid;
	assert(pthread_create(&tid, NULL, server_thread, &listen_fd) == 0);
	usleep(50000);

	int cfd = connect_to(port);

	/* 客户端协商：开关开 + 国密就绪 → 期望升级国密 */
	int upgrade = -1;
	int neg = rpc_negotiate_client(cfd, 1, 1, 0, &upgrade);
	assert(neg == RPC_TRANSPORT_TLS_SM);
	assert(upgrade == RPC_TRANSPORT_TLS_SM);

	SSL *ssl = tls_cert_client_handshake(cfd, NULL);
	assert(ssl != NULL);

	const char *msg = "hello-client";
	assert(rpc_ssl_send(ssl, (void *)msg, strlen(msg), 0) > 0);

	char buf[128] = { 0 };
	int n = rpc_ssl_recv(ssl, buf, sizeof(buf), 0);
	assert(n > 0);
	assert(strncmp(buf, "hello-server", 12) == 0);

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(cfd);

	void *thread_ret;
	pthread_join(tid, &thread_ret);
	assert((long)thread_ret == 0);

	tls_cert_cleanup();
	printf("e2e SM TLS upgrade + encrypted roundtrip OK\n");
}

/* 明文协商路径：双方开关关闭 → 明文，无 TLS 握手 */
static void *plain_server_thread(void *arg)
{
	int listen_fd = *(int *)arg;
	int cfd = accept(listen_fd, NULL, NULL);
	close(listen_fd);
	if (cfd < 0)
		return (void *)(long)-1;

	int upgrade = -1;
	int neg = rpc_negotiate_server(cfd, 0, 1, 0, &upgrade);
	if (neg != RPC_TRANSPORT_PLAIN)
		return (void *)(long)-2;

	char buf[128] = { 0 };
	int n = rpc_recv(cfd, buf, sizeof(buf), 0);
	if (n < 0)
		return (void *)(long)-3;
	if (strncmp(buf, "plain-msg", 9) != 0)
		return (void *)(long)-4;

	const char *resp = "plain-ack";
	if (rpc_send(cfd, (void *)resp, strlen(resp), 0) < 0)
		return (void *)(long)-5;

	close(cfd);
	return (void *)(long)0;
}

static void test_e2e_plain(void)
{
	tls_cert_cleanup();
	setenv("RPC_TLS_ENABLE", "0", 1);
	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);

	int port = 14447;
	int listen_fd = create_listen(port);

	pthread_t tid;
	assert(pthread_create(&tid, NULL, plain_server_thread, &listen_fd) == 0);
	usleep(50000);

	int cfd = connect_to(port);

	int upgrade = -1;
	int neg = rpc_negotiate_client(cfd, 0, 1, 0, &upgrade);
	assert(neg == RPC_TRANSPORT_PLAIN);

	const char *msg = "plain-msg";
	assert(rpc_send(cfd, (void *)msg, strlen(msg), 0) > 0);

	char buf[128] = { 0 };
	int n = rpc_recv(cfd, buf, sizeof(buf), 0);
	assert(n > 0);
	assert(strncmp(buf, "plain-ack", 9) == 0);

	close(cfd);

	void *thread_ret;
	pthread_join(tid, &thread_ret);
	assert((long)thread_ret == 0);

	tls_cert_cleanup();
	printf("e2e plain negotiation OK\n");
}

int main(void)
{
	test_e2e_sm_upgrade();
	test_e2e_plain();
	printf("rpc_tls_e2e_test: 2 passed, 0 failed\n");
	return 0;
}
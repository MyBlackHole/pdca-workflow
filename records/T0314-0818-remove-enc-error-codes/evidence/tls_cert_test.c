#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <signal.h>
#include <openssl/err.h>
#include <openssl/ssl.h>
#include <openssl/core_names.h>
#include "../tls_cert.h"
#include "../rdb-config.h"

#undef NDEBUG
#include <assert.h>

static int tests_passed = 0;
static int tests_failed = 0;

#define TEST(name) void test_##name(void)
#define RUN_TEST(name)                           \
	do {                                     \
		printf("Running %s... ", #name); \
		sec_cache_reset();               \
		test_##name();                   \
		printf("PASSED\n");              \
		tests_passed++;                  \
	} while (0)

static const char *get_cert_dir(void)
{
	const char *dir = getenv("CERT_DIR");
	if (!dir) {
		return "./tests/certs";
	}
	printf("CERT_DIR: %s\n", dir);
	return dir;
}

static int create_server_socket(int port)
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

static int create_client_socket(int port)
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
	int client_fd = accept(listen_fd, NULL, NULL);
	if (client_fd < 0) {
		return (void *)(long)-1;
	}
	close(listen_fd);

	SSL *ssl = tls_cert_server_handshake(client_fd, NULL);
	if (!ssl) {
		close(client_fd);
		return (void *)(long)-1;
	}

	char buf[64] = { 0 };
	int n = SSL_read(ssl, buf, sizeof(buf) - 1);
	if (n > 0) {
		printf("Server received: %s\n", buf);
	}

	const char *response = "Hello from server";
	SSL_write(ssl, response, strlen(response));

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(client_fd);

	return (void *)(long)0;
}

TEST(tls_server_init)
{
	tls_cert_cleanup();

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CHECK_NAME", "Server", 1);
	char ca_path[256], server_cert[256], server_key[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(server_cert, sizeof(server_cert), "%s/server.crt",
		 get_cert_dir());
	snprintf(server_key, sizeof(server_key), "%s/server.key",
		 get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", server_cert, 1);
	setenv("RPC_TLS_SERVER_KEY", server_key, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);

	tls_cert_cleanup();
}

TEST(tls_cert_init_disabled)
{
	setenv("RPC_TLS_ENABLE", "0", 1);
	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == false);
	tls_cert_cleanup();
}

TEST(tls_cert_init_missing_ca)
{
	setenv("RPC_TLS_ENABLE", "1", 1);
	char client_cert[256], client_key[256];
	snprintf(client_cert, sizeof(client_cert), "%s/client.crt", get_cert_dir());
	snprintf(client_key, sizeof(client_key), "%s/client.key", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", "/nonexistent/ca.crt", 1);
	setenv("RPC_TLS_CLIENT_CERT", client_cert, 1);
	setenv("RPC_TLS_CLIENT_KEY", client_key, 1);
	int ret = tls_cert_init_client_from_env();
	/* 客户端 init 三个文件用短路或链加载，统一返回 LOAD_CERT */
	assert(ret == TLS_CERT_ERR_LOAD_CERT);
	tls_cert_cleanup();
}

TEST(tls_cert_init_missing_cert)
{
	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", "/nonexistent/ca.crt", 1);
	setenv("RPC_TLS_CLIENT_CERT", "/nonexistent/client.crt", 1);
	setenv("RPC_TLS_CLIENT_KEY", "/nonexistent/client.key", 1);
	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_ERR_LOAD_CERT);
	tls_cert_cleanup();
}

TEST(tls_cert_init_cleanup)
{
	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", "/nonexistent/ca.crt", 1);
	setenv("RPC_TLS_CLIENT_CERT", "/nonexistent/client.crt", 1);
	setenv("RPC_TLS_CLIENT_KEY", "/nonexistent/client.key", 1);
	tls_cert_init_client_from_env();
	tls_cert_cleanup();
	assert(tls_cert_get_global_ctx() == NULL);
}

TEST(tls_multi_cert_handshake)
{
	tls_cert_cleanup();

	setenv("RPC_TLS_ENABLE", "1", 1);
	char ca_path[256], cert_path[256], key_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(cert_path, sizeof(cert_path), "%s/server.crt", get_cert_dir());
	snprintf(key_path, sizeof(key_path), "%s/server.key", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", cert_path, 1);
	setenv("RPC_TLS_SERVER_KEY", key_path, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);

	int port = 14445;
	int listen_fd = create_server_socket(port);

	pthread_t tid;
	pthread_create(&tid, NULL, server_thread, &listen_fd);
	usleep(50000);

	int client_fd = create_client_socket(port);

	SSL *ssl = tls_cert_client_handshake(client_fd, NULL);
	assert(ssl != NULL);

	const char *msg = "Hello from multi-cert client";
	SSL_write(ssl, msg, strlen(msg));

	char buf[64] = { 0 };
	ssize_t n = SSL_read(ssl, buf, sizeof(buf) - 1);
	assert(n > 0);
	printf("Client received: %s\n", buf);
	assert(strcmp(buf, "Hello from server") == 0);

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(client_fd);

	void *thread_ret;
	pthread_join(tid, &thread_ret);
	assert((long)thread_ret == 0);

	tls_cert_cleanup();
}

TEST(tls_multi_cert_mutual_auth)
{
	tls_cert_cleanup();

	setenv("RPC_TLS_ENABLE", "1", 1);
	char ca_path[256], server_cert[256], server_key[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(server_cert, sizeof(server_cert), "%s/server.crt",
		 get_cert_dir());
	snprintf(server_key, sizeof(server_key), "%s/server.key",
		 get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", server_cert, 1);
	setenv("RPC_TLS_SERVER_KEY", server_key, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);

	int port = 14446;
	int listen_fd = create_server_socket(port);

	pthread_t tid;
	pthread_create(&tid, NULL, server_thread, &listen_fd);
	usleep(50000);

	tls_cert_cleanup();

	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);

	ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);

	int client_fd = create_client_socket(port);

	SSL *ssl = tls_cert_client_handshake(client_fd, NULL);
	assert(ssl != NULL);

	const char *msg = "Mutual TLS test";
	SSL_write(ssl, msg, strlen(msg));

	char buf[64] = { 0 };
	ssize_t n = SSL_read(ssl, buf, sizeof(buf) - 1);
	assert(n > 0);
	printf("Client received: %s\n", buf);
	assert(strcmp(buf, "Hello from server") == 0);

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(client_fd);

	void *thread_ret;
	pthread_join(tid, &thread_ret);
	assert((long)thread_ret == 0);

	tls_cert_cleanup();
}

TEST(tls_server_missing_ca)
{
	tls_cert_cleanup();

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", "/nonexistent/ca.crt", 1);
	setenv("RPC_TLS_SERVER_CERT", "/nonexistent/server.crt", 1);
	setenv("RPC_TLS_SERVER_KEY", "/nonexistent/server.key", 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_ERR_LOAD_CA);

	tls_cert_cleanup();
}

TEST(tls_server_missing_cert)
{
	tls_cert_cleanup();

	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", "/nonexistent/server.crt", 1);
	setenv("RPC_TLS_SERVER_KEY", "/nonexistent/server.key", 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_ERR_LOAD_CERT);

	tls_cert_cleanup();
}

TEST(tls_server_missing_key)
{
	tls_cert_cleanup();

	char ca_path[256], cert_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(cert_path, sizeof(cert_path), "%s/server.crt", get_cert_dir());
	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", cert_path, 1);
	setenv("RPC_TLS_SERVER_KEY", "/nonexistent/server.key", 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_ERR_LOAD_CERT);

	tls_cert_cleanup();
}

static void clear_client_cert_env(void)
{
	unsetenv("RPC_TLS_CLIENT_CERT");
	unsetenv("RPC_TLS_CLIENT_KEY");
}

TEST(tls_empty_cert_dir)
{
	tls_cert_cleanup();
	clear_client_cert_env();

	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", "/tmp", 1);

	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);

	tls_cert_cleanup();
}

TEST(tls_invalid_ca_cert_format)
{
	tls_cert_cleanup();

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", "/etc/passwd", 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);
	char cert_path[256], key_path[256];
	snprintf(cert_path, sizeof(cert_path), "%s/server.crt", get_cert_dir());
	snprintf(key_path, sizeof(key_path), "%s/server.key", get_cert_dir());
	setenv("RPC_TLS_SERVER_CERT", cert_path, 1);
	setenv("RPC_TLS_SERVER_KEY", key_path, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_ERR_LOAD_CA);

	tls_cert_cleanup();
}

TEST(tls_client_with_server_cert_env)
{
	tls_cert_cleanup();

	char ca_path[256], server_cert[256], server_key[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(server_cert, sizeof(server_cert), "%s/server.crt",
		 get_cert_dir());
	snprintf(server_key, sizeof(server_key), "%s/server.key",
		 get_cert_dir());

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", server_cert, 1);
	setenv("RPC_TLS_SERVER_KEY", server_key, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);

	printf("Client can init with server cert (not recommended but should work)\n");

	tls_cert_cleanup();
}

TEST(tls_server_with_cert_dir_env)
{
	tls_cert_cleanup();

	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);

	printf("Server can init with cert_dir (will load first matching cert)\n");

	tls_cert_cleanup();
}

static void *mtls_server_thread(void *arg)
{
	int listen_fd = *(int *)arg;
	int client_fd = accept(listen_fd, NULL, NULL);
	if (client_fd < 0) {
		printf("mtls server: accept failed\n");
		return (void *)(long)-1;
	}
	close(listen_fd);

	SSL *ssl = tls_cert_server_handshake(client_fd, NULL);
	if (!ssl) {
		printf("mtls server: handshake failed\n");
		int err = ERR_get_error();
		if (err) {
			printf("mtls server: SSL error: %s\n",
			       ERR_error_string(err, NULL));
		}
		close(client_fd);
		return (void *)(long)-1;
	}

	printf("mtls server: handshake success\n");

	char buf[64] = { 0 };
	int n = SSL_read(ssl, buf, sizeof(buf) - 1);
	if (n > 0) {
		printf("mtls server received: %s\n", buf);
	}

	const char *response = "Hello from mtls server";
	SSL_write(ssl, response, strlen(response));

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(client_fd);

	return (void *)(long)0;
}

TEST(tls_mtls_handshake)
{
	tls_cert_cleanup();

	setbuf(stdout, NULL);
	setbuf(stderr, NULL);

	char ca_path[256], server_cert[256], server_key[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(server_cert, sizeof(server_cert), "%s/server.crt",
		 get_cert_dir());
	snprintf(server_key, sizeof(server_key), "%s/server.key",
		 get_cert_dir());

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CHECK_NAME", "Server", 1);
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_SERVER_CERT", server_cert, 1);
	setenv("RPC_TLS_SERVER_KEY", server_key, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);
	printf("mtls: server initialized\n");
	fflush(stdout);

	int port = 14449;
	int listen_fd = create_server_socket(port);
	printf("mtls: server listening on port %d\n", port);
	fflush(stdout);

	pthread_t tid;
	pthread_create(&tid, NULL, mtls_server_thread, &listen_fd);
	usleep(200000);

	tls_cert_cleanup();

	char client_cert[256], client_key[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	snprintf(client_cert, sizeof(client_cert), "%s/client.crt",
		 get_cert_dir());
	snprintf(client_key, sizeof(client_key), "%s/client.key",
		 get_cert_dir());

	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CLIENT_CERT", client_cert, 1);
	setenv("RPC_TLS_CLIENT_KEY", client_key, 1);
	setenv("RPC_TLS_CHECK_NAME", "Client", 1);
	setenv("RPC_TLS_VERIFY_LOCAL", "0", 1);

	ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);
	printf("mtls: client initialized\n");
	fflush(stdout);

	int client_fd = create_client_socket(port);
	printf("mtls: client connected to server\n");
	fflush(stdout);

	SSL *ssl = tls_cert_client_handshake(client_fd, NULL);
	if (!ssl) {
		printf("mtls: client handshake failed\n");
		int err = ERR_get_error();
		if (err) {
			printf("mtls: SSL error: %s\n",
			       ERR_error_string(err, NULL));
		}
	}
	assert(ssl != NULL);
	printf("mtls: client handshake success\n");
	fflush(stdout);

	const char *msg = "Hello from mtls client";
	int w = SSL_write(ssl, msg, strlen(msg));
	printf("mtls: client wrote %d bytes\n", w);
	fflush(stdout);

	char buf[64] = { 0 };
	ssize_t n = SSL_read(ssl, buf, sizeof(buf) - 1);
	printf("mtls: client read %zd bytes: %s\n", n, buf);
	fflush(stdout);
	if (n <= 0) {
		int err = SSL_get_error(ssl, n);
		printf("mtls: SSL_read error code: %d\n", err);
		err = ERR_get_error();
		if (err) {
			printf("mtls: SSL error: %s\n",
			       ERR_error_string(err, NULL));
		}
		fflush(stdout);
	}
	assert(n > 0);
	assert(strcmp(buf, "Hello from mtls server") == 0);

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(client_fd);

	void *thread_ret;
	pthread_join(tid, &thread_ret);
	printf("mtls: server thread returned %ld\n", (long)thread_ret);
	fflush(stdout);
	assert((long)thread_ret == 0);

	tls_cert_cleanup();
}

TEST(tls_sm2_mtls_handshake)
{
	tls_cert_cleanup();

	setbuf(stdout, NULL);
	setbuf(stderr, NULL);

	char sm2_ca[256], sm2_server_cert[256], sm2_server_key[256];
	snprintf(sm2_ca, sizeof(sm2_ca), "%s/sm2_ca.crt", get_cert_dir());
	snprintf(sm2_server_cert, sizeof(sm2_server_cert), "%s/sm2_host.crt",
		 get_cert_dir());
	snprintf(sm2_server_key, sizeof(sm2_server_key), "%s/sm2_host.key",
		 get_cert_dir());

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CHECK_NAME", "SM2 Test CA", 1);
	setenv("RPC_TLS_CIPHERSUITES", "TLS_SM4_GCM_SM3", 1);
	setenv("RPC_TLS_CA_CERT", sm2_ca, 1);
	setenv("RPC_TLS_SERVER_CERT", sm2_server_cert, 1);
	setenv("RPC_TLS_SERVER_KEY", sm2_server_key, 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);
	printf("sm2 mtls: server initialized with SM2 chain\n");
	fflush(stdout);

	int port = 14451;
	int listen_fd = create_server_socket(port);
	printf("sm2 mtls: server listening on port %d\n", port);
	fflush(stdout);

	pthread_t tid;
	pthread_create(&tid, NULL, mtls_server_thread, &listen_fd);
	usleep(200000);

	tls_cert_cleanup();

	char sm2_client_cert[256], sm2_client_key[256];
	snprintf(sm2_client_cert, sizeof(sm2_client_cert), "%s/sm2_client.crt",
		 get_cert_dir());
	snprintf(sm2_client_key, sizeof(sm2_client_key), "%s/sm2_client.key",
		 get_cert_dir());

	setenv("RPC_TLS_CA_CERT", sm2_ca, 1);
	setenv("RPC_TLS_CLIENT_CERT", sm2_client_cert, 1);
	setenv("RPC_TLS_CLIENT_KEY", sm2_client_key, 1);
	setenv("RPC_TLS_CHECK_NAME", "SM2 Test CA", 1);
	setenv("RPC_TLS_VERIFY_LOCAL", "0", 1);

	ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);
	printf("sm2 mtls: client initialized with SM2 chain\n");
	fflush(stdout);

	int client_fd = create_client_socket(port);
	printf("sm2 mtls: client connected to server\n");
	fflush(stdout);

	SSL *ssl = tls_cert_client_handshake(client_fd, NULL);
	if (!ssl) {
		printf("sm2 mtls: client handshake failed\n");
		int err = ERR_get_error();
		if (err) {
			printf("sm2 mtls: SSL error: %s\n",
			       ERR_error_string(err, NULL));
		}
	}
	assert(ssl != NULL);

	const SSL_CIPHER *cipher = SSL_get_current_cipher(ssl);
	assert(cipher != NULL);
	const char *cipher_name = SSL_CIPHER_get_name(cipher);
	printf("sm2 mtls: negotiated cipher = %s\n", cipher_name);
	fflush(stdout);
	assert(strcmp(cipher_name, "TLS_SM4_GCM_SM3") == 0);

	const char *msg = "Hello from sm2 client";
	int w = SSL_write(ssl, msg, strlen(msg));
	printf("sm2 mtls: client wrote %d bytes\n", w);
	fflush(stdout);

	char buf[64] = { 0 };
	ssize_t n = SSL_read(ssl, buf, sizeof(buf) - 1);
	printf("sm2 mtls: client read %zd bytes: %s\n", n, buf);
	fflush(stdout);
	assert(n > 0);
	assert(strcmp(buf, "Hello from mtls server") == 0);

	SSL_shutdown(ssl);
	SSL_free(ssl);
	close(client_fd);

	void *thread_ret;
	pthread_join(tid, &thread_ret);
	printf("sm2 mtls: server thread returned %ld\n", (long)thread_ret);
	fflush(stdout);
	assert((long)thread_ret == 0);

	tls_cert_cleanup();
	unsetenv("RPC_TLS_CIPHERSUITES");
}

TEST(tls_cert_select_callback)
{
	tls_cert_cleanup();
	clear_client_cert_env();

	setenv("RPC_TLS_ENABLE", "1", 1);
	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);

	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);
	assert(sec_tls_enabled() == true);

	tls_cert_ctx_t *ctx = tls_cert_get_global_ctx();
	assert(ctx != NULL);

	printf("TLS cert callback test passed\n");

	tls_cert_cleanup();
}

// TEST(tls_verify_is_local)
// {
// 	int ret;
//
// 	unsetenv("RPC_TLS_CHECK_NAME");
//
// 	// 测试1: 使用 tls_cert_set_checkname 设置主机名
// 	// CN="server-a" 匹配 checkname="server-a" → 应返回 TLS_CERT_IS_LOCAL
// 	tls_cert_cleanup();
// 	tls_cert_set_checkname("server-a");
// 	ret = tls_cert_verify_is_local("/tmp/tls_cert_test/server-a.crt");
// 	printf("Test 1: ret=%d (expect %d)\n", ret, TLS_CERT_IS_LOCAL);
// 	assert(ret == TLS_CERT_IS_LOCAL);
//
// 	// 测试2: CN="server-b" 不匹配 checkname="server-a" → 应返回 TLS_CERT_NOT_LOCAL
// 	ret = tls_cert_verify_is_local("/tmp/tls_cert_test/server-b.crt");
// 	printf("Test 2: ret=%d (expect %d)\n", ret, TLS_CERT_NOT_LOCAL);
// 	assert(ret == TLS_CERT_NOT_LOCAL);
//
// 	// 测试3: 大小写敏感测试
// 	// CN="SERVER-A" 不匹配 checkname="server-a" → 应返回 TLS_CERT_NOT_LOCAL
// 	ret = tls_cert_verify_is_local("/tmp/tls_cert_test/server-upper.crt");
// 	printf("Test 3: ret=%d (expect %d)\n", ret, TLS_CERT_NOT_LOCAL);
// 	assert(ret == TLS_CERT_NOT_LOCAL);
//
// 	// 测试4: 无 CN 的证书 → 应返回 TLS_CERT_ERR_NO_CERT
// 	ret = tls_cert_verify_is_local("/tmp/tls_cert_test/no-cn.crt");
// 	printf("Test 4: ret=%d (expect %d)\n", ret, TLS_CERT_ERR_NO_CERT);
// 	assert(ret == TLS_CERT_ERR_NO_CERT);
//
// 	// 测试5: 不存在的文件 → 应返回 TLS_CERT_ERR_LOAD
// 	ret = tls_cert_verify_is_local("/tmp/tls_cert_test/not-exist.crt");
// 	printf("Test 5: ret=%d (expect %d)\n", ret, TLS_CERT_ERR_LOAD);
// 	assert(ret == TLS_CERT_ERR_LOAD);
//
// 	// 测试6: 未显式设置 checkname 时，从 HOST_ID_FILE 读取
// 	// 由于 /etc/aio-speedd-id 存在，会返回 NOT_LOCAL（因为 CN 不匹配）
// 	tls_cert_cleanup();
// 	ret = tls_cert_verify_is_local("/tmp/tls_cert_test/server-a.crt");
// 	printf("Test 6: ret=%d (expect NOT_LOCAL since host ID exists)\n", ret);
// 	assert(ret == TLS_CERT_NOT_LOCAL);
//
// 	// 测试7: 使用环境变量 RPC_TLS_CHECK_NAME
// 	tls_cert_cleanup();
// 	setenv("RPC_TLS_CHECK_NAME", "server-a", 1);
// 	ret = tls_cert_verify_is_local("/tmp/tls_cert_test/server-a.crt");
// 	printf("Test 7: ret=%d (expect %d)\n", ret, TLS_CERT_IS_LOCAL);
// 	assert(ret == TLS_CERT_IS_LOCAL);
// 	unsetenv("RPC_TLS_CHECK_NAME");
//
// 	printf("tls_verify_is_local tests passed!\n");
// 	tls_cert_cleanup();
// }

TEST(tls_ciphersuites_default_null)
{
	tls_cert_cleanup();
	unsetenv("RPC_TLS_CIPHERSUITES");

	/* 未配置算法参数时返回 NULL，保持 OpenSSL 默认套件（存量行为） */
	assert(sec_tls_ciphersuites() == NULL);
}

TEST(tls_ciphersuites_from_env)
{
	tls_cert_cleanup();
	unsetenv("RPC_TLS_CLIENT_CERT");
	unsetenv("RPC_TLS_CLIENT_KEY");

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CIPHERSUITES",
	       "TLS_SM4_GCM_SM3:TLS_AES_256_GCM_SHA384", 1);
	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);

	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);

	/* 配置读取结果包含国密套件 */
	const char *ciphers = sec_tls_ciphersuites();
	assert(ciphers != NULL);
	assert(strstr(ciphers, "TLS_SM4_GCM_SM3") != NULL);

	/* 验证套件已实际应用到 SSL_CTX */
	SSL_CTX *ctx = tls_cert_get_ssl_ctx();
	assert(ctx != NULL);
	STACK_OF(SSL_CIPHER) *ciphers_stack = SSL_CTX_get_ciphers(ctx);
	int found = 0;
	for (int i = 0; i < sk_SSL_CIPHER_num(ciphers_stack); i++) {
		const SSL_CIPHER *c = sk_SSL_CIPHER_value(ciphers_stack, i);
		const char *name = SSL_CIPHER_get_name(c);
		if (name && strcmp(name, "TLS_SM4_GCM_SM3") == 0) {
			found = 1;
			break;
		}
	}
	assert(found == 1);

	tls_cert_cleanup();
	unsetenv("RPC_TLS_CIPHERSUITES");
}

TEST(tls_ciphersuites_invalid_ignored)
{
	tls_cert_cleanup();
	unsetenv("RPC_TLS_CLIENT_CERT");
	unsetenv("RPC_TLS_CLIENT_KEY");

	setenv("RPC_TLS_ENABLE", "1", 1);
	/* 非法套件名：set_ciphersuites 失败仅记日志，init 不应失败 */
	setenv("RPC_TLS_CIPHERSUITES", "TLS_THIS_SUITE_DOES_NOT_EXIST", 1);
	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);

	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);

	tls_cert_cleanup();
	unsetenv("RPC_TLS_CIPHERSUITES");
}

TEST(tls_sm2_chain_loaded_with_ciphersuites)
{
	tls_cert_cleanup();
	unsetenv("RPC_TLS_CLIENT_CERT");
	unsetenv("RPC_TLS_CLIENT_KEY");

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CIPHERSUITES", "TLS_SM4_GCM_SM3", 1);
	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);

	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_OK);

	/* 国密套件配置下，SSL_CTX 应加载 SM2 主机证书（非 Ed25519 host.crt） */
	SSL_CTX *ctx = tls_cert_get_ssl_ctx();
	assert(ctx != NULL);
	X509 *loaded = SSL_CTX_get0_certificate(ctx);
	assert(loaded != NULL);
	/* SM2 证书公钥 group 应为 SM2（TLS 层 base id 为 EC，需查 group 名） */
	EVP_PKEY *pk = X509_get_pubkey(loaded);
	assert(pk != NULL);
	char group_name[64] = {0};
	assert(EVP_PKEY_get_group_name(pk, group_name, sizeof(group_name),
				       NULL) > 0);
	EVP_PKEY_free(pk);
	assert(strcmp(group_name, "SM2") == 0);

	tls_cert_cleanup();
	unsetenv("RPC_TLS_CIPHERSUITES");
}

TEST(tls_sm2_chain_missing_fails)
{
	tls_cert_cleanup();
	unsetenv("RPC_TLS_CLIENT_CERT");
	unsetenv("RPC_TLS_CLIENT_KEY");

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CIPHERSUITES", "TLS_SM4_GCM_SM3", 1);
	/* cert_dir 指向空目录：SM2 证书缺失，初始化失败且不降级。 */
	char empty_dir[] = "/tmp/tls_sm2_empty_dir";
	mkdir(empty_dir, 0700);
	unsetenv("RPC_TLS_CA_CERT");
	setenv("RPC_TLS_CERT_DIR", empty_dir, 1);

	int ret = tls_cert_init_client_from_env();
	assert(ret == TLS_CERT_ERR_LOAD_CERT);

	tls_cert_cleanup();
	rmdir(empty_dir);
	unsetenv("RPC_TLS_CIPHERSUITES");
}

TEST(tls_sm2_server_chain_loaded)
{
	tls_cert_cleanup();

	setenv("RPC_TLS_ENABLE", "1", 1);
	setenv("RPC_TLS_CIPHERSUITES", "TLS_SM4_GCM_SM3", 1);
	char ca_path[256];
	snprintf(ca_path, sizeof(ca_path), "%s/ca.crt", get_cert_dir());
	setenv("RPC_TLS_CA_CERT", ca_path, 1);
	setenv("RPC_TLS_CERT_DIR", get_cert_dir(), 1);

	int ret = tls_cert_init_server_from_env();
	assert(ret == TLS_CERT_OK);

	SSL_CTX *ctx = tls_cert_get_ssl_ctx();
	assert(ctx != NULL);
	X509 *loaded = SSL_CTX_get0_certificate(ctx);
	assert(loaded != NULL);
	EVP_PKEY *pk = X509_get_pubkey(loaded);
	assert(pk != NULL);
	char group_name[64] = {0};
	assert(EVP_PKEY_get_group_name(pk, group_name, sizeof(group_name),
				       NULL) > 0);
	EVP_PKEY_free(pk);
	assert(strcmp(group_name, "SM2") == 0);

	tls_cert_cleanup();
	unsetenv("RPC_TLS_CIPHERSUITES");
}

int main()
{
	printf("=== TLS Cert Unit Tests ===\n\n");
	printf("Using CERT_DIR: %s\n", get_cert_dir());

	RUN_TEST(tls_cert_init_disabled);
	RUN_TEST(tls_cert_init_missing_ca);
	RUN_TEST(tls_cert_init_missing_cert);
	RUN_TEST(tls_cert_init_cleanup);
	RUN_TEST(tls_server_init);
	RUN_TEST(tls_server_missing_ca);
	RUN_TEST(tls_server_missing_cert);
	RUN_TEST(tls_server_missing_key);
	RUN_TEST(tls_empty_cert_dir);
	RUN_TEST(tls_invalid_ca_cert_format);
	RUN_TEST(tls_client_with_server_cert_env);
	RUN_TEST(tls_server_with_cert_dir_env);
	RUN_TEST(tls_cert_select_callback);
	RUN_TEST(tls_ciphersuites_default_null);
	RUN_TEST(tls_ciphersuites_from_env);
	RUN_TEST(tls_ciphersuites_invalid_ignored);
	RUN_TEST(tls_sm2_chain_loaded_with_ciphersuites);
	RUN_TEST(tls_sm2_chain_missing_fails);
	RUN_TEST(tls_sm2_server_chain_loaded);
	// RUN_TEST(tls_verify_is_local);
	RUN_TEST(tls_mtls_handshake);
	RUN_TEST(tls_sm2_mtls_handshake);

	printf("\n=== Results ===\n");
	printf("Passed: %d\n", tests_passed);
	printf("Failed: %d\n", tests_failed);
	printf("\nAll tests %s!\n", tests_failed == 0 ? "PASSED" : "FAILED");

	return tests_failed > 0 ? 1 : 0;
}

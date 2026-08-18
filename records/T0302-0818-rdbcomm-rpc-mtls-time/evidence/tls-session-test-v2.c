#include "rpc-handshake.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <sys/socket.h>
#include <unistd.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

static const char *cert_dir = NULL;

struct tls_server_args {
	int fd;
	SSL_CTX *ctx;
};

struct protocol_tls_server_args {
	int fd;
	SSL_CTX *ctx;
};

static void *protocol_tls_server(void *arg)
{
	struct protocol_tls_server_args *args = arg;
	rpc_hs_session_t plain;
	rpc_hs_message_t request;
	rpc_hs_result_t result = { 0 };
	uint8_t payload[RPC_HS_MAX_PAYLOAD];
	SSL *ssl;
	char buf[32] = { 0 };
	rpc_hs_session_t encrypted;
	rpc_hs_session_init_plain(&plain, args->fd);
	assert(rpc_hs_recv(&plain, &request, payload, sizeof(payload)) == 0);
	assert(rpc_hs_server_respond(&plain, &request, 1, RPC_HS_ALG_CLASSIC,
					     "Test CA", &result) == 0);
	assert(result.result == RPC_HS_OK_MTLS);
	ssl = SSL_new(args->ctx);
	assert(ssl != NULL);
	SSL_set_fd(ssl, args->fd);
	assert(SSL_accept(ssl) == 1);
	rpc_hs_session_init_tls(&encrypted, args->fd, ssl);
	assert(encrypted.read(&encrypted, buf, sizeof(buf), 0) == 6);
	assert(memcmp(buf, "secret", 6) == 0);
	rpc_hs_session_cleanup(&encrypted);
	SSL_CTX_free(args->ctx);
	close(args->fd);
	return NULL;
}

static void *tls_server(void *arg)
{
	struct tls_server_args *args = arg;
	SSL *ssl = SSL_new(args->ctx);
	char buf[32] = { 0 };
	rpc_hs_session_t session;
	assert(ssl != NULL);
	SSL_set_fd(ssl, args->fd);
	assert(SSL_accept(ssl) == 1);
	rpc_hs_session_init_tls(&session, args->fd, ssl);
	assert(session.read(&session, buf, sizeof(buf), 0) == 6);
	assert(memcmp(buf, "secret", 6) == 0);
	rpc_hs_session_cleanup(&session);
	SSL_CTX_free(args->ctx);
	close(args->fd);
	return NULL;
}

static SSL_CTX *make_ctx(int server)
{
	char path[256];
	if (!cert_dir)
		cert_dir = getenv("CERT_DIR");
	assert(cert_dir != NULL);
	SSL_CTX *ctx = SSL_CTX_new(TLS_method());
	assert(ctx != NULL);
	SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION);
	if (server) {
		snprintf(path, sizeof(path), "%s/server.crt", cert_dir);
		assert(SSL_CTX_use_certificate_file(ctx, path, SSL_FILETYPE_PEM) == 1);
		snprintf(path, sizeof(path), "%s/server.key", cert_dir);
		assert(SSL_CTX_use_PrivateKey_file(ctx, path, SSL_FILETYPE_PEM) == 1);
	} else {
		snprintf(path, sizeof(path), "%s/client.crt", cert_dir);
		assert(SSL_CTX_use_certificate_file(ctx, path, SSL_FILETYPE_PEM) == 1);
		snprintf(path, sizeof(path), "%s/client.key", cert_dir);
		assert(SSL_CTX_use_PrivateKey_file(ctx, path, SSL_FILETYPE_PEM) == 1);
	}
	snprintf(path, sizeof(path), "%s/ca.crt", cert_dir);
	assert(SSL_CTX_load_verify_locations(ctx, path, NULL) == 1);
	if (server)
		SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT,
				   NULL);
	else
		SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, NULL);
	return ctx;
}

static void *time_server(void *arg)
{
	int fd = *(int *)arg;
	rpc_hs_session_t session;
	rpc_hs_message_t request;
	uint8_t payload[RPC_HS_MAX_PAYLOAD];
	rpc_hs_session_init_plain(&session, fd);
	assert(rpc_hs_recv(&session, &request, payload, sizeof(payload)) == 0);
	assert(request.operation == RPC_HS_OP_TIME);
	assert(rpc_hs_send_time_response(&session, 123456789ULL) == 0);
	close(fd);
	return NULL;
}

int main(void)
{
	SSL_library_init();
	SSL_load_error_strings();
	uint8_t wire[512];
	uint32_t wire_len = 0;
	const uint8_t *payload = NULL;
	rpc_hs_message_t in = { 0 };
	rpc_hs_message_t out = { 0 };
	const char body[] = "time-v1";

	in.version = RPC_HS_VERSION;
	in.operation = RPC_HS_OP_NEGOTIATE;
	in.flags = RPC_HS_F_MTLS_REQUEST;
	in.algorithm = RPC_HS_ALG_SM;
	strcpy(in.ca_cn, "ca-sm");
	in.payload_length = sizeof(body) - 1;
	assert(rpc_hs_encode(&in, body, wire, sizeof(wire), &wire_len) == 0);
	assert(rpc_hs_decode(&out, wire, wire_len, &payload) == 0);
	assert(out.version == RPC_HS_VERSION);
	assert(out.operation == RPC_HS_OP_NEGOTIATE);
	assert(out.flags == RPC_HS_F_MTLS_REQUEST);
	assert(out.algorithm == RPC_HS_ALG_SM);
	assert(strcmp(out.ca_cn, "ca-sm") == 0);
	assert(out.payload_length == sizeof(body) - 1);
	assert(memcmp(payload, body, out.payload_length) == 0);

	assert(rpc_hs_decide(RPC_HS_F_MTLS_REQUEST,
				 RPC_HS_F_MTLS_REQUIRED, RPC_HS_ALG_SM,
				 RPC_HS_ALG_SM, NULL) == 1);
	assert(rpc_hs_decide(0, RPC_HS_F_MTLS_REQUIRED,
				 RPC_HS_ALG_SM, RPC_HS_ALG_SM, NULL) == 0);
	assert(rpc_hs_decide(0, 0, RPC_HS_ALG_DEFAULT,
				 RPC_HS_ALG_DEFAULT, NULL) == 1);
	{
		int fds[2];
		pthread_t thread;
		uint64_t timestamp = 0;
		assert(socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);
		assert(pthread_create(&thread, NULL, time_server, &fds[1]) == 0);
		{
			rpc_hs_session_t session;
			rpc_hs_session_init_plain(&session, fds[0]);
			assert(rpc_hs_request_time(&session, &timestamp) == 0);
		}
		assert(timestamp == 123456789ULL);
		close(fds[0]);
		pthread_join(thread, NULL);
	}
	{
		int fds[2];
		pthread_t thread;
		struct protocol_tls_server_args args;
		SSL_CTX *client_ctx;
		SSL *client_ssl;
		rpc_hs_session_t plain;
		rpc_hs_result_t result = { 0 };
		assert(socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);
		args.fd = fds[1];
		args.ctx = make_ctx(1);
		assert(pthread_create(&thread, NULL, protocol_tls_server, &args) == 0);
		rpc_hs_session_init_plain(&plain, fds[0]);
		assert(rpc_hs_client_negotiate(&plain, 1, RPC_HS_ALG_CLASSIC,
					       &result) == 0);
		assert(result.result == RPC_HS_OK_MTLS);
		client_ctx = make_ctx(0);
		client_ssl = SSL_new(client_ctx);
		assert(client_ssl != NULL);
		SSL_set_fd(client_ssl, fds[0]);
		assert(SSL_connect(client_ssl) == 1);
		plain.ssl = NULL;
		rpc_hs_session_init_tls(&plain, fds[0], client_ssl);
		assert(plain.write(&plain, "secret", 6, 0) == 6);
		rpc_hs_session_cleanup(&plain);
		SSL_CTX_free(client_ctx);
		close(fds[0]);
		pthread_join(thread, NULL);
	}
	{
		int fds[2];
		pthread_t thread;
		struct tls_server_args args;
		SSL_CTX *client_ctx;
		SSL *client_ssl;
		rpc_hs_session_t client_session;
		assert(socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);
		args.fd = fds[1];
		args.ctx = make_ctx(1);
		assert(pthread_create(&thread, NULL, tls_server, &args) == 0);
		client_ctx = make_ctx(0);
		client_ssl = SSL_new(client_ctx);
		assert(client_ssl != NULL);
		SSL_set_fd(client_ssl, fds[0]);
		assert(SSL_connect(client_ssl) == 1);
		rpc_hs_session_init_tls(&client_session, fds[0], client_ssl);
		assert(client_session.write(&client_session, "secret", 6, 0) == 6);
		rpc_hs_session_cleanup(&client_session);
		SSL_CTX_free(client_ctx);
		close(fds[0]);
		pthread_join(thread, NULL);
	}
	puts("rpc_handshake_test: PASS");
	return 0;
}


#include "bandwidth.h"
#include "common.h"
#include "rpc-protocol.h"
#include "rpc-io.h"
#include "rpc-config.h"
#include "logger.h"
#include "tls_cert.h"
#include "rdb-config.h"

#include <cstdint>
#include <string.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/sendfile.h>

static ssize_t rpc_plain_read(rpc_io_t *io, void *buf, size_t len, int flags)
{
	return recv(io->fd, buf, len, flags);
}

static ssize_t rpc_plain_write(rpc_io_t *io, const void *buf, size_t len,
			       int flags)
{
	return send(io->fd, buf, len, flags);
}

static ssize_t rpc_tls_read(rpc_io_t *io, void *buf, size_t len, int flags)
{
	(void)flags;
	return SSL_read(io->ssl, buf, (int)len);
}

static ssize_t rpc_tls_write(rpc_io_t *io, const void *buf, size_t len,
			      int flags)
{
	(void)flags;
	return SSL_write(io->ssl, buf, (int)len);
}

void rpc_io_init_plain(rpc_io_t *io, int fd)
{
	memset(io, 0, sizeof(*io));
	io->fd = fd;
	io->read = rpc_plain_read;
	io->write = rpc_plain_write;
}

void rpc_io_init_tls(rpc_io_t *io, int fd, TLS_SSL *tssl)
{
	memset(io, 0, sizeof(*io));
	io->fd = fd;
	io->tssl = tssl;
	io->ssl = tls_ssl_get_ssl(tssl);
	io->read = rpc_tls_read;
	io->write = rpc_tls_write;
}

void rpc_io_cleanup(rpc_io_t *io)
{
	if (!io)
		return;
	if (io->tssl) {
		tls_cert_ssl_free(io->tssl);
		io->tssl = NULL;
	}
	io->ssl = NULL;
	io->read = NULL;
	io->write = NULL;
}

/* ---- 自实现握手：客户端（按需） ---- */

int rpc_ensure_handshake(rpc_io_t *io)
{
	if (io->hs_done || io->hs_in_progress)
		return 0;
	if (!g_rpc_config->mtls_enabled) {
		io->hs_done = true;
		return 0;
	}
	io->hs_in_progress = true;
	int ret = rpc_handshake_client_negotiate(io);
	io->hs_in_progress = false;
	if (ret == 0)
		io->hs_done = true;
	return ret;
}

int rpc_handshake_client_negotiate(rpc_io_t *io)
{
	if (!g_rpc_config->mtls_enabled)
		return 0;

	/* 发送 HANDSHAKE 请求 */
	msg_handshake_t hs_host = {};
	msg_handshake_t hs_net = {};
	hs_host.flags = HS_FLAG_MTLS_REQUEST;
	hs_host.algorithm = hs_algorithm_from_name(g_rpc_config->tls_algorithm);
	hs_host.ca_cn[0] = '\0';
	msg_handshake_hton(&hs_host, &hs_net);
	if (rpc_send_io(io, &hs_net, sizeof(hs_net), 0) < 0)
		return -1;

	/* 接收 HANDSHAKE 响应 */
	char buf[MSG_BUFF_LEN];
	int bytes = rpc_recv_io(io, buf, sizeof(buf), 0);
	if (bytes < 0)
		return -1;
	msg_base_t *base = (msg_base_t *)buf;
	if (ntohl(base->uiMT) != MT_HANDSHAKE_RESP) {
		ErrorLog("handshake: expected HANDSHAKE_RESP, got 0x%x",
			 ntohl(base->uiMT));
		return -1;
	}
	msg_handshake_resp_t resp_host = {};
	msg_handshake_resp_ntoh(&resp_host, (msg_handshake_resp_t *)buf);
	if (resp_host.result == HS_ERR_MTLS_REQUIRED) {
		ErrorLog("handshake: server requires mTLS but not satisfied");
		return -1;
	}
	if (resp_host.result != HS_OK_MTLS)
		return 0;

	/* 需要 TLS 握手 */
	tls_cert_ctx_t *ctx = NULL;
	tls_cert_client_options_t opts = { 0 };
	char client_cert[512], client_key[512];
	const char *alg_name = hs_algorithm_name(resp_host.algorithm);
	TLS_SSL *tssl;
	opts.mtls_enabled = 1;
	opts.profiles[0].algorithm = alg_name;
	opts.profiles[0].ca_cn = resp_host.ca_cn;
	opts.profiles[0].ca_cert = g_rpc_config->ca_cert;
	if (g_rpc_config->client_cert[0] && g_rpc_config->client_key[0]) {
		snprintf(client_cert, sizeof(client_cert), "%s",
			 g_rpc_config->client_cert);
		snprintf(client_key, sizeof(client_key), "%s",
			 g_rpc_config->client_key);
	} else if (g_rpc_config->cert_dir[0] && resp_host.ca_cn[0]) {
		if (sec_tls_client_cert_paths(client_cert, sizeof(client_cert),
					      client_key, sizeof(client_key),
					      resp_host.ca_cn) != 0)
			return -1;
	} else {
		ErrorLog("handshake: no client cert available");
		return -1;
	}
	opts.profiles[0].cert = client_cert;
	opts.profiles[0].key = client_key;
	opts.profile_count = 1;
	if (tls_cert_init_client(&opts, &ctx) != 0)
		return -1;
	tssl = tls_cert_client_handshake(ctx, io->fd, alg_name, NULL);
	tls_cert_cleanup(ctx);
	if (!tssl)
		return -1;
	int saved_fd = io->fd;
	rpc_io_init_tls(io, saved_fd, tssl);
	return 0;
}

static int rpc_connect_first_stage(int fd)
{
	/* fd-only API：默认明文，不做握手；如后续 mTLS 必需由上层处理 */
	(void)fd;
	return 0;
}

int connect_server_session(const char *ip, const unsigned short port,
				   const char *local_ip,
				   const unsigned short local_port,
				   rpc_io_t *io)
{
	int fd = -1;
	struct sockaddr_in localaddr;
	struct sockaddr_in serveraddr;
	if (!io)
		return -1;
	fd = socket(AF_INET, SOCK_STREAM, 0);
	if (fd < 0)
		return -1;
	if (g_rpc_config->keepalive > 0 &&
	    sock_keepalive(fd, g_rpc_config->keepalive) != 0)
		goto error;
	if (local_ip && local_ip[0]) {
		memset(&localaddr, 0, sizeof(localaddr));
		localaddr.sin_family = AF_INET;
		localaddr.sin_addr.s_addr = htonl(INADDR_ANY);
		localaddr.sin_port = htons(local_port);
		if (inet_pton(AF_INET, local_ip, &localaddr.sin_addr) <= 0 ||
		    bind(fd, (struct sockaddr *)&localaddr, sizeof(localaddr)) != 0)
			goto error;
	}
	memset(&serveraddr, 0, sizeof(serveraddr));
	serveraddr.sin_family = AF_INET;
	serveraddr.sin_port = htons(port);
	if (inet_pton(AF_INET, ip, &serveraddr.sin_addr) <= 0 ||
	    connect(fd, (struct sockaddr *)&serveraddr, sizeof(serveraddr)) != 0)
		goto error;
	rpc_io_init_plain(io, fd);
	/* 连接后根据状态决定是否握手 */
	if (g_rpc_config->mtls_enabled) {
		if (rpc_handshake_client_negotiate(io) != 0)
			goto error_session;
	}
	return fd;
error_session:
	rpc_io_cleanup(io);
error:
	close(fd);
	return -1;
}

int rpc_get_time(const char *ip, unsigned short port, uint64_t *timestamp)
{
	int fd = -1;
	struct sockaddr_in serveraddr = { 0 };
	char net_buf[MSG_BUFF_LEN];
	char host_buf[MSG_BUFF_LEN];
	if (!ip || !timestamp)
		return -1;
	fd = socket(AF_INET, SOCK_STREAM, 0);
	if (fd < 0)
		return -1;
	serveraddr.sin_family = AF_INET;
	serveraddr.sin_port = htons(port);
	if (inet_pton(AF_INET, ip, &serveraddr.sin_addr) <= 0 ||
	    connect(fd, (struct sockaddr *)&serveraddr, sizeof(serveraddr)) != 0)
		goto error;
	{
		msg_get_time_t req_host = {};
		msg_get_time_t req_net = {};
		msg_get_time_hton(&req_host, &req_net);
		if (rpc_send(fd, &req_net, sizeof(req_net), 0) < 0)
			goto error;
		int bytes = rpc_recv(fd, net_buf, sizeof(net_buf), 0);
		if (bytes < 0)
			goto error;
		msg_get_time_resp_t *resp = (msg_get_time_resp_t *)host_buf;
		msg_get_time_resp_ntoh(resp, (msg_get_time_resp_t *)net_buf);
		if (resp->uiMT != MT_GET_TIME_RESP)
			goto error;
		*timestamp = resp->timestamp;
	}
	close(fd);
	return 0;
error:
	close(fd);
	return -1;
}


int rpc_recv_io(rpc_io_t *io, void *buf, const int buflen, int flags)
{
	int fd = io->fd;
	int bytes = 0;
	int nread = 0;
	int msg_net_length = 0;
	int opt_status = 0;
	int eof = 0;
	struct sockaddr_in serv;
	socklen_t serv_len = sizeof(serv);

	opt_status = (intptr_t)(int *)pthread_getspecific(g_key);

	while (bytes < (int)sizeof(msg_net_length)) {
		nread = io->read(io, ((char *)&msg_net_length) + bytes,
				  (sizeof(msg_net_length) - bytes), flags);
		if (nread < 1) {
			if (nread == 0) {
				eof = 1;
				break;
			}
			if (errno == EINTR || errno == EAGAIN) {
				WarningLog(
					"receive failure.  nread: %d,  status(%s, errno: %d)",
					nread, strerror(errno), errno);
				continue;
			}
			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"receive failure.  nread: %d,  addr: [%s:%d],  status(%s, errno: %d)",
				nread, inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
			break;
		}
		bytes += nread;
	}
	if (bytes != (int)sizeof(msg_net_length)) {
		getpeername(fd, (struct sockaddr *)&serv, &serv_len);
		if (eof == 0) {
			ErrorLog(
				"receive failure bytes: %d != (int)sizeof(msg_net_length): %d, addr: [%s:%d], status: %s(errno: %d)",
				bytes, sizeof(msg_net_length),
				inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
		}
		return eof ? IO_EOF : -100;
	}

	const int msg_length = ntohl(msg_net_length);
	if (buflen < msg_length) {
		getpeername(fd, (struct sockaddr *)&serv, &serv_len);
		ErrorLog(
			"receive failure buflen: %d < msg_length: %d, addr: [%s:%d], status: %s(errno: %d)",
			buflen, msg_length, inet_ntoa(serv.sin_addr),
			ntohs(serv.sin_port), strerror(errno), errno);
		return -200;
	}

	bytes = 0;
	nread = 0;
	while (bytes < msg_length) {
		nread = io->read(io, (char *)buf + bytes, (msg_length - bytes), flags);
		if (nread < 1) {
			if (nread == 0) {
				eof = 1;
				break;
			}
			if (errno == EINTR || errno == EAGAIN) {
				WarningLog(
					"receive failure.  nread: %d,  status(%s, errno: %d)",
					nread, strerror(errno), errno);
				continue;
			}
			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"receive failure.  nread: %d,  addr: [%s:%d],  status(%s, errno: %d)",
				nread, inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
			break;
		}
		bytes += nread;
		if (opt_status == TRANSFER_OPT) {
			bandwidth_limit(BW_OP_DOWNLOAD, nread);
		}
	}
	if (bytes != msg_length) {
		getpeername(fd, (struct sockaddr *)&serv, &serv_len);
		if (eof == 0) {
			ErrorLog(
				"receive failure bytes: %d != msg_length: %d, addr: [%s:%d], status: %s(errno: %d)",
				bytes, msg_length, inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
		}
		return eof ? IO_EOF : IO_TRUNCATE;
	}

	return bytes;
}

int rpc_send_io(rpc_io_t *io, void *buf, const int len, int flags)
{
	int fd = io->fd;
	int bytes = 0;
	int nwrite = 0;
	const int msg_length = htonl(len);
	int opt_status = 0;
	struct sockaddr_in serv;
	socklen_t serv_len = sizeof(serv);

	opt_status = (intptr_t)(int *)pthread_getspecific(g_key);

	while (bytes < (int)sizeof(msg_length)) {
		nwrite = io->write(io, ((char *)&msg_length) + bytes,
				   (sizeof(msg_length) - bytes), flags);
		if (nwrite < 1) {
			if (errno == EINTR || errno == EAGAIN) {
				WarningLog(
					"rpc_send failure.  nwrite: %d,  status(%s, errno: %d)",
					nwrite, strerror(errno), errno);
				continue;
			}

			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"rpc_send failure.  nwrite: %d, addr: [%s:%d],  status(%s, errno: %d)",
				nwrite, inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
			break;
		}
		bytes += nwrite;
	}
	if (bytes != (int)sizeof(msg_length)) {
		getpeername(fd, (struct sockaddr *)&serv, &serv_len);
		ErrorLog("rpc_send failure bytes: %d status: %s(errno: %d)",
			 bytes, inet_ntoa(serv.sin_addr), ntohs(serv.sin_port),
			 strerror(errno), errno);
		return -100;
	}

	bytes = 0;
	nwrite = 0;
	while (bytes < len) {
		nwrite = io->write(io, (char *)buf + bytes, len - bytes, flags);
		if (nwrite < 1) {
			if (errno == EINTR || errno == EAGAIN) {
				WarningLog(
					"rpc_send failure.  nwrite: %d,  status(%s, errno: %d)",
					nwrite, strerror(errno), errno);
				continue;
			}
			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"rpc_send failure.  nwrite: %d,  addr: [%s:%d],  status(%s, errno: %d)",
				nwrite, inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
			break;
		}
		bytes += nwrite;
		if (opt_status == TRANSFER_OPT) {
			bandwidth_limit(BW_OP_UPLOAD, nwrite);
		}
	}

	if (len != bytes) {
		getpeername(fd, (struct sockaddr *)&serv, &serv_len);
		ErrorLog("rpc_send failure bytes: %d status: %s(errno: %d)",
			 bytes, inet_ntoa(serv.sin_addr), ntohs(serv.sin_port),
			 strerror(errno), errno);
		return -1;
	}
	return bytes;
}

int rpc_recv(int fd, void *buf, const int buflen, int flags)
{
	rpc_io_t io;
	rpc_io_init_plain(&io, fd);
	return rpc_recv_io(&io, buf, buflen, flags);
}

int rpc_send(int fd, void *buf, const int buflen, int flags)
{
	rpc_io_t io;
	rpc_io_init_plain(&io, fd);
	return rpc_send_io(&io, buf, buflen, flags);
}

int get_keepalive_interval()
{
	return g_rpc_config->keepalive;
}

int connect_server(const char *ip, const unsigned short port,
		   const char *local_ip, const unsigned short local_port)
{
	int opt = 1;
	int sockfd = -1;
	struct sockaddr_in localaddr;
	struct sockaddr_in servaddr;
	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		ErrorLog("create socket error: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	opt = 1;
	if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *)&opt,
		       sizeof(opt))) {
		WarningLog("setsockopt failure.");
	}

	if (g_rpc_config->keepalive > 0 &&
	    sock_keepalive(sockfd, g_rpc_config->keepalive) != 0) {
		ErrorLog("sock_keepalive failed.");
		goto return__;
	}

	if (local_ip[0] != 0x00) {
		memset(&localaddr, 0, sizeof(localaddr));
		localaddr.sin_family = AF_INET;
		localaddr.sin_addr.s_addr = htonl(INADDR_ANY);
		localaddr.sin_port = htons(local_port);
		if (inet_pton(AF_INET, local_ip, &localaddr.sin_addr) <= 0) {
			ErrorLog("inet_pton error for [%s]", local_ip);
		} else {
			if (bind(sockfd, (struct sockaddr *)&localaddr,
				 sizeof(localaddr)) != 0) {
				ErrorLog(
					"bind socket to local [%s:%d] failed status: %s(errno: %d)",
					local_ip, local_port, strerror(errno),
					errno);
			}
		}
	}

	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(port);
	if (inet_pton(AF_INET, ip, &servaddr.sin_addr) <= 0) {
		ErrorLog("inet_pton error for [%s]", ip);
		goto return__;
	}

	if (connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) <
	    0) {
		ErrorLog("connect error: %s(errno: %d)\n", strerror(errno),
			 errno);
		goto return__;
	}

	if (rpc_connect_first_stage(sockfd) != 0)
		goto return__;
	return sockfd;
return__:
	close(sockfd);
	return -1;
}

int connect_server2(const char *ip, const unsigned short port)
{
	int opt = 1;
	int sockfd = -1;
	struct sockaddr_in servaddr;
	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		fprintf(stderr, "create socket error: %s(errno: %d)\n",
			strerror(errno), errno);
		goto return__;
	}

	opt = 1;
	if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const void *)&opt,
		       sizeof(opt))) {
		WarningLog("setsockopt failure.");
	}

	if (g_rpc_config->keepalive > 0 &&
	    sock_keepalive(sockfd, g_rpc_config->keepalive) != 0) {
		ErrorLog("sock_keepalive failed.");
		goto return__;
	}

	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(port);
	if (inet_pton(AF_INET, ip, &servaddr.sin_addr) <= 0) {
		fprintf(stderr, "%d inet_pton error for [%s]\n", __LINE__, ip);
		goto return__;
	}

	if (connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) <
	    0) {
		fprintf(stderr, "connect error: %s(errno: %d)\n",
			strerror(errno), errno);
		goto return__;
	}

	if (rpc_connect_first_stage(sockfd) != 0)
		goto return__;
	return sockfd;
return__:
	close(sockfd);
	return -1;
}

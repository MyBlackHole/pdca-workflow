
#include "bandwidth.h"
#include "common.h"
#include "rpc-protocol.h"
#include "rpc-io.h"
#include "rpc-config.h"
#include "rpc-negotiate.h"
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

#include <map>
#include <mutex>

/* fd→SSL 绑定表：协商升级 TLS 后，把 fd 绑定到 SSL*，使既有
 * rpc_recv/rpc_send 调用方无感走加密通道（服务端 woker 各处理器等）。 */
static std::map<int, SSL *> g_ssl_bindings;
static std::mutex g_ssl_bind_mutex;

int rpc_ssl_bind(int fd, SSL *ssl)
{
	if (fd < 0 || !ssl)
		return -1;
	std::lock_guard<std::mutex> lock(g_ssl_bind_mutex);
	g_ssl_bindings[fd] = ssl;
	return 0;
}

int rpc_ssl_unbind(int fd)
{
	std::lock_guard<std::mutex> lock(g_ssl_bind_mutex);
	return g_ssl_bindings.erase(fd) == 1 ? 0 : -1;
}

SSL *rpc_ssl_lookup(int fd)
{
	std::lock_guard<std::mutex> lock(g_ssl_bind_mutex);
	auto it = g_ssl_bindings.find(fd);
	return it == g_ssl_bindings.end() ? NULL : it->second;
}

void rpc_ssl_cleanup_fd(int fd)
{
	if (fd < 0)
		return;
	SSL *ssl = rpc_ssl_lookup(fd);
	if (!ssl)
		return;
	rpc_ssl_unbind(fd);
	SSL_free(ssl);
}

int rpc_recv(int fd, void *buf, const int buflen, int flags)
{
	int bytes = 0;
	int nread = 0;
	int msg_net_length = 0;
	int opt_status = 0;
	int eof = 0;
	struct sockaddr_in serv;
	socklen_t serv_len = sizeof(serv);

	/* TLS 升级后：fd 绑定 SSL → 透明走加密通道 */
	SSL *bind_ssl = rpc_ssl_lookup(fd);
	if (bind_ssl) {
		return rpc_ssl_recv(bind_ssl, buf, buflen, flags);
	}

	opt_status = (intptr_t)(int *)pthread_getspecific(g_key);

	while (bytes < (int)sizeof(msg_net_length)) {
		nread = recv(fd, ((char *)&msg_net_length) + bytes,
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
		nread = recv(fd, (char *)buf + bytes, (msg_length - bytes),
			     flags);
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

int rpc_send(int fd, void *buf, const int len, int flags)
{
	int bytes = 0;
	int nwrite = 0;
	const int msg_length = htonl(len);
	int opt_status = 0;
	struct sockaddr_in serv;
	socklen_t serv_len = sizeof(serv);

	/* TLS 升级后：fd 绑定 SSL → 透明走加密通道 */
	SSL *bind_ssl = rpc_ssl_lookup(fd);
	if (bind_ssl) {
		return rpc_ssl_send(bind_ssl, buf, len, flags);
	}

	opt_status = (intptr_t)(int *)pthread_getspecific(g_key);

	while (bytes < (int)sizeof(msg_length)) {
		nwrite = send(fd, ((char *)&msg_length) + bytes,
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
		nwrite = send(fd, (char *)buf + bytes, len - bytes, flags);
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

int rpc_ssl_recv(SSL *ssl, void *buf, const int buflen, int flags)
{
	int bytes = 0;
	int nread = 0;
	int msg_net_length = 0;
	int opt_status = 0;
	int eof = 0;
	int fd = -1;
	struct sockaddr_in serv;
	socklen_t serv_len = sizeof(serv);

	(void)flags;
	if (!ssl) {
		return -100;
	}
	fd = SSL_get_fd(ssl);

	opt_status = (intptr_t)(int *)pthread_getspecific(g_key);

	while (bytes < (int)sizeof(msg_net_length)) {
		nread = SSL_read(ssl, ((char *)&msg_net_length) + bytes,
				 (sizeof(msg_net_length) - bytes));
		if (nread <= 0) {
			int ssl_err = SSL_get_error(ssl, nread);
			if (ssl_err == SSL_ERROR_WANT_READ ||
			    ssl_err == SSL_ERROR_WANT_WRITE ||
			    errno == EINTR) {
				WarningLog(
					"rpc_ssl_recv retry.  nread: %d,  status(%s, errno: %d)",
					nread, strerror(errno), errno);
				continue;
			}
			if (ssl_err == SSL_ERROR_ZERO_RETURN ||
			    (ssl_err == SSL_ERROR_SYSCALL && nread == 0)) {
				eof = 1;
				break;
			}
			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"rpc_ssl_recv failure.  nread: %d,  addr: [%s:%d],  status(%s, errno: %d)",
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
				"rpc_ssl_recv failure bytes: %d != (int)sizeof(msg_net_length): %d, addr: [%s:%d], status: %s(errno: %d)",
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
			"rpc_ssl_recv failure buflen: %d < msg_length: %d, addr: [%s:%d], status: %s(errno: %d)",
			buflen, msg_length, inet_ntoa(serv.sin_addr),
			ntohs(serv.sin_port), strerror(errno), errno);
		return -200;
	}

	bytes = 0;
	nread = 0;
	while (bytes < msg_length) {
		nread = SSL_read(ssl, (char *)buf + bytes, msg_length - bytes);
		if (nread <= 0) {
			int ssl_err = SSL_get_error(ssl, nread);
			if (ssl_err == SSL_ERROR_WANT_READ ||
			    ssl_err == SSL_ERROR_WANT_WRITE ||
			    errno == EINTR) {
				WarningLog(
					"rpc_ssl_recv retry.  nread: %d,  status(%s, errno: %d)",
					nread, strerror(errno), errno);
				continue;
			}
			if (ssl_err == SSL_ERROR_ZERO_RETURN ||
			    (ssl_err == SSL_ERROR_SYSCALL && nread == 0)) {
				eof = 1;
				break;
			}
			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"rpc_ssl_recv failure.  nread: %d,  addr: [%s:%d],  status(%s, errno: %d)",
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
				"rpc_ssl_recv failure bytes: %d != msg_length: %d, addr: [%s:%d], status: %s(errno: %d)",
				bytes, msg_length, inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
		}
		return eof ? IO_EOF : IO_TRUNCATE;
	}

	return bytes;
}

int rpc_ssl_send(SSL *ssl, void *buf, const int len, int flags)
{
	int bytes = 0;
	int nwrite = 0;
	const int msg_length = htonl(len);
	int opt_status = 0;
	int fd = -1;
	struct sockaddr_in serv;
	socklen_t serv_len = sizeof(serv);

	(void)flags;
	if (!ssl) {
		return -100;
	}
	fd = SSL_get_fd(ssl);

	opt_status = (intptr_t)(int *)pthread_getspecific(g_key);

	while (bytes < (int)sizeof(msg_length)) {
		nwrite = SSL_write(ssl, ((char *)&msg_length) + bytes,
				   (sizeof(msg_length) - bytes));
		if (nwrite <= 0) {
			int ssl_err = SSL_get_error(ssl, nwrite);
			if (ssl_err == SSL_ERROR_WANT_READ ||
			    ssl_err == SSL_ERROR_WANT_WRITE ||
			    errno == EINTR) {
				WarningLog(
					"rpc_ssl_send retry.  nwrite: %d,  status(%s, errno: %d)",
					nwrite, strerror(errno), errno);
				continue;
			}
			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"rpc_ssl_send failure.  nwrite: %d, addr: [%s:%d],  status(%s, errno: %d)",
				nwrite, inet_ntoa(serv.sin_addr),
				ntohs(serv.sin_port), strerror(errno), errno);
			break;
		}
		bytes += nwrite;
	}
	if (bytes != (int)sizeof(msg_length)) {
		getpeername(fd, (struct sockaddr *)&serv, &serv_len);
		ErrorLog("rpc_ssl_send failure bytes: %d status: %s(errno: %d)",
			 bytes, inet_ntoa(serv.sin_addr), ntohs(serv.sin_port),
			 strerror(errno), errno);
		return -100;
	}

	bytes = 0;
	nwrite = 0;
	while (bytes < len) {
		nwrite = SSL_write(ssl, (char *)buf + bytes, len - bytes);
		if (nwrite <= 0) {
			int ssl_err = SSL_get_error(ssl, nwrite);
			if (ssl_err == SSL_ERROR_WANT_READ ||
			    ssl_err == SSL_ERROR_WANT_WRITE ||
			    errno == EINTR) {
				WarningLog(
					"rpc_ssl_send retry.  nwrite: %d,  status(%s, errno: %d)",
					nwrite, strerror(errno), errno);
				continue;
			}
			getpeername(fd, (struct sockaddr *)&serv, &serv_len);
			ErrorLog(
				"rpc_ssl_send failure.  nwrite: %d,  addr: [%s:%d],  status(%s, errno: %d)",
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
		ErrorLog("rpc_ssl_send failure bytes: %d status: %s(errno: %d)",
			 bytes, inet_ntoa(serv.sin_addr), ntohs(serv.sin_port),
			 strerror(errno), errno);
		return -1;
	}
	return bytes;
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

	/* 协商 + 数据面加密（单端口明文/加密并存）：
	 * 1) 先发独立协商头（无论开关状态），服务端回能力响应；
	 * 2) 判定升级目标：TLS_SM/TLS_GENERIC → 同连接内 TLS 握手并绑定 SSL；
	 *    PLAIN → 保持明文；
	 * 3) 对端超时无响应（旧版无协商）→ 本端配置加密则拒绝，否则明文。 */
	{
		const int tls_enable = sec_tool_tls_enabled(
			"rpc_tls_enable", g_rpc_config->tls_enable_cli);
		uint8_t caps = rpc_capability_from_ciphersuites(
			sec_tool_tls_ciphersuites("rpc_tls_ciphersuites",
						  g_rpc_config
							  ->tls_ciphersuites_cli));
		int sm_ready = (caps & RPC_CAP_SM) ? 1 : 0;
		int tls_ready = (caps & RPC_CAP_TLS) ? 1 : 0;
		int upgrade = -1;
		int neg = rpc_negotiate_client(sockfd, tls_enable, sm_ready,
					       tls_ready, &upgrade);
		if (neg == RPC_TRANSPORT_REJECT) {
			ErrorLog("negotiation rejected for %s:%d (ENC-004)",
				 ip, port);
			close(sockfd);
			sockfd = -1;
			goto return__;
		}
		if (neg == RPC_NEG_ERR_TIMEOUT) {
			/* 对端无协商协议（存量服务端） */
			if (tls_enable) {
				ErrorLog(
					"peer has no negotiation but TLS required for %s:%d",
					ip, port);
				close(sockfd);
				sockfd = -1;
				goto return__;
			}
			return sockfd;
		}
		if (upgrade == RPC_TRANSPORT_TLS_SM ||
		    upgrade == RPC_TRANSPORT_TLS_GENERIC) {
			SSL *ssl = tls_cert_client_handshake(sockfd, NULL);
			if (!ssl) {
				ErrorLog("TLS handshake failed for %s:%d", ip,
					 port);
				close(sockfd);
				sockfd = -1;
				goto return__;
			}
			if (rpc_ssl_bind(sockfd, ssl) != 0) {
				ErrorLog("ssl bind failed for %s:%d", ip, port);
				SSL_free(ssl);
				close(sockfd);
				sockfd = -1;
				goto return__;
			}
		}
	}

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

	/* 协商 + 数据面加密（单端口明文/加密并存）：
	 * 1) 先发独立协商头（无论开关状态），服务端回能力响应；
	 * 2) 判定升级目标：TLS_SM/TLS_GENERIC → 同连接内 TLS 握手并绑定 SSL；
	 *    PLAIN → 保持明文；
	 * 3) 对端超时无响应（旧版无协商）→ 本端配置加密则拒绝，否则明文。 */
	{
		const int tls_enable = sec_tool_tls_enabled(
			"rpc_tls_enable", g_rpc_config->tls_enable_cli);
		uint8_t caps = rpc_capability_from_ciphersuites(
			sec_tool_tls_ciphersuites("rpc_tls_ciphersuites",
						  g_rpc_config
							  ->tls_ciphersuites_cli));
		int sm_ready = (caps & RPC_CAP_SM) ? 1 : 0;
		int tls_ready = (caps & RPC_CAP_TLS) ? 1 : 0;
		int upgrade = -1;
		int neg = rpc_negotiate_client(sockfd, tls_enable, sm_ready,
					       tls_ready, &upgrade);
		if (neg == RPC_TRANSPORT_REJECT) {
			ErrorLog("negotiation rejected for %s:%d (ENC-004)",
				 ip, port);
			close(sockfd);
			sockfd = -1;
			goto return__;
		}
		if (neg == RPC_NEG_ERR_TIMEOUT) {
			/* 对端无协商协议（存量服务端） */
			if (tls_enable) {
				ErrorLog(
					"peer has no negotiation but TLS required for %s:%d",
					ip, port);
				close(sockfd);
				sockfd = -1;
				goto return__;
			}
			return sockfd;
		}
		if (upgrade == RPC_TRANSPORT_TLS_SM ||
		    upgrade == RPC_TRANSPORT_TLS_GENERIC) {
			SSL *ssl = tls_cert_client_handshake(sockfd, NULL);
			if (!ssl) {
				ErrorLog("TLS handshake failed for %s:%d", ip,
					 port);
				close(sockfd);
				sockfd = -1;
				goto return__;
			}
			if (rpc_ssl_bind(sockfd, ssl) != 0) {
				ErrorLog("ssl bind failed for %s:%d", ip, port);
				SSL_free(ssl);
				close(sockfd);
				sockfd = -1;
				goto return__;
			}
		}
	}

	return sockfd;
return__:
	close(sockfd);
	return -1;
}

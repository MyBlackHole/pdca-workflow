#define _GNU_SOURCE

#include "common.h"
#include "misc.h"
#include "logger.h"
#include "module.h"
#include "msg.h"
#include "client.h"
#include "rdbcomm.h"
#include "buf.h"
#include "tls_cert.h"
#include "rdb-config.h"
#include "crypt.h"

#include <sys/stat.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <endian.h>
#include <errno.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>

static uint32_t get_status(struct rdbcomm_conn *conn, uint32_t expected_id);

int rdbcomm_get_time(const char *ip, int port, uint64_t *timestamp)
{
	int fd;
	struct sockaddr_in addr;
	rpc_hs_session_t session;
	int ret;
	if (!ip || !timestamp)
		return -1;
	fd = socket(AF_INET, SOCK_STREAM, 0);
	if (fd < 0)
		return -1;
	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons((uint16_t)port);
	if (inet_aton(ip, &addr.sin_addr) == 0 ||
	    connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		close(fd);
		return -1;
	}
	rpc_hs_session_init_plain(&session, fd);
	ret = rpc_hs_request_time(&session, timestamp);
	close(fd);
	return ret;
}

struct rdbcomm_conn *rdbcomm_new(const char *ip, const int port,
				 client_options *options)
{
	struct rdbcomm_conn *conn = calloc(1, sizeof(struct rdbcomm_conn));
	if (conn == NULL) {
		return NULL;
	}
	conn->sockfd = -1;
	conn->ip = strdup(ip);
	if (options->user) {
		conn->user = strdup(options->user);
	} else {
		conn->user = strdup("test");
	}
	conn->port = port;
	conn->msg_id = 0;
	conn->msgw = buf_new();
	conn->flags = 0;
	conn->sndtimeo = 0;
	conn->rcvtimeo = 0;
	conn->keepalive = 0;
	if (options->key) {
		conn->key = strdup(options->key);
	} else {
		conn->key = NULL;
	}
	if (options->rcvtimeo) {
		conn->rcvtimeo = options->rcvtimeo;
		conn->flags |= RDBCOMM_RCVTIMEO;
	}
	if (options->sndtimeo) {
		conn->sndtimeo = options->sndtimeo;
		conn->flags |= RDBCOMM_SNDTIMEO;
	}
	if (options->keepalive) {
		conn->keepalive = options->keepalive;
		conn->flags |= RDBCOMM_KEEPALIVE;
	}
	if (options->debug) {
		conn->flags |= RDBCOMM_DEBUG;
	}
	if (options->encrypt) {
		conn->flags |= RDBCOMM_ENCRYPT;
	}
	if (conn->msgw == NULL ||
	    buf_set_max_size(conn->msgw, RDBCOMM_MAX_MSG_LENGTH) != 0) {
		ErrorLog("create message buffer error");
		free(conn->user);
		free(conn->ip);
		free(conn);
		return NULL;
	}
	conn->msgr = buf_new();
	if (conn->msgr == NULL ||
	    buf_set_max_size(conn->msgr, RDBCOMM_MAX_MSG_LENGTH) != 0) {
		ErrorLog("create message buffer error");
		buf_free(conn->msgw);
		free(conn->user);
		free(conn->ip);
		free(conn);
		return NULL;
	}
	return conn;
}

int rdbcomm_connect(struct rdbcomm_conn *conn)
{
	int sockfd;
	struct sockaddr_in addr;
	struct buf *msgw = conn->msgw;
	int mid = 0;
	int ret = 0;
	uint32_t status = RDBCOMM_MSG_OK;

	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) {
		ErrorLog("create socket error");
		return -1;
	}
	addr.sin_family = AF_INET;
	addr.sin_port = htons(conn->port);
	if (inet_aton(conn->ip, &addr.sin_addr) == 0) {
		ErrorLog("invalid ip address");
		close(sockfd);
		return -1;
	}

	if ((conn->flags & RDBCOMM_KEEPALIVE) &&
	    sock_keepalive(sockfd, conn->keepalive) != 0) {
		ErrorLog("keepalive error F:%d", sockfd);
		close(sockfd);
		return -1;
	}

	if ((conn->flags & RDBCOMM_SNDTIMEO) &&
	    sock_sendtimeout(sockfd, conn->sndtimeo) != 0) {
		ErrorLog("send timeout error F:%d", sockfd);
		close(sockfd);
		return -1;
	}

	if ((conn->flags & RDBCOMM_RCVTIMEO) &&
	    sock_recvtimeout(sockfd, conn->rcvtimeo) != 0) {
		ErrorLog("recv timeout error F:%d", sockfd);
		close(sockfd);
		return -1;
	}

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("start connect, F:%d", sockfd);
	}

	if (connect(sockfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		ErrorLog("connect error F:%d", sockfd);
		close(sockfd);
		return -1;
	}

	rpc_hs_session_t hs;
	rpc_hs_result_t hs_result = { 0 };
	uint16_t algorithm = sec_tls_ciphersuites() &&
			strstr(sec_tls_ciphersuites(), "SM") ? RPC_HS_ALG_SM
									 : RPC_HS_ALG_CLASSIC;
	rpc_hs_session_init_plain(&hs, sockfd);
	if (rpc_hs_client_negotiate(&hs, sec_tls_enabled(), algorithm,
				    &hs_result) != 0) {
		close(sockfd);
		return -1;
	}
	if (hs_result.result == RPC_HS_OK_MTLS) {
		SSL *ssl = tls_cert_client_handshake_for_cn(sockfd, hs_result.ca_cn,
								 NULL);
		if (!ssl) {
			close(sockfd);
			return -1;
		}
		rpc_hs_session_init_tls(&hs, sockfd, ssl);
	}

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("end connect, F:%d", sockfd);
	}

	conn->sockfd = sockfd;
	conn->io = hs;

	mid = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("init U:%s I:%d F:%d ST:%d RT:%d KT:%d", conn->user,
			 mid, conn->flags, conn->sndtimeo, conn->rcvtimeo,
			 conn->keepalive);
	}

	buf_reset(msgw);
	// 加密 key 后发送
	char *key_to_send = conn->key ? conn->key : "";
	char key_buf[64] = { 0 };
	if (conn->key) {
		size_t key_len = strlen(conn->key);
		if (key_len < sizeof(key_buf)) {
			strncpy(key_buf, conn->key, sizeof(key_buf) - 1);
			data_encrypt((unsigned char *)key_buf, strlen(key_buf));
			key_to_send = key_buf;
		}
	}
	if ((ret = buf_put_u8(msgw, RDBCOMM_INIT)) != 0 ||
	    (ret = buf_put_u32(msgw, mid)) != 0 ||
	    (ret = buf_put_u32(msgw, conn->flags)) != 0 ||
	    (ret = buf_put_u32(msgw, conn->sndtimeo)) != 0 ||
	    (ret = buf_put_u32(msgw, conn->rcvtimeo)) != 0 ||
	    (ret = buf_put_cstring(msgw, key_to_send)) != 0) {
		ErrorLog("build message error");
		close(sockfd);
		conn->sockfd = -1;
		return -1;
	}

	if (send_msg(&conn->io, conn->msgw, 0) < 0) {
		ErrorLog("send message error");
		close(sockfd);
		conn->sockfd = -1;
		return -1;
	}

	status = get_status(conn, mid);
	if (status != RDBCOMM_MSG_OK) {
		ErrorLog("connect error, status:%u", status);
		close(sockfd);
		conn->sockfd = -1;
		return -1;
	}

	return 0;
}

void rdbcomm_free(struct rdbcomm_conn *conn)
{
	if (conn == NULL) {
		return;
	}
	rpc_hs_session_cleanup(&conn->io);
	if (conn->sockfd >= 0) {
		close(conn->sockfd);
	}
	free(conn->user);
	free(conn->key);
	free(conn->ip);
	buf_free(conn->msgw);
	buf_free(conn->msgr);
}

static uint32_t get_status(struct rdbcomm_conn *conn, uint32_t expected_id)
{
	struct buf *msgr = conn->msgr;
	u_char type;
	uint32_t id = 0;
	uint32_t status = 0;
	int ret;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("get_status I:%u, F:%d", expected_id, conn->sockfd);
	}

	ret = get_msg(&conn->io, conn->msgr, conn->flags);
	if (ret < 0) {
		ErrorLog("get message error");
		return -1;
	}
	if ((ret = buf_get_u8(msgr, &type)) != 0 ||
	    (ret = buf_get_u32(msgr, &id)) != 0 ||
	    (ret = buf_get_u32(msgr, &status)) != 0) {
		ErrorLog("parse msg error");
		return -1;
	}
	if (type != RDBCOMM_MSG_STATUS) {
		ErrorLog("Expected RDBCOMM_MSG_STATUS(%u) packet, got T:%u",
			 RDBCOMM_MSG_STATUS, type);
		return -1;
	}

	if (id != expected_id) {
		ErrorLog("ID mismatch (%u != %u)", id, expected_id);
		return -1;
	}

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("get_status I:%u, S:%u", id, status);
	}
	return status;
}

static uint32_t get_handle(struct rdbcomm_conn *conn, uint32_t expected_id,
			   const char *errfmt, ...)
{
	struct buf *msgr = conn->msgr;
	uint32_t id = 0;
	uint32_t status;
	u_char type;
	int handle;
	char errmsg[256];
	va_list args;
	int ret;

	va_start(args, errfmt);
	if (errfmt != NULL)
		vsnprintf(errmsg, sizeof(errmsg), errfmt, args);
	va_end(args);

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("get_handle I:%u, F:%d, %s", expected_id, conn->sockfd,
			 errmsg);
	}

	ret = get_msg(&conn->io, conn->msgr, conn->flags);
	if (ret < 0) {
		ErrorLog("get message error, F:%d, %s", conn->sockfd, errmsg);
		return -1;
	}

	if ((ret = buf_get_u8(msgr, &type)) != 0 ||
	    (ret = buf_get_u32(msgr, &id)) != 0) {
		ErrorLog("parse msg error, F:%d, %s", conn->sockfd, errmsg);
		return -1;
	}

	if (id != expected_id) {
		ErrorLog("ID mismatch (%u != %u), F:%d, %s", id, expected_id,
			 conn->sockfd, errmsg);
		return -1;
	}
	if (type == RDBCOMM_MSG_STATUS) {
		if ((ret = buf_get_u32(msgr, &status)) != 0) {
			ErrorLog("parse status error, F:%d, %s", conn->sockfd,
				 errmsg);
			return -1;
		}
		if (errfmt != NULL) {
			ErrorLog("F:%d, S:%d, %s", conn->sockfd, status,
				 errmsg);
		}
		errno = status;

		return -1;
	} else if (type != RDBCOMM_MSG_HANDLE) {
		ErrorLog(
			"Expected RDBCOMM_MSG_HANDLE(%u) packet, got T:%u, F:%d, %s",
			RDBCOMM_MSG_HANDLE, type, conn->sockfd, errmsg);
		return -1;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&handle)) != 0) {
		ErrorLog("parse handle error, F:%d, %s", conn->sockfd, errmsg);
		return -1;
	}

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("get_handle I:%u, H:%d, F:%d, %s", id, handle,
			 conn->sockfd, errmsg);
	}

	return handle;
}

static int send_open(struct rdbcomm_conn *conn, const char *path,
		     uint32_t flags, int *handlep)
{
	struct buf *msgw = conn->msgw;
	int ret;
	uint32_t id;

	*handlep = -1;

	id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending RDBCOMM_OPEN I:%u P:%s", id, path);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_OPEN)) != 0 ||
	    (ret = buf_put_u32(msgw, id)) != 0 ||
	    (ret = buf_put_u32(msgw, flags)) != 0 ||
	    (ret = buf_put_cstring(msgw, path)) != 0) {
		ErrorLog("build open message error");
		return -1;
	}

	if (send_msg(&conn->io, conn->msgw, conn->flags) < 0) {
		ErrorLog("send open message error");
		return -1;
	}

	*handlep = get_handle(conn, id, "open %s", path);
	if (*handlep < 0)
		return -1;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("open handle I:%u H:%d", id, *handlep);
	}

	return 0;
}

static int send_read(struct rdbcomm_conn *conn, uint64_t offset, u_int len,
		     int handle)
{
	int ret;
	uint32_t status = RDBCOMM_MSG_OK;
	struct buf *msgw = conn->msgw;
	uint32_t id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending RDBCOMM_READ I:%u H:%d O:%lu LEN:%u", id,
			 handle, offset, len);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_READ)) != 0 ||
	    (ret = buf_put_u32(msgw, id)) != 0 ||
	    (ret = buf_put_u32(msgw, (uint32_t)handle)) != 0) {
		ErrorLog("build read message error");
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	if (send_msg(&conn->io, conn->msgw, conn->flags) < 0) {
		ErrorLog("send read message error");
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	status = get_status(conn, id);

exit:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("read handle I:%u H:%d", id, handle);
	}

	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

static int send_write(struct rdbcomm_conn *conn, uint64_t offset, u_int len,
		      int handle)
{
	int ret;
	uint32_t status = RDBCOMM_MSG_OK;
	struct buf *msgw = conn->msgw;
	uint32_t id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending RDBCOMM_WRITE I:%u H:%d O:%lu LEN:%u", id,
			 handle, offset, len);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_WRITE)) != 0 ||
	    (ret = buf_put_u32(msgw, id)) != 0 ||
	    (ret = buf_put_u32(msgw, (uint32_t)handle)) != 0) {
		ErrorLog("build write message error");
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}
	if (send_msg(&conn->io, conn->msgw, conn->flags) < 0) {
		ErrorLog("send write message error");
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	status = get_status(conn, id);
exit:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("status I:%u S:%u", status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

static int send_close(struct rdbcomm_conn *conn, int handle)
{
	uint32_t id, status = RDBCOMM_MSG_FAILURE;
	struct buf *msgw = conn->msgw;
	int r;

	id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending RDBCOMM_CLOSE I:%u H:%d", id, handle);
	}

	buf_reset(msgw);
	if ((r = buf_put_u8(msgw, RDBCOMM_CLOSE)) != 0 ||
	    (r = buf_put_u32(msgw, id)) != 0 ||
	    (r = buf_put_u32(msgw, (uint32_t)handle)) != 0) {
		ErrorLog("build close message error");
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	if (send_msg(&conn->io, conn->msgw, conn->flags) < 0) {
		ErrorLog("send close message error");
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	status = get_status(conn, id);
	if (status != RDBCOMM_MSG_OK) {
		ErrorLog("close handle %d error", handle);
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

exit:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("status I:%u S:%u", id, status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

int file_download(struct rdbcomm_conn *conn, const char *remote_path,
		  const char *local_path)
{
	int handle = 0;
	int ret;
	uint32_t status = RDBCOMM_MSG_OK;
	struct buf *msgr = conn->msgr;
	int local_fd = -1;
	u_char type;
	uint32_t bid;
	uint32_t expected_id = 0;
	size_t len = 0;
	off_t offset = 0;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("download remote %s to local %s", remote_path,
			 local_path);
	}

	local_fd = open(local_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (local_fd == -1) {
		ErrorLog("open local %s E:%s", local_path, strerror(errno));
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	if (send_open(conn, remote_path, O_RDONLY, &handle) != 0) {
		status = RDBCOMM_MSG_FAILURE;
		ErrorLog("send open failed for %s", remote_path);
		goto exit;
	}

	expected_id = conn->msg_id;
	if (send_read(conn, offset, len, handle) != 0) {
		ErrorLog("send read failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	while (1) {
		const u_char *val;
		size_t len = 0;

		ret = get_msg(&conn->io, conn->msgr, conn->flags);
		if (ret < 0) {
			ErrorLog("get message error");
			status = RDBCOMM_MSG_FAILURE;
			goto exit;
		}
		if ((ret = buf_get_u8(msgr, &type)) != 0 ||
		    (ret = buf_get_u32(msgr, &bid)) != 0) {
			ErrorLog("parse msg error");
			status = RDBCOMM_MSG_FAILURE;
			goto exit;
		}

		if (type != RDBCOMM_MSG_DATA) {
			if (type == RDBCOMM_MSG_STATUS) {
				if ((ret = buf_get_u32(msgr, &status))) {
					ErrorLog("parse status error");
					status = RDBCOMM_MSG_FAILURE;
					goto exit;
				}
			}
			ErrorLog(
				"Expected RDBCOMM_MSG_DATA(%u) packet, got T:%u S:%u",
				RDBCOMM_MSG_DATA, type, status);
			status = RDBCOMM_MSG_FAILURE;
			goto exit;
		}

		if ((ret = buf_get_string_direct(msgr, &val, &len))) {
			ErrorLog("parse data error");
			status = RDBCOMM_MSG_FAILURE;
			goto exit;
		}

		if (len > 0) {
			if (write(local_fd, val, len) != len) {
				ErrorLog("write local E:%s", strerror(errno));
				status = RDBCOMM_MSG_FAILURE;
				goto fail;
			}
			offset += len;

			if (conn->flags & RDBCOMM_DEBUG) {
				DebugLog("Received data I:%u O:%lu L:%u", bid,
					 offset, len);
			}
		} else if (len == 0) {
			if (conn->flags & RDBCOMM_DEBUG) {
				DebugLog("Received EOF I:%u O:%lu", bid,
					 offset);
			}
			break;
		} else {
			ErrorLog("read remote LEN:%d", len);
			break;
		}
	}

	status = get_status(conn, expected_id);
	if (status != RDBCOMM_MSG_OK) {
		ErrorLog("read remote %s failed", remote_path);
		goto fail;
	}

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("download remote %s to local %s S:%u", remote_path,
			 local_path, status);
	}
fail:
	if (send_close(conn, handle) != 0)
		status = RDBCOMM_MSG_FAILURE;
exit:
	if (local_fd != -1)
		close(local_fd);
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

int file_upload(struct rdbcomm_conn *conn, const char *local_path,
		const char *remote_path)
{
	int ret, local_fd;
	uint32_t status = RDBCOMM_MSG_OK;
	off_t offset = 0;
	size_t len = 0;
	struct buf *msgw = conn->msgw;
	uint32_t expected_id = 0;
	int handle;
	u_int32_t bid = 0;
	struct stat st;
	int flag = O_WRONLY | O_CREAT | O_TRUNC;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("upload local %s to remote %s", local_path,
			 remote_path);
	}

	if ((local_fd = open(local_path, O_RDONLY)) == -1) {
		ErrorLog("open local %s E:%s", local_path, strerror(errno));
		return -1;
	}

	if (fstat(local_fd, &st) == -1) {
		ErrorLog("stat local S:%s F:%d E:%s", local_path, local_fd,
			 strerror(errno));
		return -1;
	}

	if (S_ISDIR(st.st_mode)) {
		ErrorLog("local %s is a directory", local_path);
		return -1;
	}

	if (send_open(conn, remote_path, flag, &handle) != 0) {
		ErrorLog("send open failed for %s", remote_path);
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	expected_id = conn->msg_id;
	if (send_write(conn, offset, len, handle) != 0) {
		ErrorLog("send write failed");
		status = RDBCOMM_MSG_FAILURE;
		goto exit;
	}

	while (1) {
		u_char *valp = NULL;
		u_char *len32 = NULL;
		size_t len = 0;
		size_t size = 0;

		buf_reset(msgw);
		if ((ret = buf_put_u8(msgw, RDBCOMM_MSG_DATA)) != 0 ||
		    (ret = buf_put_u32(msgw, bid++)) != 0 ||
		    (ret = buf_put_string_direct(msgw, &len32, &valp, &size)) !=
			    0) {
			ErrorLog("build data I:%u O:%lu L:%u failed", bid,
				 offset, len);
			status = RDBCOMM_MSG_FAILURE;
			goto exit;
		}

		do
			len = read(local_fd, valp, size);
		while ((len == -1) && (errno == EINTR || errno == EAGAIN ||
				       errno == EWOULDBLOCK));

		if (len >= 0) {
			offset += len;

			put_u32(len32, len);
			if (size > len) {
				buf_unreserve(msgw, size - len);
			}

			ret = send_msg(&conn->io, conn->msgw, conn->flags);
			if (ret < 0) {
				ErrorLog("send data I:%u O:%lu L:%u failed",
					 bid, offset, len);
				status = RDBCOMM_MSG_FAILURE;
				goto exit;
			} else {
				ret = 0;
			}
			if (conn->flags & RDBCOMM_DEBUG) {
				DebugLog("Sent data I:%u O:%lu L:%u", bid,
					 offset, len);
			}
		}

		if (len > 0) {
			if (conn->flags & RDBCOMM_DEBUG) {
				DebugLog("Sent data I:%u O:%lu L:%u", bid,
					 offset, len);
			}
		} else if (len == 0) {
			if (conn->flags & RDBCOMM_DEBUG) {
				DebugLog("Sent EOF I:%u O:%lu", bid, offset);
			}
			break;
		} else {
			ErrorLog("read local E:%s", strerror(errno));
			status = RDBCOMM_MSG_FAILURE;
			goto fail;
		}
	}

	status = get_status(conn, expected_id);
	if (status != RDBCOMM_MSG_OK) {
		ErrorLog("upload local %s to remote %s failed", local_path,
			 remote_path);
		goto fail;
	}
fail:
	if (send_close(conn, handle) != 0) {
		ErrorLog("send close H:%d failed", handle);
		status = RDBCOMM_MSG_FAILURE;
	}
exit:
	if (close(local_fd) == -1) {
		ErrorLog("close local %s E:%s", local_path, strerror(errno));
		status = RDBCOMM_MSG_FAILURE;
	}

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("upload local %s to remote %s S:%u", local_path,
			 remote_path, status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

int module_register(struct rdbcomm_conn *conn, const char *name)
{
	struct buf *msgw = conn->msgw;
	int ret;
	uint32_t expected_id;
	uint32_t status = RDBCOMM_MSG_OK;

	expected_id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending message RDBCOMM_MODULE_REGISTER I:%u N:%s",
			 expected_id, name);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_MODULE_REGISTER)) != 0 ||
	    (ret = buf_put_u32(msgw, expected_id)) != 0 ||
	    (ret = buf_put_cstring(msgw, name)) != 0) {
		ErrorLog("build message RDBCOMM_MODULE_REGISTER failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	ret = send_msg(&conn->io, conn->msgw, conn->flags);
	if (ret < 0) {
		ErrorLog("send message RDBCOMM_MODULE_REGISTER failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	status = get_status(conn, expected_id);

fail:
	if (status != RDBCOMM_MSG_OK) {
		fprintf(stdout, "RDBCOMM_MODULE_REGISTER status I:%u N:%s S:%d",
			expected_id, name, status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

int module_unregister(struct rdbcomm_conn *conn, const char *name)
{
	struct buf *msgw = conn->msgw;
	int ret;
	uint32_t expected_id;
	uint32_t status = RDBCOMM_MSG_OK;

	expected_id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending message RDBCOMM_MODULE_UNREGISTER I:%u N:%s",
			 expected_id, name);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_MODULE_UNREGISTER)) != 0 ||
	    (ret = buf_put_u32(msgw, expected_id)) != 0 ||
	    (ret = buf_put_cstring(msgw, name)) != 0) {
		ErrorLog("build message RDBCOMM_MODULE_UNREGISTER failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	ret = send_msg(&conn->io, conn->msgw, conn->flags);
	if (ret < 0) {
		ErrorLog("send message RDBCOMM_MODULE_UNREGISTER failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	status = get_status(conn, expected_id);

fail:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("RDBCOMM_MODULE_UNREGISTER status I:%u N:%s S:%d",
			 expected_id, name, status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

int module_start(struct rdbcomm_conn *conn, const char *name)
{
	struct buf *msgw = conn->msgw;
	int ret;
	uint32_t expected_id;
	uint32_t status = RDBCOMM_MSG_OK;

	expected_id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending message RDBCOMM_MODULE_START I:%u N:%s",
			 expected_id, name);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_MODULE_START)) != 0 ||
	    (ret = buf_put_u32(msgw, expected_id)) != 0 ||
	    (ret = buf_put_cstring(msgw, name)) != 0) {
		ErrorLog("build message RDBCOMM_MODULE_START failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	ret = send_msg(&conn->io, conn->msgw, conn->flags);
	if (ret < 0) {
		ErrorLog("send message RDBCOMM_MODULE_START failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	status = get_status(conn, expected_id);

fail:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("RDBCOMM_MODULE_START status I:%u N:%s S:%d",
			 expected_id, name, status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

int module_stop(struct rdbcomm_conn *conn, const char *name)
{
	struct buf *msgw = conn->msgw;
	int ret;
	uint32_t expected_id;
	uint32_t status = RDBCOMM_MSG_OK;

	expected_id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending message RDBCOMM_MODULE_STOP I:%u N:%s",
			 expected_id, name);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_MODULE_STOP)) != 0 ||
	    (ret = buf_put_u32(msgw, expected_id)) != 0 ||
	    (ret = buf_put_cstring(msgw, name)) != 0) {
		ErrorLog("build message RDBCOMM_MODULE_STOP failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	ret = send_msg(&conn->io, conn->msgw, conn->flags);
	if (ret < 0) {
		ErrorLog("send message RDBCOMM_MODULE_STOP failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	status = get_status(conn, expected_id);
fail:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("RDBCOMM_MODULE_STOP status I:%u N:%s S:%d",
			 expected_id, name, status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

int execute_cmd(struct rdbcomm_conn *conn, const char *cmd)
{
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	int ret;
	uint32_t expected_id;
	uint32_t status = RDBCOMM_MSG_OK;
	u_char type;
	uint32_t bid;

	expected_id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending message RDBCOMM_EXEC_CMD I:%u C:%s",
			 expected_id, cmd);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_EXEC_CMD)) != 0 ||
	    (ret = buf_put_u32(msgw, expected_id)) != 0 ||
	    (ret = buf_put_cstring(msgw, cmd)) != 0) {
		ErrorLog("build message RDBCOMM_EXEC_CMD failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	ret = send_msg(&conn->io, conn->msgw, conn->flags);
	if (ret < 0) {
		ErrorLog("send message RDBCOMM_EXEC_CMD failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	status = get_status(conn, expected_id);

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("RDBCOMM_EXEC_CMD C:%s I:%u S:%d", cmd, expected_id,
			 status);
	}

	if (status != RDBCOMM_MSG_OK) {
		ErrorLog("execute command C:%s S:%s", cmd, status);
		goto fail;
	}

	while (1) {
		const u_char *val;
		size_t len = 0;

	ret = get_msg(&conn->io, conn->msgr, conn->flags);
		if (ret < 0) {
			ErrorLog("get message RDBCOMM_EXEC_CMD failed");
			status = RDBCOMM_MSG_FAILURE;
			goto fail;
		}

		if ((ret = buf_get_u8(msgr, &type)) != 0 ||
		    (ret = buf_get_u32(msgr, &bid)) != 0) {
			ErrorLog("parse message RDBCOMM_EXEC_CMD failed");
			status = RDBCOMM_MSG_FAILURE;
			goto fail;
		}

		if (type == RDBCOMM_MSG_NODATA) {
			if (conn->flags & RDBCOMM_DEBUG) {
				DebugLog("read I:%d LEN:%d E:%s", bid, len,
					 strerror(errno));
			}
			continue;
		}

		if (type != RDBCOMM_MSG_DATA) {
			ErrorLog(
				"Expected RDBCOMM_MSG_DATA(%u) packet, got T:%u",
				RDBCOMM_MSG_DATA, type);
			status = RDBCOMM_MSG_FAILURE;
			goto fail;
		}

		if ((ret = buf_get_string_direct(msgr, &val, &len)) != 0) {
			ErrorLog("parse message RDBCOMM_EXEC_CMD failed");
			status = RDBCOMM_MSG_FAILURE;
			goto fail;
		}

		if (len > 0) {
			// printf("%.*s", (int)len, val);
			if (write(STDOUT_FILENO, val, len) != len) {
				ErrorLog("write failed, LEN:%ld E:%s", len,
					 strerror(errno));
				status = RDBCOMM_MSG_FAILURE;
				goto fail;
			}
		} else if (len == 0) {
			if (conn->flags & RDBCOMM_DEBUG) {
				DebugLog("Received EOF I:%u", bid);
			}
			break;
		} else {
			status = RDBCOMM_MSG_FAILURE;
			ErrorLog("received failure len %ld", len);
			break;
		}
	}

	status = get_status(conn, expected_id);

fail:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("cmd C:%s I:%u S:%d", cmd, expected_id, status);
	}

	return status;
}

int module_list(struct rdbcomm_conn *conn)
{
	int ret;
	int num;
	uint32_t status = RDBCOMM_MSG_OK;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	u_char type;
	uint32_t bid;
	uint32_t expected_id = 0;

	expected_id = conn->msg_id++;

	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Sending message RDBCOMM_MODULE_LIST I:%u",
			 expected_id);
	}

	buf_reset(msgw);
	if ((ret = buf_put_u8(msgw, RDBCOMM_MODULE_LIST)) != 0 ||
	    (ret = buf_put_u32(msgw, expected_id)) != 0) {
		ErrorLog("build message RDBCOMM_MODULE_LIST failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	ret = send_msg(&conn->io, conn->msgw, conn->flags);
	if (ret < 0) {
		ErrorLog("send message RDBCOMM_MODULE_LIST failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	}

	num = get_handle(conn, expected_id, "module list");
	if (num < 0) {
		ErrorLog("get handle num RDBCOMM_MODULE_LIST failed");
		status = RDBCOMM_MSG_FAILURE;
		goto fail;
	} else {
		if (conn->flags & RDBCOMM_DEBUG) {
			DebugLog("Got handle num RDBCOMM_MODULE_LIST I:%u H:%d",
				 expected_id, num);
		}
	}

	for (bid = 0; bid < num; bid++) {
		plugin_info_t *info = NULL;
		const u_char *val;
		size_t len = 0;

	ret = get_msg(&conn->io, conn->msgr, conn->flags);
		if (ret < 0) {
			ErrorLog("get message RDBCOMM_MODULE_LIST failed");
			status = RDBCOMM_MSG_FAILURE;
			goto fail;
		}
		if ((ret = buf_get_u8(msgr, &type)) != 0 ||
		    (ret = buf_get_u32(msgr, &bid)) != 0 ||
		    (ret = buf_get_string_direct(msgr, &val, &len))) {
			ErrorLog("parse message RDBCOMM_MODULE_LIST failed");
			status = RDBCOMM_MSG_FAILURE;
			goto fail;
		}
		info = (plugin_info_t *)val;
		printf("%s %s %s\n", info->name, info->version, info->path);
	}

fail:
	if (conn->flags & RDBCOMM_DEBUG) {
		DebugLog("Received EOF I:%u S:%d", expected_id, status);
	}
	return status == RDBCOMM_MSG_OK ? 0 : -1;
}

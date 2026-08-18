#include "rpc-handshake.h"

#include <arpa/inet.h>
#include <endian.h>
#include <errno.h>
#include <sys/socket.h>
#include <string.h>
#include <unistd.h>

#define RPC_HS_FIXED_SIZE 18

static void put16(uint8_t *p, uint16_t v)
{
	uint16_t n = htons(v);
	memcpy(p, &n, sizeof(n));
}

static uint16_t get16(const uint8_t *p)
{
	uint16_t n;
	memcpy(&n, p, sizeof(n));
	return ntohs(n);
}

static void put32(uint8_t *p, uint32_t v)
{
	uint32_t n = htonl(v);
	memcpy(p, &n, sizeof(n));
}

static uint32_t get32(const uint8_t *p)
{
	uint32_t n;
	memcpy(&n, p, sizeof(n));
	return ntohl(n);
}

int rpc_hs_encode(const rpc_hs_message_t *message, const void *payload,
		  uint8_t *wire, uint32_t wire_size, uint32_t *wire_length)
{
	uint32_t name_len;
	uint32_t total;

	if (!message || !wire || !wire_length || message->version == 0 ||
	    message->operation == 0 || message->payload_length > RPC_HS_MAX_PAYLOAD)
		return -EINVAL;
	name_len = (uint32_t)strnlen(message->ca_cn, RPC_HS_MAX_NAME + 1);
	if (name_len > RPC_HS_MAX_NAME ||
	    message->payload_length > UINT32_MAX - RPC_HS_FIXED_SIZE - name_len)
		return -EINVAL;
	total = RPC_HS_FIXED_SIZE + name_len + message->payload_length;
	if (wire_size < total || (message->payload_length && !payload))
		return -EMSGSIZE;

	memcpy(wire, RPC_HS_MAGIC, 4);
	wire[4] = message->version;
	wire[5] = message->operation;
	put16(wire + 6, message->flags);
	put16(wire + 8, message->algorithm);
	put16(wire + 10, message->result);
	put16(wire + 12, (uint16_t)name_len);
	put32(wire + 14, message->payload_length);
	if (name_len)
		memcpy(wire + RPC_HS_FIXED_SIZE, message->ca_cn, name_len);
	if (message->payload_length)
		memcpy(wire + RPC_HS_FIXED_SIZE + name_len, payload,
		       message->payload_length);
	*wire_length = total;
	return 0;
}

int rpc_hs_decode(rpc_hs_message_t *message, const uint8_t *wire,
		  uint32_t wire_length, const uint8_t **payload)
{
	uint16_t name_len;
	uint32_t payload_len;
	uint32_t total;

	if (!message || !wire || wire_length < RPC_HS_FIXED_SIZE)
		return -EINVAL;
	if (memcmp(wire, RPC_HS_MAGIC, 4) != 0)
		return RPC_HS_ERR_BAD_MAGIC;
	if (wire[4] != RPC_HS_VERSION)
		return RPC_HS_ERR_BAD_VERSION;
	name_len = get16(wire + 12);
	payload_len = get32(wire + 14);
	if (name_len > RPC_HS_MAX_NAME || payload_len > RPC_HS_MAX_PAYLOAD)
		return RPC_HS_ERR_FRAME;
	total = RPC_HS_FIXED_SIZE + name_len + payload_len;
	if (total != wire_length)
		return RPC_HS_ERR_FRAME;

	memset(message, 0, sizeof(*message));
	message->version = wire[4];
	message->operation = wire[5];
	message->flags = get16(wire + 6);
	message->algorithm = get16(wire + 8);
	message->result = get16(wire + 10);
	message->payload_length = payload_len;
	if (name_len)
		memcpy(message->ca_cn, wire + RPC_HS_FIXED_SIZE, name_len);
	message->ca_cn[name_len] = '\0';
	if (payload)
		*payload = wire + RPC_HS_FIXED_SIZE + name_len;
	return 0;
}

uint16_t rpc_hs_decide(uint16_t client_flags, uint16_t server_flags,
			      uint16_t client_algorithm,
			      uint16_t server_algorithm,
			      uint16_t *result)
{
	int client_mtls = (client_flags & RPC_HS_F_MTLS_REQUEST) != 0;
	int server_mtls = (server_flags & RPC_HS_F_MTLS_REQUIRED) != 0;

	if (server_mtls && (!client_mtls || client_algorithm != server_algorithm)) {
		if (result)
			*result = RPC_HS_ERR_MTLS_REQUIRED;
		return 0;
	}
	if (client_mtls && client_algorithm != server_algorithm) {
		if (result)
			*result = RPC_HS_ERR_ALGORITHM;
		return 0;
	}
	if (result)
		*result = (client_mtls || server_mtls) ? RPC_HS_OK_MTLS : RPC_HS_OK_PLAIN;
	return 1;
}

static ssize_t plain_read(rpc_hs_session_t *session, void *buf, size_t len,
				  int flags)
{
	return recv(session->fd, buf, len, flags);
}

static ssize_t plain_write(rpc_hs_session_t *session, const void *buf,
				   size_t len, int flags)
{
	return send(session->fd, buf, len, flags);
}

static ssize_t tls_read(rpc_hs_session_t *session, void *buf, size_t len,
				int flags)
{
	(void)flags;
	return SSL_read(session->ssl, buf, (int)len);
}

static ssize_t tls_write(rpc_hs_session_t *session, const void *buf,
				 size_t len, int flags)
{
	(void)flags;
	return SSL_write(session->ssl, buf, (int)len);
}

void rpc_hs_session_init_plain(rpc_hs_session_t *session, int fd)
{
	memset(session, 0, sizeof(*session));
	session->fd = fd;
	session->read = plain_read;
	session->write = plain_write;
}

void rpc_hs_session_init_tls(rpc_hs_session_t *session, int fd, SSL *ssl)
{
	memset(session, 0, sizeof(*session));
	session->fd = fd;
	session->ssl = ssl;
	session->read = tls_read;
	session->write = tls_write;
}

void rpc_hs_session_cleanup(rpc_hs_session_t *session)
{
	if (!session)
		return;
	if (session->ssl) {
		SSL_shutdown(session->ssl);
		SSL_free(session->ssl);
	}
	session->ssl = NULL;
	session->read = NULL;
	session->write = NULL;
}

static int io_full(rpc_hs_session_t *session, void *buf, uint32_t length,
			   int writing)
{
	uint8_t *p = (uint8_t *)buf;
	uint32_t done = 0;
	while (done < length) {
		ssize_t n = writing ? session->write(session, p + done,
						     length - done, 0)
				    : session->read(session, p + done, length - done, 0);
		if (n < 0 && errno == EINTR)
			continue;
		if (n <= 0)
			return -EIO;
		done += (uint32_t)n;
	}
	return 0;
}

int rpc_hs_send(rpc_hs_session_t *session, const rpc_hs_message_t *message,
		const void *payload)
{
	uint8_t wire[RPC_HS_FIXED_SIZE + RPC_HS_MAX_NAME + RPC_HS_MAX_PAYLOAD];
	uint32_t length = 0;
	int ret = rpc_hs_encode(message, payload, wire, sizeof(wire), &length);
	if (ret != 0)
		return ret;
	return io_full(session, wire, length, 1);
}

int rpc_hs_recv(rpc_hs_session_t *session, rpc_hs_message_t *message,
		uint8_t *payload,
		uint32_t payload_size)
{
	uint8_t fixed[RPC_HS_FIXED_SIZE];
	uint8_t name[RPC_HS_MAX_NAME];
	uint16_t name_len;
	uint32_t body_len;
	int ret;

	ret = io_full(session, fixed, sizeof(fixed), 0);
	if (ret != 0)
		return ret;
	if (memcmp(fixed, RPC_HS_MAGIC, 4) != 0)
		return RPC_HS_ERR_BAD_MAGIC;
	name_len = get16(fixed + 12);
	body_len = get32(fixed + 14);
	if (name_len > RPC_HS_MAX_NAME || body_len > RPC_HS_MAX_PAYLOAD ||
		body_len > payload_size)
		return RPC_HS_ERR_FRAME;
	if (name_len && io_full(session, name, name_len, 0) != 0)
		return -EIO;
	{
		uint32_t total = RPC_HS_FIXED_SIZE + name_len + body_len;
		uint8_t wire[RPC_HS_FIXED_SIZE + RPC_HS_MAX_NAME + RPC_HS_MAX_PAYLOAD];
		memcpy(wire, fixed, RPC_HS_FIXED_SIZE);
		if (name_len)
			memcpy(wire + RPC_HS_FIXED_SIZE, name, name_len);
		if (body_len && io_full(session, wire + RPC_HS_FIXED_SIZE + name_len,
					body_len, 0) != 0)
			return -EIO;
		ret = rpc_hs_decode(message, wire, total, NULL);
		if (ret != 0)
			return ret;
		if (body_len)
			memcpy(payload, wire + RPC_HS_FIXED_SIZE + name_len, body_len);
	}
	return 0;
}

int rpc_hs_client_negotiate(rpc_hs_session_t *session, int want_mtls,
			    uint16_t algorithm,
			    rpc_hs_result_t *result)
{
	rpc_hs_message_t req = { 0 }, resp = { 0 };
	uint8_t payload[RPC_HS_MAX_PAYLOAD];
	int ret;
	req.version = RPC_HS_VERSION;
	req.operation = RPC_HS_OP_NEGOTIATE;
	req.flags = want_mtls ? RPC_HS_F_MTLS_REQUEST : 0;
	req.algorithm = algorithm;
	ret = rpc_hs_send(session, &req, NULL);
	if (ret != 0)
		return ret;
	ret = rpc_hs_recv(session, &resp, payload, sizeof(payload));
	if (ret != 0 || !(resp.flags & RPC_HS_F_RESPONSE))
		return ret ? ret : RPC_HS_ERR_FRAME;
	if (result) {
		result->result = resp.result;
		result->algorithm = resp.algorithm;
		strncpy(result->ca_cn, resp.ca_cn, RPC_HS_MAX_NAME);
		result->ca_cn[RPC_HS_MAX_NAME] = '\0';
	}
	return resp.result >= RPC_HS_OK_TIME && resp.result <= RPC_HS_OK_MTLS
		       ? 0
		       : -(int)resp.result;
}

int rpc_hs_server_negotiate(rpc_hs_session_t *session, int force_mtls,
			    uint16_t algorithm,
			    const char *ca_cn, rpc_hs_result_t *result)
{
	rpc_hs_message_t req = { 0 };
	uint8_t payload[RPC_HS_MAX_PAYLOAD];
	int ret;
	ret = rpc_hs_recv(session, &req, payload, sizeof(payload));
	if (ret != 0)
		return ret;
	return rpc_hs_server_respond(session, &req, force_mtls, algorithm, ca_cn,
				    result);
}

int rpc_hs_server_respond(rpc_hs_session_t *session,
			  const rpc_hs_message_t *request,
			  int force_mtls, uint16_t algorithm, const char *ca_cn,
			  rpc_hs_result_t *result)
{
	rpc_hs_message_t resp = { 0 };
	uint16_t selected = 0;
	int ret;
	if (!request)
		return -EINVAL;
	if (request->operation != RPC_HS_OP_NEGOTIATE)
		return RPC_HS_ERR_BAD_OPERATION;
	if (!rpc_hs_decide(request->flags,
			   force_mtls ? RPC_HS_F_MTLS_REQUIRED : 0,
			   request->algorithm, algorithm, &selected)) {
		resp.result = selected;
	} else {
		resp.result = selected;
		resp.algorithm = algorithm;
		if (selected == RPC_HS_OK_MTLS && ca_cn)
			strncpy(resp.ca_cn, ca_cn, RPC_HS_MAX_NAME);
		if (selected == RPC_HS_OK_MTLS && (!ca_cn || !ca_cn[0]))
			resp.result = RPC_HS_ERR_CA_CN;
	}
	resp.version = RPC_HS_VERSION;
	resp.operation = RPC_HS_OP_NEGOTIATE;
	resp.flags = RPC_HS_F_RESPONSE;
	ret = rpc_hs_send(session, &resp, NULL);
	if (ret != 0)
		return ret;
	if (result) {
		result->result = resp.result;
		result->algorithm = resp.algorithm;
		strncpy(result->ca_cn, resp.ca_cn, RPC_HS_MAX_NAME);
		result->ca_cn[RPC_HS_MAX_NAME] = '\0';
	}
	return resp.result == RPC_HS_OK_PLAIN || resp.result == RPC_HS_OK_MTLS
		       ? 0
		       : -(int)resp.result;
}

int rpc_hs_send_time_response(rpc_hs_session_t *session, uint64_t timestamp)
{
	rpc_hs_message_t resp = { 0 };
	uint64_t net_timestamp = htobe64(timestamp);
	resp.version = RPC_HS_VERSION;
	resp.operation = RPC_HS_OP_TIME;
	resp.flags = RPC_HS_F_RESPONSE;
	resp.result = RPC_HS_OK_TIME;
	resp.payload_length = sizeof(net_timestamp);
	return rpc_hs_send(session, &resp, &net_timestamp);
}

int rpc_hs_send_error(rpc_hs_session_t *session, uint16_t operation,
			     uint16_t result)
{
	rpc_hs_message_t response = { 0 };
	response.version = RPC_HS_VERSION;
	response.operation = operation ? operation : RPC_HS_OP_NEGOTIATE;
	response.flags = RPC_HS_F_RESPONSE;
	response.result = result;
	return rpc_hs_send(session, &response, NULL);
}

int rpc_hs_request_time(rpc_hs_session_t *session, uint64_t *timestamp)
{
	rpc_hs_message_t req = { 0 }, resp = { 0 };
	uint8_t payload[sizeof(uint64_t)];
	int ret;
	uint64_t net_timestamp;
	if (!timestamp)
		return -EINVAL;
	req.version = RPC_HS_VERSION;
	req.operation = RPC_HS_OP_TIME;
	ret = rpc_hs_send(session, &req, NULL);
	if (ret != 0)
		return ret;
	ret = rpc_hs_recv(session, &resp, payload, sizeof(payload));
	if (ret != 0)
		return ret;
	if (!(resp.flags & RPC_HS_F_RESPONSE) || resp.operation != RPC_HS_OP_TIME ||
		resp.result != RPC_HS_OK_TIME || resp.payload_length != sizeof(uint64_t))
		return -EPROTO;
	memcpy(&net_timestamp, payload, sizeof(net_timestamp));
	*timestamp = be64toh(net_timestamp);
	return 0;
}

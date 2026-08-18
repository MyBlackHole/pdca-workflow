#include "rpc-negotiate.h"

#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>

/* 能力位图中"算法就绪"部分（不含开关与版本位） */
#define RPC_CAP_ALGO_MASK (RPC_CAP_SM | RPC_CAP_TLS)

static int hdr_validate(const rpc_negotiate_header_t *hdr)
{
	if (!hdr)
		return -1;
	if (memcmp(hdr->magic, RPC_NEG_MAGIC, RPC_NEG_MAGIC_LEN) != 0)
		return -1;
	if (hdr->version != RPC_NEG_VERSION)
		return -1;
	return 0;
}

int rpc_negotiate_encode(const rpc_negotiate_header_t *hdr, uint8_t *wire,
			 int wire_len)
{
	if (!hdr || !wire)
		return -1;
	if (wire_len < RPC_NEG_HEADER_LEN)
		return -1;

	memcpy(wire, hdr->magic, RPC_NEG_MAGIC_LEN);
	wire[RPC_NEG_MAGIC_LEN] = hdr->version;
	wire[RPC_NEG_MAGIC_LEN + 1] = hdr->capability;
	wire[RPC_NEG_MAGIC_LEN + 2] = hdr->result;
	wire[RPC_NEG_MAGIC_LEN + 3] = hdr->reserved;
	return RPC_NEG_HEADER_LEN;
}

int rpc_negotiate_decode(rpc_negotiate_header_t *hdr, const uint8_t *wire,
			 int wire_len)
{
	if (!hdr || !wire)
		return -1;
	if (wire_len < RPC_NEG_HEADER_LEN)
		return -1;

	rpc_negotiate_header_t tmp;
	memcpy(tmp.magic, wire, RPC_NEG_MAGIC_LEN);
	tmp.version = wire[RPC_NEG_MAGIC_LEN];
	tmp.capability = wire[RPC_NEG_MAGIC_LEN + 1];
	tmp.result = wire[RPC_NEG_MAGIC_LEN + 2];
	tmp.reserved = wire[RPC_NEG_MAGIC_LEN + 3];

	if (hdr_validate(&tmp) != 0)
		return -1;

	*hdr = tmp;
	return 0;
}

uint8_t rpc_capability_from_ciphersuites(const char *ciphersuites)
{
	uint8_t cap = 0;

	if (ciphersuites == NULL || ciphersuites[0] == '\0') {
		/* 未配置算法 → 默认国密（对齐 PRD"默认算法为国密"） */
		cap |= RPC_CAP_SM;
		return cap;
	}

	if (strstr(ciphersuites, "TLS_SM") != NULL)
		cap |= RPC_CAP_SM;
	if (strstr(ciphersuites, "TLS_AES") != NULL ||
	    strstr(ciphersuites, "AES") != NULL)
		cap |= RPC_CAP_TLS;

	return cap;
}

int rpc_decide_transport(int tls_enable, int sm_ready, int tls_ready,
			 int peer_sm, int peer_tls)
{
	if (!tls_enable)
		return RPC_TRANSPORT_PLAIN;

	/* 开关开启：按本端算法就绪选择套件（默认国密优先） */
	if (sm_ready) {
		return peer_sm ? RPC_TRANSPORT_TLS_SM : RPC_TRANSPORT_REJECT;
	}
	if (tls_ready) {
		return peer_tls ? RPC_TRANSPORT_TLS_GENERIC
				: RPC_TRANSPORT_REJECT;
	}
	/* 本端无任何算法就绪 → ENC-004 */
	return RPC_TRANSPORT_REJECT;
}

/* ---- 协商 IO（fd 全量读写 + 超时） ---- */

static int neg_wait_readable(int fd, int timeout_ms)
{
	struct pollfd pfd;
	pfd.fd = fd;
	pfd.events = POLLIN;
	int ret = poll(&pfd, 1, timeout_ms);
	if (ret == 0) {
		errno = ETIMEDOUT;
		return -1;
	}
	if (ret < 0)
		return -1;
	return 0;
}

static int neg_read_all(int fd, void *buf, size_t len)
{
	uint8_t *p = (uint8_t *)buf;
	size_t got = 0;
	while (got < len) {
		if (neg_wait_readable(fd, RPC_NEG_TIMEOUT_MS) != 0)
			return -1;
		ssize_t n = read(fd, p + got, len - got);
		if (n < 0) {
			if (errno == EINTR)
				continue;
			return -1;
		}
		if (n == 0) {
			errno = ECONNRESET;
			return -1;
		}
		got += n;
	}
	return 0;
}

static int neg_write_all(int fd, const void *buf, size_t len)
{
	const uint8_t *p = (const uint8_t *)buf;
	size_t sent = 0;
	while (sent < len) {
		ssize_t n = write(fd, p + sent, len - sent);
		if (n < 0) {
			if (errno == EINTR)
				continue;
			return -1;
		}
		sent += n;
	}
	return 0;
}

int rpc_negotiate_client(int fd, int tls_enable, int sm_ready, int tls_ready,
			 int *upgrade)
{
	rpc_negotiate_header_t hdr;
	uint8_t wire[RPC_NEG_HEADER_LEN];
	int ret = RPC_TRANSPORT_REJECT;

	if (upgrade)
		*upgrade = -1;

	memset(&hdr, 0, sizeof(hdr));
	memcpy(hdr.magic, RPC_NEG_MAGIC, RPC_NEG_MAGIC_LEN);
	hdr.version = RPC_NEG_VERSION;
	hdr.capability = RPC_CAP_VER_MATCH;
	if (tls_enable) {
		hdr.capability |= RPC_CAP_ENCRYPT;
		if (sm_ready)
			hdr.capability |= RPC_CAP_SM;
		if (tls_ready)
			hdr.capability |= RPC_CAP_TLS;
	}
	hdr.result = RPC_NEG_OK;

	if (rpc_negotiate_encode(&hdr, wire, sizeof(wire)) < 0)
		return RPC_TRANSPORT_REJECT;
	if (neg_write_all(fd, wire, sizeof(wire)) != 0)
		return RPC_TRANSPORT_REJECT;

	if (neg_read_all(fd, wire, sizeof(wire)) != 0) {
		/* 读响应超时 → 对端不支持协商协议 */
		if (errno == ETIMEDOUT)
			return RPC_NEG_ERR_TIMEOUT;
		return RPC_TRANSPORT_REJECT;
	}
	rpc_negotiate_header_t resp;
	if (rpc_negotiate_decode(&resp, wire, sizeof(wire)) != 0)
		return RPC_TRANSPORT_REJECT;

	if (resp.result != RPC_NEG_OK) {
		/* 服务端拒绝（版本/能力不匹配）→ ENC-004 */
		return RPC_TRANSPORT_REJECT;
	}

	/* 服务端能力位（含 VER_MATCH 与算法位），据此判定本端升级目标 */
	int peer_sm = (resp.capability & RPC_CAP_SM) ? 1 : 0;
	int peer_tls = (resp.capability & RPC_CAP_TLS) ? 1 : 0;
	ret = rpc_decide_transport(tls_enable, sm_ready, tls_ready, peer_sm,
				   peer_tls);
	if (upgrade)
		*upgrade = ret;
	return ret;
}

int rpc_negotiate_server(int fd, int tls_enable, int sm_ready, int tls_ready,
			 int *upgrade)
{
	rpc_negotiate_header_t req;
	uint8_t wire[RPC_NEG_HEADER_LEN];
	rpc_negotiate_header_t resp;
	int ret = RPC_TRANSPORT_REJECT;

	if (upgrade)
		*upgrade = -1;

	/* 等协商头：超时 → 存量明文客户端（未识别协商协议） */
	if (neg_wait_readable(fd, RPC_NEG_TIMEOUT_MS) != 0) {
		if (errno == ETIMEDOUT)
			return RPC_NEG_ERR_TIMEOUT;
		return RPC_NEG_ERR_GENERIC;
	}
	if (neg_read_all(fd, wire, sizeof(wire)) != 0) {
		/* 头读入中途超时（半协商头 + 静默）也归为"存量明文"判定 */
		if (errno == ETIMEDOUT)
			return RPC_NEG_ERR_TIMEOUT;
		return RPC_NEG_ERR_GENERIC;
	}
	if (rpc_negotiate_decode(&req, wire, sizeof(wire)) != 0)
		return RPC_NEG_ERR_VER;

	memset(&resp, 0, sizeof(resp));
	memcpy(resp.magic, RPC_NEG_MAGIC, RPC_NEG_MAGIC_LEN);
	resp.version = RPC_NEG_VERSION;

	if (req.capability & RPC_CAP_ENCRYPT) {
		/* 客户端要求加密：按本端就绪与客户端算法能力判定 */
		int peer_sm = (req.capability & RPC_CAP_SM) ? 1 : 0;
		int peer_tls = (req.capability & RPC_CAP_TLS) ? 1 : 0;
		ret = rpc_decide_transport(tls_enable, sm_ready, tls_ready,
					   peer_sm, peer_tls);
		if (ret == RPC_TRANSPORT_REJECT) {
			resp.result = RPC_NEG_ERR_CAP;
			if (rpc_negotiate_encode(&resp, wire, sizeof(wire)) < 0)
				return RPC_NEG_ERR_GENERIC;
			neg_write_all(fd, wire, sizeof(wire));
			return RPC_TRANSPORT_REJECT;
		}
		resp.result = RPC_NEG_OK;
		resp.capability = RPC_CAP_VER_MATCH;
		if (ret == RPC_TRANSPORT_TLS_SM)
			resp.capability |= RPC_CAP_SM;
		else if (ret == RPC_TRANSPORT_TLS_GENERIC)
			resp.capability |= RPC_CAP_TLS;
	} else {
		/* 客户端开关关闭 → 明文 */
		resp.result = RPC_NEG_OK;
		resp.capability = RPC_CAP_VER_MATCH;
		ret = RPC_TRANSPORT_PLAIN;
	}

	if (rpc_negotiate_encode(&resp, wire, sizeof(wire)) < 0)
		return RPC_NEG_ERR_GENERIC;
	if (neg_write_all(fd, wire, sizeof(wire)) != 0)
		return RPC_NEG_ERR_GENERIC;

	if (upgrade)
		*upgrade = ret;
	return ret;
}
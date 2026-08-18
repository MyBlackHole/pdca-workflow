#ifndef __RPC_NEGOTIATE_H__
#define __RPC_NEGOTIATE_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

/* 协商协议版本 */
#define RPC_NEG_VERSION 1
#define RPC_NEG_MAGIC "AIO-NEG1"
#define RPC_NEG_MAGIC_LEN 8

/* 能力位图（capability） */
#define RPC_CAP_ENCRYPT   0x01 /* bit0: 传输加密开关开启 */
#define RPC_CAP_SM        0x02 /* bit1: 国密套件就绪（TLS_SM） */
#define RPC_CAP_TLS       0x04 /* bit2: 常规套件就绪（AES） */
#define RPC_CAP_VER_MATCH 0x08 /* bit3: 协议版本匹配 */

/* 服务端响应结果码 */
#define RPC_NEG_OK       0x00
#define RPC_NEG_ERR_VER  0x01 /* 版本不匹配 */
#define RPC_NEG_ERR_CAP  0x02 /* 无能力支持 */
#define RPC_NEG_ERR_GENERIC 0x03
#define RPC_NEG_ERR_TIMEOUT 0x04 /* 等待协商头/响应超时（存量明文或无协商端） */

/* 协商头固定长度：8 magic + 1 version + 1 capability + 1 result + 1 reserved */
#define RPC_NEG_HEADER_LEN 12

/* 协商超时（毫秒） */
#define RPC_NEG_TIMEOUT_MS 2000

/* 判定结果 */
#define RPC_TRANSPORT_PLAIN 0     /* 明文 */
#define RPC_TRANSPORT_TLS_SM 1    /* 升级国密 TLS */
#define RPC_TRANSPORT_TLS_GENERIC 2 /* 升级常规 TLS */
#define RPC_TRANSPORT_REJECT (-1) /* ENC-004 拒绝 */

typedef struct rpc_negotiate_header {
	char magic[8];
	uint8_t version;
	uint8_t capability;
	uint8_t result;
	uint8_t reserved;
} rpc_negotiate_header_t;

/* 编码协商头为线格式，返回写入字节数（失败返回 -1） */
int rpc_negotiate_encode(const rpc_negotiate_header_t *hdr, uint8_t *wire,
			 int wire_len);

/* 解码线格式为协商头，校验 magic 与版本，成功返回 0 */
int rpc_negotiate_decode(rpc_negotiate_header_t *hdr, const uint8_t *wire,
			 int wire_len);

/* 判定传输方式（纯逻辑，可单测）：
 *   tls_enable: 本端配置开关（0/1）
 *   sm_ready:   本端国密套件就绪
 *   tls_ready:  本端常规套件就绪
 *   peer_sm:    对端国密能力位
 *   peer_tls:   对端常规能力位
 * 返回 RPC_TRANSPORT_*（REJECT 为 ENC-004） */
int rpc_decide_transport(int tls_enable, int sm_ready, int tls_ready,
			 int peer_sm, int peer_tls);

/* 按算法配置字符串判定本端就绪能力（返回 capability 位图子集），
 * 未配置算法时默认国密（对齐 PRD"默认算法为国密"）。 */
uint8_t rpc_capability_from_ciphersuites(const char *ciphersuites);

/* 客户端协商：发送本端能力请求，接收服务端响应并判定传输方式。
 * 返回 RPC_TRANSPORT_*（PLAIN/TLS_SM/TLS_GENERIC/REJECT）。
 * upgrade 非空时返回升级目标（REJECT 时为 -1）。 */
int rpc_negotiate_client(int fd, int tls_enable, int sm_ready, int tls_ready,
			 int *upgrade);

/* 服务端协商：接收客户端请求，按本端策略判定并回送响应。
 * 返回 RPC_TRANSPORT_*（PLAIN/TLS_SM/TLS_GENERIC/REJECT）。
 * 对端版本不匹配时返回 RPC_NEG_ERR_VER。 */
int rpc_negotiate_server(int fd, int tls_enable, int sm_ready, int tls_ready,
			 int *upgrade);

#ifdef __cplusplus
}
#endif

#endif /* __RPC_NEGOTIATE_H__ */
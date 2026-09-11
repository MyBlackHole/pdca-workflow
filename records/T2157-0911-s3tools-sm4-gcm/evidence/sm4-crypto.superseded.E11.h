// s3tools SM4 加解密封装（openssl4 EVP 实现）。
//
// 说明：历史实现使用 gmssl（sm4_cbc_padding_*，固定 key/iv）。经兼容测试证明
// openssl4 EVP_sm4_cbc（PKCS7）与之密文逐字节一致（见 s3file/s3mount/tests/
// sm4_openssl_compat_test.cpp），故生产路径切换到项目内 openssl4，CBC 沿用
// 旧 key/iv（S3_SM4_KEY/S3_SM4_IV），存量对象无需改写。
// 链接注意：s3file/s3mount 同时链接自带 OpenSSL 1.1 的华为 SDK，openssl4 须
// 静态链接并用 -Wl,--exclude-libs 隐藏符号，避免运行时互相抢占（见 xmake.lua）。
#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 兼容旧数据的固定 key/iv：禁止修改，GCM 复用同一 key，nonce 每对象随机 */
extern const uint8_t S3_SM4_KEY[16];
extern const uint8_t S3_SM4_IV[16];

#define S3_SM4_BLOCK_LEN 16
#define S3_SM4_NONCE_LEN 12
#define S3_SM4_TAG_LEN 16
#define S3_SM4_NONCE_HEX_LEN 24
#define S3_SM4_TAG_HEX_LEN 32

/* SM4-CBC（PKCS7）。out 缓冲至少 inlen+16。成功返回 1，失败返回 0。 */
int s3_sm4_cbc_encrypt(const uint8_t *in, size_t inlen, uint8_t *out,
		       size_t *outlen);
int s3_sm4_cbc_decrypt(const uint8_t *in, size_t inlen, uint8_t *out,
		       size_t *outlen);

/* SM4-GCM（12B nonce，16B tag，无 AAD）。密文长度恒等于明文长度。
 * 成功返回 1，失败/验签不通过返回 0（fail-closed，不输出明文）。 */
int s3_sm4_gcm_encrypt(const uint8_t *nonce, const uint8_t *in, size_t inlen,
		       uint8_t *out, uint8_t tag[S3_SM4_TAG_LEN]);
int s3_sm4_gcm_decrypt(const uint8_t *nonce, const uint8_t *tag,
		       const uint8_t *in, size_t inlen, uint8_t *out);

/* 每对象随机 nonce。成功返回 1，失败返回 0（调用方须 fail-closed）。 */
int s3_sm4_rand_nonce(uint8_t nonce[S3_SM4_NONCE_LEN]);

/* hex 编解码（元数据落盘用，小写）。ok 返回 1。 */
int s3_sm4_hex_encode(const uint8_t *in, size_t inlen, char *out);
int s3_sm4_hex_decode(const char *in, uint8_t *out, size_t outlen);

/* 严格整数解析（元数据可信性）：全数字串才接受，否则返回 0（fail-closed，
 * 调用方不得回落默认值）。 */
int s3_parse_int_strict(const char *s, int *out);
int s3_parse_int64_strict(const char *s, int64_t *out);

/* 流式加解密（分段处理大对象，无需整体进内存；GCM 无 AAD）。
 * 一次性接口均基于本接口实现，分段结果与一次性逐字节一致。
 * 缓冲契约：每次 update 的 out 至少 inlen+16；finish 的 out 至少 16（CBC）
 * 或 0（GCM，密文已在 update 输出完）；nonce 固定 12B，tag 固定 16B。
 * 生命周期：init 成功后必须 finish（成功即释放）或 free（中止释放）恰一次。 */
enum {
	S3_SM4_ALGO_CBC = 0,
	S3_SM4_ALGO_GCM = 1
};

struct S3Sm4StreamCtx {
	void *cipher_impl; /* EVP_CIPHER*（GCM），CBC 为 NULL */
	void *ctx_impl; /* EVP_CIPHER_CTX* */
	int algo; /* S3_SM4_ALGO_* */
	int enc; /* 1=加密，0=解密 */
	int finished; /* 防重入 */
};

/* CBC 用固定 S3_SM4_IV；GCM 用调用方传入的每对象 nonce。
 * 成功返回 1（ctx 可用），失败返回 0（ctx 不可用）。 */
int s3_sm4_stream_init(S3Sm4StreamCtx *ctx, int algo, int enc,
		       const uint8_t *iv_or_nonce);
/* 分段输入输出，*outlen 为本次输出长度。成功 1，失败 0（ctx 须 free 中止）。 */
int s3_sm4_stream_update(S3Sm4StreamCtx *ctx, const uint8_t *in, size_t inlen,
			 uint8_t *out, size_t *outlen);
/* GCM 解密 finish 前必须 set_tag，否则失败。 */
int s3_sm4_stream_set_tag(S3Sm4StreamCtx *ctx,
			  const uint8_t tag[S3_SM4_TAG_LEN]);
/* 收尾并释放（解密验签在此发生，失败返回 0）；成功后 ctx 不可再用。 */
int s3_sm4_stream_finish(S3Sm4StreamCtx *ctx, uint8_t *out, size_t *outlen);
/* GCM 加密专用收尾：Final 之后取 tag，原子完成（tag 不可为 NULL）。 */
int s3_sm4_stream_finish_get_tag(S3Sm4StreamCtx *ctx, uint8_t *out,
				 size_t *outlen, uint8_t tag[S3_SM4_TAG_LEN]);
/* 中止并释放（init 成功但不再 finish 时调用）。 */
void s3_sm4_stream_free(S3Sm4StreamCtx *ctx);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
#include <string>

/* 对象加密元数据画像（HeadObject 解析结果）。
 * 注意：存量快照对象携带 gmssl=0 的错误元数据（旧 PutObject 默认行为），与
 * 新写明文对象的 truthful gmssl=0 不可区分，故 gmssl=0 恒按歧义回落本地模式。
 */
struct S3ObjectMeta {
	int gmssl; /* -1=无 gmssl 键（无元数据）；-2=值非法；0/1/2=元数据值 */
	int64_t orgLen; /* file-size，-1=缺失；GCM 下恒等于密文长度 */
	int64_t contentLen; /* 对象内容长度（密文长度） */
	std::string nonceHex; /* sm4-nonce，缺失为空 */
	std::string tagHex; /* sm4-tag，缺失为空 */
};

/* 按对象元数据自适应解密（fail-closed，成功返回 1）：
 * - meta 2 → GCM（nonce/tag 缺失或非法、长度不符、验签失败均返回 0）；
 * - meta 1 → CBC；
 * - meta 0/缺失 → 歧义回落：localMode=0 则明文拷贝，否则 CBC；
 * - 能力门禁：meta 模式高于 localMode（如 1 读 2）直接返回 0。
 * out 缓冲至少 contentLen+16。localMode 为卷/本次写模式（0/1/2）。 */
int s3_decrypt_object(const S3ObjectMeta &meta, int localMode,
		      const uint8_t *in, size_t inlen, uint8_t *out,
		      size_t *outlen);
#endif

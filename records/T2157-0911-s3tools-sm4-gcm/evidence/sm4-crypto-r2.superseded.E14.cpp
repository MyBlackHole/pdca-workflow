// s3tools SM4 加解密封装实现（openssl4 EVP）。
#include "sm4-crypto.h"

#include <openssl/evp.h>
#include <openssl/rand.h>
#include <limits.h>
#include <string.h>

const uint8_t S3_SM4_KEY[16] = { 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB,
				 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98,
				 0x76, 0x54, 0x32, 0x10 };
const uint8_t S3_SM4_IV[16] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
				0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B,
				0x0C, 0x0D, 0x0E, 0x0F };

int s3_sm4_cbc_encrypt(const uint8_t *in, size_t inlen, uint8_t *out,
		       size_t *outlen)
{
	S3Sm4StreamCtx ctx;
	size_t ulen = 0, flen = 0;

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (inlen > 0 && in == out)
		return 0; /* 不支持原地加解密 */
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_CBC, 1, S3_SM4_IV))
		return 0;
	if (inlen > 0 &&
	    !s3_sm4_stream_update(&ctx, in, inlen, out, &ulen)) {
		s3_sm4_stream_free(&ctx);
		return 0;
	}
	if (!s3_sm4_stream_finish(&ctx, out + ulen, &flen))
		return 0;
	*outlen = ulen + flen;
	return 1;
}

int s3_sm4_cbc_decrypt(const uint8_t *in, size_t inlen, uint8_t *out,
		       size_t *outlen)
{
	S3Sm4StreamCtx ctx;
	size_t ulen = 0, flen = 0;

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (inlen == 0 || inlen % S3_SM4_BLOCK_LEN != 0)
		return 0; /* CBC 密文恒为块整数倍，否则 fail-closed */
	if (in == out)
		return 0; /* 不支持原地加解密 */
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_CBC, 0, S3_SM4_IV))
		return 0;
	if (!s3_sm4_stream_update(&ctx, in, inlen, out, &ulen)) {
		s3_sm4_stream_free(&ctx);
		return 0;
	}
	if (!s3_sm4_stream_finish(&ctx, out + ulen, &flen))
		return 0;
	*outlen = ulen + flen;
	return 1;
}

int s3_sm4_gcm_encrypt(const uint8_t *nonce, const uint8_t *in, size_t inlen,
		       uint8_t *out, uint8_t tag[S3_SM4_TAG_LEN])
{
	S3Sm4StreamCtx ctx;
	size_t ulen = 0, flen = 0;

	if (nonce == NULL || tag == NULL)
		return 0;
	if (inlen > 0 && (in == NULL || out == NULL))
		return 0;
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_GCM, 1, nonce))
		return 0;
	if (inlen > 0 && !s3_sm4_stream_update(&ctx, in, inlen, out, &ulen)) {
		s3_sm4_stream_free(&ctx);
		return 0;
	}
	if (!s3_sm4_stream_finish_get_tag(&ctx, out + ulen, &flen, tag))
		return 0;
	return 1;
}

int s3_sm4_gcm_decrypt(const uint8_t *nonce, const uint8_t *tag,
		       const uint8_t *in, size_t inlen, uint8_t *out)
{
	S3Sm4StreamCtx ctx;
	size_t ulen = 0, flen = 0;

	if (nonce == NULL || tag == NULL)
		return 0;
	if (inlen > 0 && (in == NULL || out == NULL))
		return 0;
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_GCM, 0, nonce))
		return 0;
	if (!s3_sm4_stream_set_tag(&ctx, tag)) {
		s3_sm4_stream_free(&ctx);
		return 0;
	}
	if (inlen > 0 && !s3_sm4_stream_update(&ctx, in, inlen, out, &ulen)) {
		s3_sm4_stream_free(&ctx);
		return 0;
	}
	/* 验签不通过即 fail-closed：返回 0，调用方不得使用 out */
	if (!s3_sm4_stream_finish(&ctx, out + ulen, &flen))
		return 0;
	return 1;
}

int s3_sm4_stream_init(S3Sm4StreamCtx *ctx, int algo, int enc,
		       const uint8_t *iv_or_nonce)
{
	EVP_CIPHER_CTX *c = NULL;
	EVP_CIPHER *fetched = NULL;
	int rc;

	if (ctx == NULL || iv_or_nonce == NULL)
		return 0;
	if ((algo != S3_SM4_ALGO_CBC && algo != S3_SM4_ALGO_GCM) ||
	    (enc != 0 && enc != 1))
		return 0;
	ctx->cipher_impl = NULL;
	ctx->ctx_impl = NULL;
	ctx->algo = algo;
	ctx->enc = enc;
	ctx->finished = 0;
	c = EVP_CIPHER_CTX_new();
	if (c == NULL)
		return 0;
	ctx->ctx_impl = c;
	if (algo == S3_SM4_ALGO_CBC) {
		/* CBC 用调用方传入 IV（一次性封装传固定 S3_SM4_IV 以兼容旧数据） */
		rc = enc ? EVP_EncryptInit_ex(c, EVP_sm4_cbc(), NULL,
					      S3_SM4_KEY, iv_or_nonce) :
			   EVP_DecryptInit_ex(c, EVP_sm4_cbc(), NULL,
					      S3_SM4_KEY, iv_or_nonce);
		if (1 != rc) {
			s3_sm4_stream_free(ctx);
			return 0;
		}
		return 1;
	}
	/* GCM：按方向初始化，IV 固定 12B nonce */
	fetched = EVP_CIPHER_fetch(NULL, "SM4-GCM", NULL);
	if (fetched == NULL) {
		s3_sm4_stream_free(ctx);
		return 0;
	}
	ctx->cipher_impl = fetched;
	if (enc)
		rc = EVP_EncryptInit_ex(c, fetched, NULL, NULL, NULL);
	else
		rc = EVP_DecryptInit_ex(c, fetched, NULL, NULL, NULL);
	if (1 != rc ||
	    1 != EVP_CIPHER_CTX_ctrl(c, EVP_CTRL_GCM_SET_IVLEN,
				     S3_SM4_NONCE_LEN, NULL)) {
		s3_sm4_stream_free(ctx);
		return 0;
	}
	if (enc)
		rc = EVP_EncryptInit_ex(c, NULL, NULL, S3_SM4_KEY,
					iv_or_nonce);
	else
		rc = EVP_DecryptInit_ex(c, NULL, NULL, S3_SM4_KEY,
					iv_or_nonce);
	if (1 != rc) {
		s3_sm4_stream_free(ctx);
		return 0;
	}
	return 1;
}

int s3_sm4_stream_update(S3Sm4StreamCtx *ctx, const uint8_t *in, size_t inlen,
			 uint8_t *out, size_t *outlen)
{
	EVP_CIPHER_CTX *c;
	int outl = 0;

	if (ctx == NULL || ctx->ctx_impl == NULL || out == NULL ||
	    outlen == NULL)
		return 0;
	if (ctx->finished)
		return 0;
	if (inlen > (size_t)INT_MAX)
		return 0; /* EVP 接口 int 长度上限，超限 fail-closed */
	if (inlen > 0 && (in == NULL || in == out))
		return 0; /* 不支持原地加解密 */
	if (inlen == 0) {
		*outlen = 0;
		return 1;
	}
	c = (EVP_CIPHER_CTX *)ctx->ctx_impl;
	if (ctx->enc) {
		if (1 != EVP_EncryptUpdate(c, out, &outl, in, (int)inlen))
			return 0;
	} else {
		if (1 != EVP_DecryptUpdate(c, out, &outl, in, (int)inlen))
			return 0;
	}
	*outlen = (size_t)outl;
	return 1;
}

int s3_sm4_stream_set_tag(S3Sm4StreamCtx *ctx,
			  const uint8_t tag[S3_SM4_TAG_LEN])
{
	EVP_CIPHER_CTX *c;

	if (ctx == NULL || ctx->ctx_impl == NULL || tag == NULL)
		return 0;
	if (ctx->finished || ctx->algo != S3_SM4_ALGO_GCM || ctx->enc)
		return 0;
	c = (EVP_CIPHER_CTX *)ctx->ctx_impl;
	return 1 == EVP_CIPHER_CTX_ctrl(c, EVP_CTRL_GCM_SET_TAG,
					S3_SM4_TAG_LEN, (void *)tag) ?
	       1 :
	       0;
}

int s3_sm4_stream_finish(S3Sm4StreamCtx *ctx, uint8_t *out, size_t *outlen)
{
	EVP_CIPHER_CTX *c;
	int tmpl = 0;
	int ok;

	if (ctx == NULL || ctx->ctx_impl == NULL || out == NULL ||
	    outlen == NULL)
		return 0;
	if (ctx->finished)
		return 0;
	ctx->finished = 1;
	c = (EVP_CIPHER_CTX *)ctx->ctx_impl;
	if (ctx->enc)
		ok = (1 == EVP_EncryptFinal_ex(c, out, &tmpl));
	else
		ok = (1 == EVP_DecryptFinal_ex(c, out, &tmpl));
	s3_sm4_stream_free(ctx);
	if (!ok)
		return 0;
	*outlen = (size_t)tmpl;
	return 1;
}

int s3_sm4_stream_finish_get_tag(S3Sm4StreamCtx *ctx, uint8_t *out,
				 size_t *outlen, uint8_t tag[S3_SM4_TAG_LEN])
{
	EVP_CIPHER_CTX *c;
	int tmpl = 0;

	if (ctx == NULL || ctx->ctx_impl == NULL || out == NULL ||
	    outlen == NULL || tag == NULL)
		return 0;
	if (ctx->finished || ctx->algo != S3_SM4_ALGO_GCM || !ctx->enc)
		return 0;
	ctx->finished = 1;
	c = (EVP_CIPHER_CTX *)ctx->ctx_impl;
	if (1 != EVP_EncryptFinal_ex(c, out, &tmpl) ||
	    1 != EVP_CIPHER_CTX_ctrl(c, EVP_CTRL_GCM_GET_TAG, S3_SM4_TAG_LEN,
				     tag)) {
		s3_sm4_stream_free(ctx);
		return 0;
	}
	s3_sm4_stream_free(ctx);
	*outlen = (size_t)tmpl;
	return 1;
}

void s3_sm4_stream_free(S3Sm4StreamCtx *ctx)
{
	if (ctx == NULL)
		return;
	if (ctx->cipher_impl != NULL) {
		EVP_CIPHER_free((EVP_CIPHER *)ctx->cipher_impl);
		ctx->cipher_impl = NULL;
	}
	if (ctx->ctx_impl != NULL) {
		EVP_CIPHER_CTX_free((EVP_CIPHER_CTX *)ctx->ctx_impl);
		ctx->ctx_impl = NULL;
	}
	ctx->finished = 1;
}

int s3_sm4_rand_nonce(uint8_t nonce[S3_SM4_NONCE_LEN])
{
	if (nonce == NULL)
		return 0;
	return RAND_bytes(nonce, S3_SM4_NONCE_LEN) == 1 ? 1 : 0;
}

int s3_sm4_hex_encode(const uint8_t *in, size_t inlen, char *out)
{
	static const char digits[] = "0123456789abcdef";
	size_t i;

	if (in == NULL || out == NULL)
		return 0;
	for (i = 0; i < inlen; i++) {
		out[i * 2] = digits[(in[i] >> 4) & 0xF];
		out[i * 2 + 1] = digits[in[i] & 0xF];
	}
	out[inlen * 2] = '\0';
	return 1;
}

static int hex_val(char c)
{
	if (c >= '0' && c <= '9')
		return c - '0';
	if (c >= 'a' && c <= 'f')
		return c - 'a' + 10;
	if (c >= 'A' && c <= 'F')
		return c - 'A' + 10;
	return -1;
}

int s3_sm4_hex_decode(const char *in, uint8_t *out, size_t outlen)
{
	size_t i;
	int hi, lo;

	if (in == NULL || out == NULL)
		return 0;
	if (strlen(in) != outlen * 2)
		return 0;
	for (i = 0; i < outlen; i++) {
		hi = hex_val(in[i * 2]);
		lo = hex_val(in[i * 2 + 1]);
		if (hi < 0 || lo < 0)
			return 0;
		out[i] = (uint8_t)((hi << 4) | lo);
	}
	return 1;
}

int s3_parse_int_strict(const char *s, int *out)
{
	int64_t v;

	if (out == NULL || !s3_parse_int64_strict(s, &v) || v > INT_MAX)
		return 0;
	*out = (int)v;
	return 1;
}

int s3_parse_int64_strict(const char *s, int64_t *out)
{
	int64_t v = 0;
	size_t i;

	if (s == NULL || out == NULL || s[0] == '\0')
		return 0;
	for (i = 0; s[i] != '\0'; i++) {
		int d;
		if (s[i] < '0' || s[i] > '9')
			return 0;
		d = s[i] - '0';
		if (v > (INT64_MAX - d) / 10)
			return 0; /* 先判后乘，避免有符号溢出 UB */
		v = v * 10 + d;
	}
	*out = v;
	return 1;
}

int s3_decrypt_object(const S3ObjectMeta &meta, int localMode,
		      const uint8_t *in, size_t inlen, uint8_t *out,
		      size_t *outlen)
{
	uint8_t nonce[S3_SM4_NONCE_LEN];
	uint8_t tag[S3_SM4_TAG_LEN];

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	/* 非法元数据值（如 gmssl 非数字）直接拒绝，不回落（fail-closed） */
	if (meta.gmssl < -1)
		return 0;
	/* 能力门禁：对象模式高于本卷能力（如 CBC 卷读到 GCM 对象）必须明确报错，
	 * 不得按低模式误解密（升级顺序门禁 R3） */
	if (meta.gmssl > localMode && meta.gmssl >= 0)
		return 0;
	if (meta.gmssl == 2) {
		if (meta.nonceHex.size() != S3_SM4_NONCE_HEX_LEN ||
		    meta.tagHex.size() != S3_SM4_TAG_HEX_LEN)
			return 0;
		if (meta.orgLen >= 0 && inlen != (size_t)meta.orgLen)
			return 0; /* GCM 密文长度恒等于原文长度 */
		if (!s3_sm4_hex_decode(meta.nonceHex.c_str(), nonce,
				       sizeof(nonce)) ||
		    !s3_sm4_hex_decode(meta.tagHex.c_str(), tag, sizeof(tag)))
			return 0;
		/* GCM 密文长度恒等于明文长度，解密成功即回填 */
		if (!s3_sm4_gcm_decrypt(nonce, tag, in, inlen, out))
			return 0;
		*outlen = inlen;
		return 1;
	}
	if (meta.gmssl == 1)
		return s3_sm4_cbc_decrypt(in, inlen, out, outlen);
	/* gmssl=0/缺失：歧义回落本地模式（存量快照 CBC 对象亦标 0，不可区分） */
	if (localMode == 0) {
		if (meta.orgLen >= 0 && inlen != (size_t)meta.orgLen)
			return 0;
		memmove(out, in, inlen);
		*outlen = inlen;
		return 1;
	}
	return s3_sm4_cbc_decrypt(in, inlen, out, outlen);
}

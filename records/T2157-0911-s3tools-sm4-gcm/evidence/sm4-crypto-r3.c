// s3tools SM4 加解密封装实现（openssl4 EVP，纯 C）。
#include "sm4-crypto.h"

#include <openssl/evp.h>
#include <openssl/rand.h>
#include <limits.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>

const uint8_t S3_SM4_DEFAULT_KEY[16] = { 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB,
					 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98,
					 0x76, 0x54, 0x32, 0x10 };
const uint8_t S3_SM4_DEFAULT_IV[16] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
					0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B,
					0x0C, 0x0D, 0x0E, 0x0F };

/* 运行期 key/iv：首次访问懒装默认旧值；设置与读取互斥。常驻进程生命期。 */
static uint8_t g_sm4_key[16];
static uint8_t g_sm4_iv[16];
static int g_sm4_key_ready = 0;
static pthread_mutex_t g_sm4_key_lock = PTHREAD_MUTEX_INITIALIZER;

int s3_sm4_set_key_iv_hex(const char *keyHex, const char *ivHex)
{
	uint8_t key[16];
	uint8_t iv[16];

	if (keyHex == NULL || keyHex[0] == '\0') {
		memcpy(key, S3_SM4_DEFAULT_KEY, sizeof(key));
	} else if (!s3_sm4_hex_decode(keyHex, key, sizeof(key))) {
		return 0;
	}
	if (ivHex == NULL || ivHex[0] == '\0') {
		memcpy(iv, S3_SM4_DEFAULT_IV, sizeof(iv));
	} else if (!s3_sm4_hex_decode(ivHex, iv, sizeof(iv))) {
		return 0;
	}
	pthread_mutex_lock(&g_sm4_key_lock);
	memcpy(g_sm4_key, key, sizeof(g_sm4_key));
	memcpy(g_sm4_iv, iv, sizeof(g_sm4_iv));
	g_sm4_key_ready = 1;
	pthread_mutex_unlock(&g_sm4_key_lock);
	return 1;
}

void s3_sm4_get_key_iv(uint8_t key[16], uint8_t iv[16])
{
	pthread_mutex_lock(&g_sm4_key_lock);
	if (!g_sm4_key_ready) {
		memcpy(g_sm4_key, S3_SM4_DEFAULT_KEY, sizeof(g_sm4_key));
		memcpy(g_sm4_iv, S3_SM4_DEFAULT_IV, sizeof(g_sm4_iv));
		g_sm4_key_ready = 1;
	}
	if (key != NULL)
		memcpy(key, g_sm4_key, sizeof(g_sm4_key));
	if (iv != NULL)
		memcpy(iv, g_sm4_iv, sizeof(g_sm4_iv));
	pthread_mutex_unlock(&g_sm4_key_lock);
}

/* GCM provider cipher 进程单例：EVP_CIPHER_fetch 线程安全但抢全局锁，
 * 高并发下每次 fetch 开销显著；单例后各线程共享只读 cipher。常驻不释放。 */
static EVP_CIPHER *g_gcm_cipher = NULL;
static pthread_once_t g_gcm_once = PTHREAD_ONCE_INIT;

static void fetch_gcm_once(void)
{
	g_gcm_cipher = EVP_CIPHER_fetch(NULL, "SM4-GCM", NULL);
}

static EVP_CIPHER *s3_gcm_cipher(void)
{
	pthread_once(&g_gcm_once, fetch_gcm_once);
	return g_gcm_cipher;
}

/* ---- 一次性接口（基于流式实现，分段结果逐字节一致） ---- */

int s3_sm4_cbc_encrypt(const uint8_t *in, size_t inlen, uint8_t *out,
		       size_t *outlen)
{
	S3Sm4StreamCtx ctx;
	int inited = 0;
	uint8_t iv[16];
	size_t ulen = 0, flen = 0;

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (inlen > 0 && in == out)
		return 0; /* 不支持原地加解密 */
	s3_sm4_get_key_iv(NULL, iv);
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_CBC, 1, iv))
		return 0;
	inited = 1;
	if (inlen > 0 && !s3_sm4_stream_update(&ctx, in, inlen, out, &ulen))
		goto fail;
	if (!s3_sm4_stream_finish(&ctx, out + ulen, &flen))
		goto fail;
	*outlen = ulen + flen;
	return 1;
fail:
	if (inited)
		s3_sm4_stream_free(&ctx);
	return 0;
}

int s3_sm4_cbc_decrypt(const uint8_t *in, size_t inlen, uint8_t *out,
		       size_t *outlen)
{
	S3Sm4StreamCtx ctx;
	int inited = 0;
	uint8_t iv[16];
	size_t ulen = 0, flen = 0;

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (inlen == 0 || inlen % S3_SM4_BLOCK_LEN != 0)
		return 0; /* CBC 密文恒为块整数倍，否则 fail-closed */
	if (in == out)
		return 0; /* 不支持原地加解密 */
	s3_sm4_get_key_iv(NULL, iv);
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_CBC, 0, iv))
		return 0;
	inited = 1;
	if (!s3_sm4_stream_update(&ctx, in, inlen, out, &ulen))
		goto fail;
	if (!s3_sm4_stream_finish(&ctx, out + ulen, &flen))
		goto fail;
	*outlen = ulen + flen;
	return 1;
fail:
	if (inited)
		s3_sm4_stream_free(&ctx);
	return 0;
}

int s3_sm4_gcm_encrypt(const uint8_t *nonce, const uint8_t *in, size_t inlen,
		       uint8_t *out, uint8_t tag[S3_SM4_TAG_LEN])
{
	S3Sm4StreamCtx ctx;
	int inited = 0;
	size_t ulen = 0, flen = 0;

	if (nonce == NULL || tag == NULL)
		return 0;
	if (inlen > 0 && (in == NULL || out == NULL))
		return 0;
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_GCM, 1, nonce))
		return 0;
	inited = 1;
	if (inlen > 0 && !s3_sm4_stream_update(&ctx, in, inlen, out, &ulen))
		goto fail;
	if (!s3_sm4_stream_finish_get_tag(&ctx, out + ulen, &flen, tag))
		goto fail;
	return 1;
fail:
	if (inited)
		s3_sm4_stream_free(&ctx);
	return 0;
}

int s3_sm4_gcm_decrypt(const uint8_t *nonce, const uint8_t *tag,
		       const uint8_t *in, size_t inlen, uint8_t *out)
{
	S3Sm4StreamCtx ctx;
	int inited = 0;
	size_t ulen = 0, flen = 0;

	if (nonce == NULL || tag == NULL)
		return 0;
	if (inlen > 0 && (in == NULL || out == NULL))
		return 0;
	if (!s3_sm4_stream_init(&ctx, S3_SM4_ALGO_GCM, 0, nonce))
		return 0;
	inited = 1;
	if (!s3_sm4_stream_set_tag(&ctx, tag))
		goto fail;
	if (inlen > 0 && !s3_sm4_stream_update(&ctx, in, inlen, out, &ulen))
		goto fail;
	/* 验签不通过即 fail-closed：返回 0，调用方不得使用 out */
	if (!s3_sm4_stream_finish(&ctx, out + ulen, &flen))
		goto fail;
	return 1;
fail:
	if (inited)
		s3_sm4_stream_free(&ctx);
	return 0;
}

/* ---- 流式接口 ---- */

int s3_sm4_stream_init(S3Sm4StreamCtx *ctx, int algo, int enc,
		       const uint8_t *iv_or_nonce)
{
	EVP_CIPHER_CTX *c = NULL;
	EVP_CIPHER *fetched = NULL;
	uint8_t key[16];
	int rc;

	if (ctx == NULL || iv_or_nonce == NULL)
		return 0;
	if ((algo != S3_SM4_ALGO_CBC && algo != S3_SM4_ALGO_GCM) ||
	    (enc != 0 && enc != 1))
		return 0;
	ctx->ctx_impl = NULL;
	ctx->algo = algo;
	ctx->enc = enc;
	ctx->finished = 0;
	s3_sm4_get_key_iv(key, NULL);
	c = EVP_CIPHER_CTX_new();
	if (c == NULL)
		return 0;
	ctx->ctx_impl = c;
	if (algo == S3_SM4_ALGO_CBC) {
		/* CBC 用调用方传入 IV（一次性封装传运行期 IV） */
		rc = enc ? EVP_EncryptInit_ex(c, EVP_sm4_cbc(), NULL, key,
					      iv_or_nonce) :
			   EVP_DecryptInit_ex(c, EVP_sm4_cbc(), NULL, key,
					      iv_or_nonce);
		if (1 != rc) {
			s3_sm4_stream_free(ctx);
			return 0;
		}
		return 1;
	}
	/* GCM：按方向初始化，IV 固定 12B nonce */
	fetched = s3_gcm_cipher();
	if (fetched == NULL) {
		s3_sm4_stream_free(ctx);
		return 0;
	}
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
		rc = EVP_EncryptInit_ex(c, NULL, NULL, key, iv_or_nonce);
	else
		rc = EVP_DecryptInit_ex(c, NULL, NULL, key, iv_or_nonce);
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
	if (1 != EVP_CIPHER_CTX_ctrl(c, EVP_CTRL_GCM_SET_TAG, S3_SM4_TAG_LEN,
				    (void *)tag))
		return 0;
	return 1;
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

void s3_meta_init(S3ObjectMeta *meta)
{
	if (meta == NULL)
		return;
	meta->gmssl = -1;
	meta->orgLen = -1;
	meta->contentLen = 0;
	meta->nonceHex[0] = '\0';
	meta->tagHex[0] = '\0';
}

int s3_meta_fill(S3ObjectMeta *meta, const char *gmssl, const char *orgLen,
		 const char *nonceHex, const char *tagHex, int64_t contentLen)
{
	int gv = -1;
	int64_t ov = -1;

	if (meta == NULL)
		return 0;
	if (gmssl != NULL && !s3_parse_int_strict(gmssl, &gv))
		gv = -2; /* 非法值，读端 fail-closed */
	if (orgLen != NULL)
		s3_parse_int64_strict(orgLen, &ov);
	meta->gmssl = gv;
	meta->orgLen = ov;
	meta->contentLen = contentLen;
	meta->nonceHex[0] = '\0';
	meta->tagHex[0] = '\0';
	if (nonceHex != NULL && strlen(nonceHex) < sizeof(meta->nonceHex))
		snprintf(meta->nonceHex, sizeof(meta->nonceHex), "%s",
			 nonceHex);
	if (tagHex != NULL && strlen(tagHex) < sizeof(meta->tagHex))
		snprintf(meta->tagHex, sizeof(meta->tagHex), "%s", tagHex);
	return 1;
}

/* ---- Strategy 各模式实现 ---- */

static int sm4_plain_decrypt(const Sm4Mode *mode, const uint8_t *in,
			     size_t inlen, uint8_t *out, size_t *outlen)
{
	if (mode == NULL || in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (mode->orgLen >= 0 && inlen != (size_t)mode->orgLen)
		return 0;
	memmove(out, in, inlen);
	*outlen = inlen;
	return 1;
}

static int sm4_cbc_decrypt_fn(const Sm4Mode *mode, const uint8_t *in,
			      size_t inlen, uint8_t *out, size_t *outlen)
{
	size_t olen = 0;
	(void)mode;
	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (!s3_sm4_cbc_decrypt(in, inlen, out, &olen))
		return 0;
	*outlen = olen;
	return 1;
}

static int sm4_gcm_decrypt_fn(const Sm4Mode *mode, const uint8_t *in,
			      size_t inlen, uint8_t *out, size_t *outlen)
{
	if (mode == NULL || in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (mode->orgLen >= 0 && inlen != (size_t)mode->orgLen)
		return 0; /* GCM 密文长度恒等于原文长度 */
	/* GCM 密文长度恒等于明文长度，解密成功即回填 */
	if (!s3_sm4_gcm_decrypt(mode->nonce, mode->tag, in, inlen, out))
		return 0;
	*outlen = inlen;
	return 1;
}

int s3_select_mode(const S3ObjectMeta *meta, int localMode, Sm4Mode *mode)
{
	if (meta == NULL || mode == NULL)
		return 0;
	/* 非法元数据值（如 gmssl 非数字）直接拒绝，不回落（fail-closed） */
	if (meta->gmssl < -1)
		return 0;
	/* 能力门禁：对象模式高于本卷能力（如 CBC 卷读到 GCM 对象）必须明确报错，
	 * 不得按低模式误解密（升级顺序门禁 R3） */
	if (meta->gmssl > localMode && meta->gmssl >= 0)
		return 0;
	if (meta->gmssl == 2) {
		if (strlen(meta->nonceHex) != S3_SM4_NONCE_HEX_LEN ||
		    strlen(meta->tagHex) != S3_SM4_TAG_HEX_LEN)
			return 0;
		if (!s3_sm4_hex_decode(meta->nonceHex, mode->nonce,
				       sizeof(mode->nonce)) ||
		    !s3_sm4_hex_decode(meta->tagHex, mode->tag,
				       sizeof(mode->tag)))
			return 0;
		mode->name = "sm4-gcm";
		mode->decrypt = sm4_gcm_decrypt_fn;
		mode->orgLen = meta->orgLen;
		return 1;
	}
	if (meta->gmssl == 1) {
		mode->name = "sm4-cbc";
		mode->decrypt = sm4_cbc_decrypt_fn;
		mode->orgLen = meta->orgLen;
		return 1;
	}
	/* gmssl=0/缺失：歧义回落本地模式（存量快照 CBC 对象亦标 0，不可区分） */
	if (localMode == 0) {
		mode->name = "plain";
		mode->decrypt = sm4_plain_decrypt;
		mode->orgLen = meta->orgLen;
		return 1;
	}
	mode->name = "sm4-cbc";
	mode->decrypt = sm4_cbc_decrypt_fn;
	mode->orgLen = meta->orgLen;
	return 1;
}

int s3_decrypt_object(const S3ObjectMeta *meta, int localMode,
		      const uint8_t *in, size_t inlen, uint8_t *out,
		      size_t *outlen)
{
	Sm4Mode mode;
	size_t olen = 0;

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	memset(&mode, 0, sizeof(mode));
	if (!s3_select_mode(meta, localMode, &mode))
		return 0;
	if (mode.decrypt == NULL)
		return 0;
	if (!mode.decrypt(&mode, in, inlen, out, &olen))
		return 0;
	*outlen = olen;
	return 1;
}

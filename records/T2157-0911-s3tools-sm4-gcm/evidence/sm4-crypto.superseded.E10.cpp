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
	EVP_CIPHER_CTX *ctx = NULL;
	int outl = 0, tmpl = 0;
	size_t total = 0;
	int ok = 0;

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	ctx = EVP_CIPHER_CTX_new();
	if (ctx == NULL)
		return 0;
	if (inlen > 0 && in == out)
		goto end; /* 不支持原地加解密 */
	if (1 != EVP_EncryptInit_ex(ctx, EVP_sm4_cbc(), NULL, S3_SM4_KEY,
				    S3_SM4_IV))
		goto end;
	if (inlen > 0 &&
	    1 != EVP_EncryptUpdate(ctx, out, &outl, in, (int)inlen))
		goto end;
	total = (size_t)outl;
	if (1 != EVP_EncryptFinal_ex(ctx, out + total, &tmpl))
		goto end;
	total += (size_t)tmpl;
	*outlen = total;
	ok = 1;
end:
	EVP_CIPHER_CTX_free(ctx);
	return ok;
}

int s3_sm4_cbc_decrypt(const uint8_t *in, size_t inlen, uint8_t *out,
		       size_t *outlen)
{
	EVP_CIPHER_CTX *ctx = NULL;
	int outl = 0, tmpl = 0;
	size_t total = 0;
	int ok = 0;

	if (in == NULL || out == NULL || outlen == NULL)
		return 0;
	if (inlen == 0 || inlen % S3_SM4_BLOCK_LEN != 0)
		return 0; /* CBC 密文恒为块整数倍，否则 fail-closed */
	ctx = EVP_CIPHER_CTX_new();
	if (ctx == NULL)
		return 0;
	if (in == out)
		goto end; /* 不支持原地加解密 */
	if (1 != EVP_DecryptInit_ex(ctx, EVP_sm4_cbc(), NULL, S3_SM4_KEY,
				    S3_SM4_IV))
		goto end;
	if (1 != EVP_DecryptUpdate(ctx, out, &outl, in, (int)inlen))
		goto end;
	total = (size_t)outl;
	if (1 != EVP_DecryptFinal_ex(ctx, out + total, &tmpl))
		goto end;
	total += (size_t)tmpl;
	*outlen = total;
	ok = 1;
end:
	EVP_CIPHER_CTX_free(ctx);
	return ok;
}

int s3_sm4_gcm_encrypt(const uint8_t *nonce, const uint8_t *in, size_t inlen,
		       uint8_t *out, uint8_t tag[S3_SM4_TAG_LEN])
{
	EVP_CIPHER_CTX *ctx = NULL;
	EVP_CIPHER *cipher = NULL;
	int outl = 0, tmpl = 0;
	int ok = 0;

	if (nonce == NULL || tag == NULL)
		return 0;
	if (inlen > 0 && (in == NULL || out == NULL))
		return 0;
	ctx = EVP_CIPHER_CTX_new();
	if (ctx == NULL)
		return 0;
	cipher = EVP_CIPHER_fetch(NULL, "SM4-GCM", NULL);
	if (cipher == NULL)
		goto end;
	if (1 != EVP_EncryptInit_ex(ctx, cipher, NULL, NULL, NULL))
		goto end;
	if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN,
				     S3_SM4_NONCE_LEN, NULL))
		goto end;
	if (1 != EVP_EncryptInit_ex(ctx, NULL, NULL, S3_SM4_KEY, nonce))
		goto end;
	if (inlen > 0 &&
	    1 != EVP_EncryptUpdate(ctx, out, &outl, in, (int)inlen))
		goto end;
	if (1 != EVP_EncryptFinal_ex(ctx, out + outl, &tmpl))
		goto end;
	if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG,
				     S3_SM4_TAG_LEN, tag))
		goto end;
	ok = 1;
end:
	if (cipher != NULL)
		EVP_CIPHER_free(cipher);
	EVP_CIPHER_CTX_free(ctx);
	return ok;
}

int s3_sm4_gcm_decrypt(const uint8_t *nonce, const uint8_t *tag,
		       const uint8_t *in, size_t inlen, uint8_t *out)
{
	EVP_CIPHER_CTX *ctx = NULL;
	EVP_CIPHER *cipher = NULL;
	int outl = 0, tmpl = 0;
	int ok = 0;

	if (nonce == NULL || tag == NULL)
		return 0;
	if (inlen > 0 && (in == NULL || out == NULL))
		return 0;
	ctx = EVP_CIPHER_CTX_new();
	if (ctx == NULL)
		return 0;
	cipher = EVP_CIPHER_fetch(NULL, "SM4-GCM", NULL);
	if (cipher == NULL)
		goto end;
	if (1 != EVP_DecryptInit_ex(ctx, cipher, NULL, NULL, NULL))
		goto end;
	if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN,
				     S3_SM4_NONCE_LEN, NULL))
		goto end;
	if (1 != EVP_DecryptInit_ex(ctx, NULL, NULL, S3_SM4_KEY, nonce))
		goto end;
	if (inlen > 0 &&
	    1 != EVP_DecryptUpdate(ctx, out, &outl, in, (int)inlen))
		goto end;
	if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG,
				     S3_SM4_TAG_LEN, (void *)tag))
		goto end;
	/* 验签不通过即 fail-closed：返回 0，调用方不得使用 out */
	if (1 != EVP_DecryptFinal_ex(ctx, out + outl, &tmpl))
		goto end;
	ok = 1;
end:
	if (cipher != NULL)
		EVP_CIPHER_free(cipher);
	EVP_CIPHER_CTX_free(ctx);
	return ok;
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
	long v;

	if (!s3_parse_int64_strict(s, &v) || v > INT_MAX)
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
		if (s[i] < '0' || s[i] > '9')
			return 0;
		v = v * 10 + (s[i] - '0');
		if (v > (int64_t)0x7FFFFFFFFFFFFFFFLL / 10)
			return 0;
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

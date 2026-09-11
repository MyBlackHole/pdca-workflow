// s3file SM4 兼容测试：gmssl 加密 → openssl4 解密
//
// 目的：证明现网 s3file 按 `--gmssl` 写入的 SM4-CBC 密文，可用项目内
// openssl4（third_party/openssl4，EVP_sm4_cbc）直接解密正确，即 gmssl
// 可替换为 openssl4，存量对象无需重写。
//
// 对应生产路径：s3tools/s3file/main.cpp upload_snapshot_bundle_to_s3
//   key/iv 与生产完全一致（固定 key/iv，见下 S3SM4_KEY/S3SM4_IV）
//   写：sm4_set_encrypt_key + sm4_cbc_padding_encrypt（main.cpp:1156,1172）
//   读：sm4_set_decrypt_key + sm4_cbc_padding_decrypt（main.cpp:955,971）
// 本测试用 gmssl 模拟“已落盘的存量密文”，用 openssl4 解密并断言明文一致，
// 同时断言双方加密输出逐字节一致（可替换性的充分条件）。

#include "gmssl/sm4.h"
#include <openssl/evp.h>
#include <openssl/provider.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

static int failures = 0;
#define CHECK(cond, msg)                           \
	do {                                       \
		if (!(cond)) {                     \
			printf("FAIL: %s\n", msg); \
			failures++;                \
		} else {                           \
			printf("ok:   %s\n", msg); \
		}                                  \
	} while (0)

/* 与 s3file/main.cpp、s3mount/fuse-file.cpp 完全一致的固定 key/iv */
static const uint8_t S3SM4_KEY[16] = { 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB,
				       0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98,
				       0x76, 0x54, 0x32, 0x10 };
static const uint8_t S3SM4_IV[16] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
				      0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B,
				      0x0C, 0x0D, 0x0E, 0x0F };

/* gmssl 侧：模拟现网写路径 */
static int gmssl_encrypt(const uint8_t *in, size_t inlen, uint8_t *out,
			 size_t *outlen)
{
	SM4_KEY k;
	sm4_set_encrypt_key(&k, S3SM4_KEY);
	return sm4_cbc_padding_encrypt(&k, S3SM4_IV, in, inlen, out, outlen);
}

/* openssl4 侧：待切换的目标读路径（EVP SM4-CBC，PKCS7 padding 默认开启） */
static int ossl4_encrypt(const uint8_t *in, size_t inlen, uint8_t *out,
			 size_t *outlen)
{
	EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
	int outl = 0, tmpl = 0;
	size_t total = 0;
	int ok = 0;
	if (!ctx)
		return 0;
	if (1 !=
	    EVP_EncryptInit_ex(ctx, EVP_sm4_cbc(), NULL, S3SM4_KEY, S3SM4_IV))
		goto end;
	if (1 != EVP_EncryptUpdate(ctx, out, &outl, in, (int)inlen))
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

/* openssl4 侧：核心被测能力——直接解密 gmssl 产出的密文 */
static int ossl4_decrypt(const uint8_t *in, size_t inlen, uint8_t *out,
			 size_t *outlen)
{
	EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
	int outl = 0, tmpl = 0;
	size_t total = 0;
	int ok = 0;
	if (!ctx)
		return 0;
	if (1 !=
	    EVP_DecryptInit_ex(ctx, EVP_sm4_cbc(), NULL, S3SM4_KEY, S3SM4_IV))
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

static int gmssl_decrypt(const uint8_t *in, size_t inlen, uint8_t *out,
			 size_t *outlen)
{
	SM4_KEY k;
	sm4_set_decrypt_key(&k, S3SM4_KEY);
	return sm4_cbc_padding_decrypt(&k, S3SM4_IV, in, inlen, out, outlen);
}

static int test_one_len(size_t len)
{
	uint8_t *plain = (uint8_t *)malloc(len + 1);
	uint8_t *g_ct = (uint8_t *)malloc(len + 32);
	uint8_t *o_ct = (uint8_t *)malloc(len + 32);
	uint8_t *o_pt = (uint8_t *)malloc(len + 32);
	uint8_t *g_pt = (uint8_t *)malloc(len + 32);
	size_t g_ctlen = 0, o_ctlen = 0, o_ptlen = 0, g_ptlen = 0;
	char msg[128];
	int pass = 1;

	if (!plain || !g_ct || !o_ct || !o_pt || !g_pt) {
		printf("FAIL: malloc len=%zu\n", len);
		failures++;
		pass = 0;
		goto done;
	}
	for (size_t i = 0; i < len; i++)
		plain[i] = (uint8_t)(i * 31 + 7);

	/* 1) gmssl 加密模拟存量密文 */
	g_ctlen = 0;
	if (1 != gmssl_encrypt(plain, len, g_ct, &g_ctlen)) {
		snprintf(msg, sizeof(msg), "gmssl encrypt len=%zu", len);
		CHECK(0, msg);
		pass = 0;
		goto done;
	}

	/* 2) 核心断言：openssl4 直接解密 gmssl 密文得原文 */
	o_ptlen = len + 32;
	if (!ossl4_decrypt(g_ct, g_ctlen, o_pt, &o_ptlen) || o_ptlen != len ||
	    (len > 0 && memcmp(o_pt, plain, len) != 0)) {
		snprintf(msg, sizeof(msg),
			 "openssl4 decrypts gmssl ciphertext len=%zu", len);
		CHECK(0, msg);
		pass = 0;
		goto done;
	}
	snprintf(msg, sizeof(msg),
		 "openssl4 decrypts gmssl ciphertext len=%zu (ct=%zu)", len,
		 g_ctlen);
	CHECK(1, msg);

	/* 3) 充分条件：双方加密输出逐字节一致（存量无需重写） */
	o_ctlen = len + 32;
	if (!ossl4_encrypt(plain, len, o_ct, &o_ctlen) || o_ctlen != g_ctlen ||
	    memcmp(o_ct, g_ct, g_ctlen) != 0) {
		snprintf(msg, sizeof(msg), "ciphertext byte-identical len=%zu",
			 len);
		CHECK(0, msg);
		pass = 0;
		goto done;
	}
	snprintf(msg, sizeof(msg), "ciphertext byte-identical len=%zu", len);
	CHECK(1, msg);

	/* 4) 反向：gmssl 解 openssl4 密文（双向可替换） */
	g_ptlen = len + 32;
	if (1 != gmssl_decrypt(o_ct, o_ctlen, g_pt, &g_ptlen) ||
	    g_ptlen != len || (len > 0 && memcmp(g_pt, plain, len) != 0)) {
		snprintf(msg, sizeof(msg),
			 "gmssl decrypts openssl4 ciphertext len=%zu", len);
		CHECK(0, msg);
		pass = 0;
		goto done;
	}
	snprintf(msg, sizeof(msg), "gmssl decrypts openssl4 ciphertext len=%zu",
		 len);
	CHECK(1, msg);

done:
	free(plain);
	free(g_ct);
	free(o_ct);
	free(o_pt);
	free(g_pt);
	return pass;
}

int main(void)
{
	/* 静态链接的 openssl4 自带 default provider；显式加载失败也不中断，
	 * 后续 EVP 调用会按内置 provider 继续工作 */
	OSSL_PROVIDER *def = OSSL_PROVIDER_load(NULL, "default");
	printf("openssl: %s\n", OpenSSL_version(OPENSSL_VERSION));
	printf("default provider: %s\n", def ? "loaded" : "builtin/skip");

	/* 覆盖 padding 边界（0/15/16/17/31/32）、小对象、块尺寸与 bundle 大块 */
	static const size_t lens[] = { 0,  1,	15,   16,   17,	   31,
				       32, 100, 1024, 4096, 65536, 1048576 };
	for (size_t i = 0; i < sizeof(lens) / sizeof(lens[0]); i++)
		test_one_len(lens[i]);

	printf("\n%s\n",
	       failures == 0 ? "ALL TESTS PASSED" : "SOME TESTS FAILED");
	return failures == 0 ? 0 : 1;
}

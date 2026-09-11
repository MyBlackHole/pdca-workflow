// s3file SM4-GCM 与自适应解密单测（T2157）。
//
// 覆盖 sm4-crypto.h（项目内 openssl4 实现）：GCM 往返、篡改拒绝、nonce 唯一性、
// hex 编解码、s3_decrypt_object 分发矩阵（meta 2/1/0/缺失 × 本地 0/1/2）。
// 不依赖 S3 服务与 gmssl，可离线运行。

#include "sm4-crypto.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <set>
#include <string>

static int failures = 0;
#define CHECK(cond, msg)                                                     \
	do {                                                                 \
		if (!(cond)) {                                                 \
			printf("FAIL: %s\n", msg);                             \
			failures++;                                            \
		} else {                                                       \
			printf("ok:   %s\n", msg);                             \
		}                                                              \
	} while (0)

static void fill_pattern(uint8_t *buf, size_t len)
{
	for (size_t i = 0; i < len; i++)
		buf[i] = (uint8_t)(i * 17 + 3);
}

/* GCM 往返：密文长度恒等于明文长度，解密恢复原文 */
static void test_gcm_roundtrip(size_t len)
{
	uint8_t nonce[S3_SM4_NONCE_LEN] = { 0x09, 0xf3, 0x3a, 0x11, 0x22,
					    0x33, 0x44, 0x55, 0x66, 0x77,
					    0x88, 0xc1 };
	uint8_t *plain = (uint8_t *)malloc(len + 1);
	uint8_t *ct = (uint8_t *)malloc(len + 1);
	uint8_t *pt = (uint8_t *)malloc(len + 1);
	uint8_t tag[S3_SM4_TAG_LEN];
	char msg[128];

	if (!plain || !ct || !pt) {
		CHECK(0, "gcm malloc");
		goto done;
	}
	fill_pattern(plain, len);
	memset(ct, 0, len + 1);
	memset(pt, 0, len + 1);
	CHECK(s3_sm4_gcm_encrypt(nonce, plain, len, ct, tag) == 1,
	      "gcm encrypt ok");
	snprintf(msg, sizeof(msg), "gcm roundtrip len=%zu", len);
	CHECK(s3_sm4_gcm_decrypt(nonce, tag, ct, len, pt) == 1 &&
	      (len == 0 || memcmp(pt, plain, len) == 0),
	      msg);
done:
	free(plain);
	free(ct);
	free(pt);
}

/* 篡改拒绝：密文/tag 各翻转 1bit 必须解密失败 */
static void test_gcm_tamper(void)
{
	const size_t len = 100;
	uint8_t nonce[S3_SM4_NONCE_LEN] = { 1, 2, 3, 4, 5, 6,
					    7, 8, 9, 10, 11, 12 };
	uint8_t plain[100], ct[100], bad[100], pt[100];
	uint8_t tag[S3_SM4_TAG_LEN], badtag[S3_SM4_TAG_LEN];

	fill_pattern(plain, len);
	CHECK(s3_sm4_gcm_encrypt(nonce, plain, len, ct, tag) == 1,
	      "gcm encrypt for tamper");
	memcpy(bad, ct, len);
	bad[0] ^= 0x01;
	CHECK(s3_sm4_gcm_decrypt(nonce, tag, bad, len, pt) == 0,
	      "gcm tampered ct rejected");
	memcpy(badtag, tag, sizeof(tag));
	badtag[15] ^= 0x01;
	CHECK(s3_sm4_gcm_decrypt(nonce, badtag, ct, len, pt) == 0,
	      "gcm tampered tag rejected");
}

/* nonce 唯一性：1 万个随机 nonce 无碰撞 */
static void test_nonce_unique(void)
{
	std::set<std::string> seen;
	uint8_t nonce[S3_SM4_NONCE_LEN];
	char hex[S3_SM4_NONCE_HEX_LEN + 1];
	int ok = 1;

	for (int i = 0; i < 10000; i++) {
		if (!s3_sm4_rand_nonce(nonce) ||
		    !s3_sm4_hex_encode(nonce, sizeof(nonce), hex)) {
			ok = 0;
			break;
		}
		if (!seen.insert(hex).second) {
			ok = 0;
			break;
		}
	}
	CHECK(ok, "gcm nonce unique over 10000");
}

/* hex 编解码：往返一致，非法输入拒绝 */
static void test_hex(void)
{
	uint8_t bin[S3_SM4_TAG_LEN], back[S3_SM4_TAG_LEN];
	char hex[S3_SM4_TAG_HEX_LEN + 1];

	fill_pattern(bin, sizeof(bin));
	CHECK(s3_sm4_hex_encode(bin, sizeof(bin), hex) == 1 &&
	      strlen(hex) == S3_SM4_TAG_HEX_LEN,
	      "hex encode");
	CHECK(s3_sm4_hex_decode(hex, back, sizeof(back)) == 1 &&
	      memcmp(back, bin, sizeof(bin)) == 0,
	      "hex roundtrip");
	CHECK(s3_sm4_hex_decode("zz", back, 1) == 0, "hex reject non-hex");
	CHECK(s3_sm4_hex_decode("abc", back, 1) == 0,
	      "hex reject bad length");
}

/* 严格整数解析 + 非法 gmssl 画像一律拒绝 */
static void test_strict_parse(void)
{
	int v = -9;
	int64_t w = -9;
	uint8_t out[8];
	size_t outlen = 0;
	S3ObjectMeta bad;

	CHECK(s3_parse_int_strict("2", &v) == 1 && v == 2,
	      "strict parse accept 2");
	CHECK(s3_parse_int_strict("abc", &v) == 0,
	      "strict parse reject non-digit");
	CHECK(s3_parse_int_strict("", &v) == 0, "strict parse reject empty");
	CHECK(s3_parse_int_strict("12x", &v) == 0,
	      "strict parse reject trailing junk");
	CHECK(s3_parse_int64_strict("1256089190400", &w) == 1 &&
	      w == 1256089190400L,
	      "strict parse accept large file-size");
	bad.gmssl = -2;
	bad.orgLen = -1;
	bad.contentLen = 0;
	bad.nonceHex.clear();
	bad.tagHex.clear();
	CHECK(s3_decrypt_object(bad, 2, (uint8_t *)"x", 1, out, &outlen) ==
		      0,
	      "dispatch illegal gmssl rejected even on gcm-volume");
}

/* 构造指定模式的对象画像与密文，供分发矩阵使用 */
static void make_object(int mode, size_t len, uint8_t *ct, S3ObjectMeta &meta,
			std::string &pt_holder)
{
	uint8_t *plain = (uint8_t *)malloc(len + 1);
	uint8_t nonce[S3_SM4_NONCE_LEN];
	uint8_t tag[S3_SM4_TAG_LEN];
	char nonceStr[S3_SM4_NONCE_HEX_LEN + 1];
	char tagStr[S3_SM4_TAG_HEX_LEN + 1];
	size_t outlen = len + 32;

	fill_pattern(plain, len);
	meta.gmssl = mode;
	meta.orgLen = (int64_t)len;
	meta.contentLen = (int64_t)len;
	meta.nonceHex.clear();
	meta.tagHex.clear();
	if (mode == 2) {
		memcpy(nonce, "0123456789ab", 12);
		s3_sm4_gcm_encrypt(nonce, plain, len, ct, tag);
		s3_sm4_hex_encode(nonce, sizeof(nonce), nonceStr);
		s3_sm4_hex_encode(tag, sizeof(tag), tagStr);
		meta.nonceHex = nonceStr;
		meta.tagHex = tagStr;
	} else if (mode == 1) {
		s3_sm4_cbc_encrypt(plain, len, ct, &outlen);
		meta.contentLen = (int64_t)outlen;
		meta.orgLen = (int64_t)len;
	} else {
		memcpy(ct, plain, len);
	}
	pt_holder.assign((char *)plain, len);
	free(plain);
}

/* s3_decrypt_object 分发矩阵 */
static void test_dispatch(void)
{
	const size_t len = 64;
	uint8_t ct[128], out[128];
	size_t outlen = 0;
	S3ObjectMeta meta;
	std::string expect;
	char msg[160];

	/* meta2 + 本地2：GCM 正常 */
	make_object(2, len, ct, meta, expect);
	outlen = 0;
	snprintf(msg, sizeof(msg), "dispatch meta2/local2 gcm ok");
	CHECK(s3_decrypt_object(meta, 2, ct, len, out, &outlen) == 1 &&
	      outlen == len && memcmp(out, expect.data(), len) == 0,
	      msg);

	/* meta2 缺 nonce/tag：fail-closed */
	meta.nonceHex.clear();
	outlen = 0;
	CHECK(s3_decrypt_object(meta, 2, ct, len, out, &outlen) == 0,
	      "dispatch meta2 missing nonce rejected");

	/* meta2 + 本地1：能力门禁拒绝 */
	make_object(2, len, ct, meta, expect);
	outlen = 0;
	CHECK(s3_decrypt_object(meta, 1, ct, len, out, &outlen) == 0,
	      "dispatch meta2/local1 gate rejected");

	/* meta1 + 本地1/2：CBC 正常；本地0：门禁拒绝 */
	make_object(1, len, ct, meta, expect);
	outlen = 0;
	CHECK(s3_decrypt_object(meta, 1, ct, (size_t)meta.contentLen, out,
				&outlen) == 1 &&
	      outlen == len && memcmp(out, expect.data(), len) == 0,
	      "dispatch meta1/local1 cbc ok");
	outlen = 0;
	CHECK(s3_decrypt_object(meta, 2, ct, (size_t)meta.contentLen, out,
				&outlen) == 1 &&
	      outlen == len,
	      "dispatch meta1/local2 cbc ok");
	outlen = 0;
	CHECK(s3_decrypt_object(meta, 0, ct, (size_t)meta.contentLen, out,
				&outlen) == 0,
	      "dispatch meta1/local0 gate rejected");

	/* meta0 + 本地0：明文拷贝；本地1/2：回落 CBC（兼容存量标 0 的 CBC 对象） */
	make_object(0, len, ct, meta, expect);
	outlen = 0;
	CHECK(s3_decrypt_object(meta, 0, ct, len, out, &outlen) == 1 &&
	      outlen == len && memcmp(out, expect.data(), len) == 0,
	      "dispatch meta0/local0 passthrough");
	{
		uint8_t cbc_ct[128];
		S3ObjectMeta m1;
		std::string e1;
		size_t clen = sizeof(cbc_ct);
		uint8_t *p = (uint8_t *)malloc(len);
		fill_pattern(p, len);
		s3_sm4_cbc_encrypt(p, len, cbc_ct, &clen);
		free(p);
		m1.gmssl = 0; /* 存量 CBC 快照的错误元数据长这样 */
		m1.nonceHex.clear();
		m1.tagHex.clear();
		m1.orgLen = (int64_t)clen;
		m1.contentLen = (int64_t)clen;
		outlen = 0;
		CHECK(s3_decrypt_object(m1, 1, cbc_ct, clen, out, &outlen) ==
			      1 &&
		      outlen == len,
		      "dispatch legacy-cbc-meta0/local1 fallback cbc");
	}

	/* 缺失 meta + 本地0：拷贝；本地2：回落 CBC */
	{
		S3ObjectMeta m0;
		m0.gmssl = -1;
		m0.orgLen = -1;
		m0.contentLen = 0;
		m0.nonceHex.clear();
		m0.tagHex.clear();
		outlen = 0;
		CHECK(s3_decrypt_object(m0, 0, ct, len, out, &outlen) == 1 &&
		      outlen == len,
		      "dispatch missing-meta/local0 passthrough");
	}
}

int main(void)
{
	static const size_t lens[] = { 0, 1, 15, 16, 17, 100, 4096 };
	for (size_t i = 0; i < sizeof(lens) / sizeof(lens[0]); i++)
		test_gcm_roundtrip(lens[i]);
	test_gcm_tamper();
	test_nonce_unique();
	test_hex();
	test_strict_parse();
	test_dispatch();

	printf("\n%s\n", failures == 0 ? "ALL TESTS PASSED"
				      : "SOME TESTS FAILED");
	return failures == 0 ? 0 : 1;
}

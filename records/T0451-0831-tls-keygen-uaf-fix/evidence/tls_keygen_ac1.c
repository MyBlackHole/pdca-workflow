#include "tls_keygen.h"
#include "common.h"
#include "version.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <sys/stat.h>
#include <errno.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <arpa/inet.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/bn.h>
#include <openssl/rand.h>
#include <time.h>
#include <sys/stat.h>

static int g_verbose = 0;

/* 统一证书文件名：复用 common.h 常量，避免硬编码拼接 */
static const char *keygen_host_key_file(const char *algo)
{
	if (strcmp(algo, TLS_KEYGEN_ALGO_SM2) == 0)
		return CERT_FILE_SM2_HOST_KEY;
	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) == 0)
		return CERT_FILE_ED25519_HOST_KEY;
	return CERT_FILE_HOST_KEY;
}
static const char *keygen_host_csr_file(const char *algo)
{
	if (strcmp(algo, TLS_KEYGEN_ALGO_SM2) == 0)
		return CERT_FILE_SM2_HOST_CSR;
	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) == 0)
		return CERT_FILE_ED25519_HOST_CSR;
	return CERT_FILE_HOST_CSR;
}
static const char *keygen_host_cert_file(const char *algo)
{
	if (strcmp(algo, TLS_KEYGEN_ALGO_SM2) == 0)
		return CERT_FILE_SM2_HOST;
	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) == 0)
		return CERT_FILE_ED25519_HOST;
	return CERT_FILE_HOST;
}
static const char *keygen_ca_key_file(const char *algo)
{
	if (strcmp(algo, TLS_KEYGEN_ALGO_SM2) == 0)
		return "sm2_ca.key";
	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) == 0)
		return CERT_FILE_ED25519_CA_KEY;
	return CERT_FILE_CA_KEY;
}
static const char *keygen_ca_cert_file(const char *algo)
{
	if (strcmp(algo, TLS_KEYGEN_ALGO_SM2) == 0)
		return CERT_FILE_SM2_CA;
	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) == 0)
		return CERT_FILE_ED25519_CA;
	return CERT_FILE_CA;
}

/* 开启 verbose 时输出 OpenSSL 错误队列，否则清空抑制 */
static void dump_openssl_errors(const char *where)
{
	if (g_verbose) {
		fprintf(stderr, "OpenSSL error(s) at %s:\n", where);
		ERR_print_errors_fp(stderr);
	} else {
		ERR_clear_error();
	}
}

/* T0402：把内部错误码枚举映射为使用者可直接理解的含义短语。
 * -3 等数字对使用者无意义，必须写出它代表什么（如写文件失败），
 * 配合 handler 汇总行呈现 "failed to create CA: failed to write output file (code: -3)"。 */
static const char *tls_keygen_errmsg(int code)
{
	switch (code) {
	case TLS_KEYGEN_OK:
		return "success";
	case TLS_KEYGEN_ERR_PARAM:
		return "invalid parameter";
	case TLS_KEYGEN_ERR_GENERATE:
		return "key generation failed";
	case TLS_KEYGEN_ERR_WRITE:
		return "failed to write output file";
	case TLS_KEYGEN_ERR_FILE:
		return "file access error";
	case TLS_KEYGEN_ERR_CSR:
		return "CSR generation failed";
	case TLS_KEYGEN_ERR_CA_CREATE:
		return "CA certificate creation failed";
	case TLS_KEYGEN_ERR_SIGN:
		return "certificate signing failed";
	case TLS_KEYGEN_ERR_KEY_MISMATCH:
		return "CA key/certificate mismatch";
	default:
		return "unknown error";
	}
}

/* T3973：sign 未显式传 --san 时写入的回环默认集，保证默认产物可被
 * 严格客户端（Go/ossutil/curl）按 RFC 6125 校验通过 */
#define TLS_KEYGEN_DEFAULT_SAN "DNS:localhost,IP:127.0.0.1,IP:::1"

static int set_file_permissions(const char *path, mode_t mode)
{
	return chmod(path, mode);
}

/**
 * gen_pkey_by_algo - 按算法生成非对称密钥
 * @algo: TLS_KEYGEN_ALGO_ED25519 / TLS_KEYGEN_ALGO_SM2
 * @pkey: 输出密钥指针
 *
 * Ed25519 直接走 EVP_PKEY_ED25519；SM2 走 EC 曲线 NID_sm2，
 * OpenSSL 3.0+ 自动将 SM2 曲线密钥识别为 EVP_PKEY_SM2 类型。
 */
static int gen_pkey_by_algo(const char *algo, EVP_PKEY **pkey)
{
	if (!algo || !pkey) {
		return TLS_KEYGEN_ERR_PARAM;
	}

	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) == 0) {
		EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_ED25519, NULL);
		if (!ctx) {
			dump_openssl_errors("keygen(ed25519) context");
			return TLS_KEYGEN_ERR_GENERATE;
		}
		if (EVP_PKEY_keygen_init(ctx) <= 0 ||
		    EVP_PKEY_keygen(ctx, pkey) <= 0) {
			dump_openssl_errors("keygen(ed25519)");
			EVP_PKEY_CTX_free(ctx);
			return TLS_KEYGEN_ERR_GENERATE;
		}
		EVP_PKEY_CTX_free(ctx);
		return TLS_KEYGEN_OK;
	}

	if (strcmp(algo, TLS_KEYGEN_ALGO_SM2) == 0) {
		/* SM2 必须以 EVP_PKEY_SM2 为起点 keygen（而非 EC 再设曲线），
		 * 否则生成的密钥缺少 SM2 属性，X509_sign 会因 distid 参数缺失失败。
		 * SM2 为固定曲线（curveSM2），无需 set_ec_paramgen_curve_nid。 */
		EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_SM2, NULL);
		if (!ctx) {
			dump_openssl_errors("keygen(sm2) context");
			return TLS_KEYGEN_ERR_GENERATE;
		}
		if (EVP_PKEY_keygen_init(ctx) <= 0 ||
		    EVP_PKEY_keygen(ctx, pkey) <= 0) {
			dump_openssl_errors("keygen(sm2)");
			EVP_PKEY_CTX_free(ctx);
			return TLS_KEYGEN_ERR_GENERATE;
		}
		EVP_PKEY_CTX_free(ctx);
		return TLS_KEYGEN_OK;
	}

	return TLS_KEYGEN_ERR_PARAM;
}

/**
 * algo_to_digest - 按算法返回证书/CSR 签名摘要
 * SM2 必须显式使用 EVP_sm3()（RFC 8998 sm2sig_sm3）；Ed25519 传 NULL 由 OpenSSL 自动选择
 */
static const EVP_MD *algo_to_digest(const char *algo)
{
	if (strcmp(algo, TLS_KEYGEN_ALGO_SM2) == 0) {
		return EVP_sm3();
	}
	return NULL;
}

static char *read_cn_from_file(void)
{
	FILE *fp = fopen(HOST_ID_FILE, "r");
	if (!fp) {
		return NULL;
	}

	char buf[256];
	if (!fgets(buf, sizeof(buf), fp)) {
		fclose(fp);
		return NULL;
	}
	fclose(fp);

	// 去除换行符
	size_t len = strlen(buf);
	while (len > 0 && (buf[len - 1] == '\n' || buf[len - 1] == '\r')) {
		buf[--len] = '\0';
	}

	if (len == 0) {
		return NULL;
	}

	return strdup(buf);
}

int tls_keygen_create(int force, const char *key_path, const char *csr_path)
{
	return tls_keygen_create_with_algo(force, key_path, csr_path,
					   TLS_KEYGEN_ALGO_ED25519);
}

int tls_keygen_create_with_algo(int force, const char *key_path,
				const char *csr_path, const char *algo)
{
	if (!key_path || !key_path[0] || !csr_path || !csr_path[0]) {
		return TLS_KEYGEN_ERR_PARAM;
	}

	// 检查文件是否已存在
	if (!force) {
		struct stat st;
		if (stat(key_path, &st) == 0 || stat(csr_path, &st) == 0) {
			fprintf(stderr,
				"Error: output files already exist. Use -f to overwrite.\n");
			return TLS_KEYGEN_ERR_FILE;
		}
	}

	// 生成私钥
	EVP_PKEY *pkey = NULL;
	int ret = gen_pkey_by_algo(algo, &pkey);
	if (ret != TLS_KEYGEN_OK) {
		return ret;
	}

	// 写入私钥
	FILE *fp = fopen(key_path, "w");
	if (!fp) {
		fprintf(stderr,
			"Error: cannot open %s for writing: %s\n",
			key_path, strerror(errno));
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_WRITE;
	}

	PEM_write_PrivateKey(fp, pkey, NULL, NULL, 0, NULL, NULL);
	fclose(fp);
	set_file_permissions(key_path, 0600);

	printf("Generating private key (%s)... done\n", algo);

	// 读取 CN
	char *cn = read_cn_from_file();
	if (!cn) {
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_FILE;
	}

	// 创建 CSR
	X509_REQ *req = X509_REQ_new();
	if (!req) {
		free(cn);
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_CSR;
	}

	// 设置 Subject
	// 注：OpenSSL 4 中 X509_REQ_get_subject_name 返回 const 指针，无法直接修改，
	// 故先新建 X509_NAME 填充后通过 X509_REQ_set_subject_name 设置（兼容 3/4）
	X509_NAME *name = X509_NAME_new();
	if (!name) {
		X509_REQ_free(req);
		EVP_PKEY_free(pkey);
		free(cn);
		return TLS_KEYGEN_ERR_CSR;
	}
	X509_NAME_add_entry_by_txt(name, "CN", MBSTRING_ASC,
				   (unsigned char *)cn, -1, -1, 0);
	X509_REQ_set_subject_name(req, name);
	X509_NAME_free(name);
	free(cn);

	// 设置公钥
	if (X509_REQ_set_pubkey(req, pkey) <= 0) {
		X509_REQ_free(req);
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_CSR;
	}

	// 签名 - SM2 用 EVP_sm3()，Ed25519 传 NULL 由 OpenSSL 自动选择
	if (X509_REQ_sign(req, pkey, algo_to_digest(algo)) <= 0) {
		dump_openssl_errors("CSR sign");
		X509_REQ_free(req);
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_CSR;
	}

	// 写入 CSR
	fp = fopen(csr_path, "w");
	if (!fp) {
		fprintf(stderr,
			"Error: cannot open %s for writing: %s\n",
			csr_path, strerror(errno));
		X509_REQ_free(req);
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_WRITE;
	}

	PEM_write_X509_REQ(fp, req);
	fclose(fp);

	X509_REQ_free(req);
	EVP_PKEY_free(pkey);

	printf("Generating CSR... done\n");
	printf("Private key: %s\n", key_path);
	printf("CSR: %s\n", csr_path);

	return TLS_KEYGEN_OK;
}

int tls_keygen_create_ca(const char *cn, const char *key_path,
			 const char *cert_path, int force, int days)
{
	return tls_keygen_create_ca_with_algo(cn, key_path, cert_path, force,
					       days, TLS_KEYGEN_ALGO_ED25519);
}

int tls_keygen_create_ca_with_algo(const char *cn, const char *key_path,
				   const char *cert_path, int force, int days,
				   const char *algo)
{
	if (!cn || !key_path || !cert_path) {
		return TLS_KEYGEN_ERR_PARAM;
	}
	/* T0387：CN 必须满足客户端 tls_cert_ca_cn_valid 同款规则，
	 * 否则部署后 mTLS 握手期才暴露失败 */
	if (!cn_name_valid(cn)) {
		fprintf(stderr,
			"Error: invalid CN '%s' (allowed: [A-Za-z0-9._-], no spaces, no \"..\"); example: -n My_SM2_Root_CA\n",
			cn);
		return TLS_KEYGEN_ERR_PARAM;
	}

	if (!force) {
		struct stat st;
		if (stat(key_path, &st) == 0 || stat(cert_path, &st) == 0) {
			fprintf(stderr,
				"Error: CA files already exist. Use -f to overwrite.\n");
			return TLS_KEYGEN_ERR_FILE;
		}
	}

	EVP_PKEY *pkey = NULL;
	int ret = gen_pkey_by_algo(algo, &pkey);
	if (ret != TLS_KEYGEN_OK) {
		return ret;
	}

	FILE *fp = fopen(key_path, "w");
	if (!fp) {
		fprintf(stderr,
			"Error: cannot open %s for writing: %s\n",
			key_path, strerror(errno));
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_WRITE;
	}
	PEM_write_PrivateKey(fp, pkey, NULL, NULL, 0, NULL, NULL);
	fclose(fp);
	set_file_permissions(key_path, 0600);

	X509 *cert = X509_new();
	if (!cert) {
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_CA_CREATE;
	}

	ASN1_INTEGER_set(X509_get_serialNumber(cert), 1);
	X509_gmtime_adj(X509_get_notBefore(cert), 0);
	X509_gmtime_adj(X509_get_notAfter(cert), days * 24 * 60 * 60);

	X509_set_version(cert, 2);

	X509_NAME *name = X509_NAME_new();
	X509_NAME_add_entry_by_txt(name, "CN", MBSTRING_ASC,
				   (unsigned char *)cn, -1, -1, 0);
	X509_set_subject_name(cert, name);
	X509_set_issuer_name(cert, name);

	X509_set_pubkey(cert, pkey);

	X509V3_CTX v3ctx;
	X509V3_set_ctx(&v3ctx, cert, cert, NULL, NULL, 0);
	X509V3_set_nconf(&v3ctx, NULL);

	X509_EXTENSION *ex = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_basic_constraints, "critical,CA:TRUE");
	if (!ex) {
		X509_free(cert);
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_CA_CREATE;
	}
	X509_add_ext(cert, ex, 0);
	X509_EXTENSION_free(ex);

	X509_EXTENSION *ext_ku = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_key_usage,
		"critical,keyCertSign,cRLSign,digitalSignature");
	if (ext_ku) {
		X509_add_ext(cert, ext_ku, 0);
		X509_EXTENSION_free(ext_ku);
	}

	X509_EXTENSION *ext_ski = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_subject_key_identifier, "hash");
	if (ext_ski) {
		X509_add_ext(cert, ext_ski, 0);
		X509_EXTENSION_free(ext_ski);
	}

	X509_EXTENSION *ext_aki = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_authority_key_identifier, "keyid:always");
	if (ext_aki) {
		X509_add_ext(cert, ext_aki, 0);
		X509_EXTENSION_free(ext_aki);
	}

	if (X509_sign(cert, pkey, algo_to_digest(algo)) <= 0) {
		dump_openssl_errors("CA self-sign");
		X509_free(cert);
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_CA_CREATE;
	}

	fp = fopen(cert_path, "w");
	if (!fp) {
		fprintf(stderr,
			"Error: cannot open %s for writing: %s\n",
			cert_path, strerror(errno));
		X509_free(cert);
		EVP_PKEY_free(pkey);
		return TLS_KEYGEN_ERR_WRITE;
	}
	PEM_write_X509(fp, cert);
	fclose(fp);

	X509_free(cert);
	EVP_PKEY_free(pkey);

	printf("Creating CA (%s)... done\n", algo);
	printf("CA private key: %s\n", key_path);
	printf("CA certificate: %s\n", cert_path);

	return TLS_KEYGEN_OK;
}

int tls_keygen_sign(const char *ca_cert_path, const char *ca_key_path,
		    const char *key_path, const char *csr_path,
		    const char *out_path, int force, int days)
{
	return tls_keygen_sign_with_algo(ca_cert_path, ca_key_path, key_path,
					  csr_path, out_path, force, days,
					  TLS_KEYGEN_ALGO_ED25519, NULL);
}

int tls_keygen_sign_with_algo(const char *ca_cert_path,
			      const char *ca_key_path, const char *key_path,
			      const char *csr_path, const char *out_path,
			      int force, int days, const char *algo,
			      const char *san)
{
	const char *san_value = (san && san[0]) ? san : TLS_KEYGEN_DEFAULT_SAN;
	if (!ca_cert_path || !ca_key_path || !key_path || !csr_path ||
	    !out_path) {
		return TLS_KEYGEN_ERR_PARAM;
	}

	if (!force) {
		struct stat st;
		if (stat(out_path, &st) == 0) {
			fprintf(stderr,
				"Error: output file already exists. Use -f to overwrite.\n");
			return TLS_KEYGEN_ERR_FILE;
		}
	}

	FILE *fp = fopen(ca_cert_path, "r");
	if (!fp) {
		fprintf(stderr, "Error: cannot open CA certificate: %s\n",
			ca_cert_path);
		return TLS_KEYGEN_ERR_FILE;
	}
	X509 *ca_cert = PEM_read_X509(fp, NULL, NULL, NULL);
	fclose(fp);
	if (!ca_cert) {
		return TLS_KEYGEN_ERR_FILE;
	}

	fp = fopen(ca_key_path, "r");
	if (!fp) {
		fprintf(stderr, "Error: cannot open CA key: %s\n", ca_key_path);
		X509_free(ca_cert);
		return TLS_KEYGEN_ERR_FILE;
	}
	EVP_PKEY *ca_key = PEM_read_PrivateKey(fp, NULL, NULL, NULL);
	fclose(fp);
	if (!ca_key) {
		X509_free(ca_cert);
		return TLS_KEYGEN_ERR_FILE;
	}

	/* 校验 CA 私钥与 CA 证书匹配：不匹配时 OpenSSL X509_sign 不报错，
	 * 会静默生成"签名失败"的伪证书，运维无感知（openssl verify 才报
	 * error 7 signature failure）。这里主动拦截，杜绝伪证书产生。 */
	if (!X509_check_private_key(ca_cert, ca_key)) {
		fprintf(stderr,
			"Error: CA private key does not match CA certificate\n");
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_KEY_MISMATCH;
	}

	fp = fopen(csr_path, "r");
	if (!fp) {
		fprintf(stderr, "Error: cannot open CSR: %s\n", csr_path);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_FILE;
	}
	X509_REQ *req = PEM_read_X509_REQ(fp, NULL, NULL, NULL);
	fclose(fp);
	if (!req) {
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_FILE;
	}

	EVP_PKEY *req_pkey = X509_REQ_get_pubkey(req);
	if (!req_pkey) {
		X509_REQ_free(req);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_FILE;
	}

	if (X509_REQ_verify(req, req_pkey) <= 0) {
		fprintf(stderr, "Error: CSR verification failed\n");
		dump_openssl_errors("CSR verify");
		EVP_PKEY_free(req_pkey);
		X509_REQ_free(req);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_FILE;
	}

	X509 *cert = X509_new();
	if (!cert) {
		EVP_PKEY_free(req_pkey);
		X509_REQ_free(req);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_SIGN;
	}

	/* 序列号必须唯一：同 CA 下多张 host 证书硬编码 2 会冲突 CRL/校验。
	 * 用 RAND_bytes 生成 63 位正整数，失败回退到 time+pid 混合。 */
	{
		long long serial = 0;
		unsigned char rnd[8];
		if (RAND_bytes(rnd, sizeof(rnd)) == 1) {
			for (size_t i = 0; i < sizeof(rnd); i++)
				serial = (serial << 8) | rnd[i];
			serial &= 0x7fffffffffffffffLL;
		}
		if (serial == 0) {
			serial = (long long)time(NULL) ^ (long long)getpid() ^
				 (long long)random();
			if (serial < 0)
				serial = -serial;
			if (serial == 0)
				serial = 1;
		}
		ASN1_INTEGER_set_int64(X509_get_serialNumber(cert), serial);
	}
	X509_gmtime_adj(X509_get_notBefore(cert), 0);
	X509_gmtime_adj(X509_get_notAfter(cert), days * 24 * 60 * 60);

	X509_set_version(cert, 2);

	// 注：OpenSSL 4 中 X509_REQ_get_subject_name 返回 const 指针
	const X509_NAME *subject = X509_REQ_get_subject_name(req);
	X509_set_subject_name(cert, subject);
	X509_set_issuer_name(cert, X509_get_subject_name(ca_cert));

	if (X509_set_pubkey(cert, req_pkey) != 1) {
		EVP_PKEY_free(req_pkey);
		X509_free(cert);
		X509_REQ_free(req);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_SIGN;
	}
	EVP_PKEY_free(req_pkey);

	X509V3_CTX v3ctx;
	X509V3_set_ctx(&v3ctx, ca_cert, cert, NULL, NULL, 0);
	X509V3_set_nconf(&v3ctx, NULL);

	/* 证书扩展：basicConstraints=CA:FALSE + keyUsage + SKI/AKI */
	X509_EXTENSION *ex = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_basic_constraints, "critical,CA:FALSE");
	if (!ex) {
		X509_free(cert);
		X509_REQ_free(req);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_SIGN;
	}
	X509_add_ext(cert, ex, 0);
	X509_EXTENSION_free(ex);

	/* T3973: subjectAltName——客户端 hostname/IP 匹配的唯一依据 */
	if (san_value && san_value[0]) {
		X509_EXTENSION *ext_san = X509V3_EXT_nconf_nid(
			NULL, &v3ctx, NID_subject_alt_name, san_value);
		if (!ext_san) {
			fprintf(stderr, "Error: invalid SAN '%s'\n", san_value);
			dump_openssl_errors("SAN ext");
			X509_free(cert);
			X509_REQ_free(req);
			X509_free(ca_cert);
			EVP_PKEY_free(ca_key);
			return TLS_KEYGEN_ERR_SIGN;
		}
		X509_add_ext(cert, ext_san, 1);
		X509_EXTENSION_free(ext_san);
	}

	X509_EXTENSION *ext_ku = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_key_usage,
		"critical,digitalSignature,keyEncipherment,keyAgreement");
	if (ext_ku) {
		X509_add_ext(cert, ext_ku, 0);
		X509_EXTENSION_free(ext_ku);
	}

	X509_EXTENSION *ext_ski = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_subject_key_identifier, "hash");
	if (ext_ski) {
		X509_add_ext(cert, ext_ski, 0);
		X509_EXTENSION_free(ext_ski);
	}

	X509_EXTENSION *ext_aki = X509V3_EXT_nconf_nid(
		NULL, &v3ctx, NID_authority_key_identifier, "keyid:always");
	if (ext_aki) {
		X509_add_ext(cert, ext_aki, 0);
		X509_EXTENSION_free(ext_aki);
	}

	if (X509_sign(cert, ca_key, algo_to_digest(algo)) <= 0) {
		dump_openssl_errors("cert sign");
		X509_free(cert);
		X509_REQ_free(req);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_SIGN;
	}

	fp = fopen(out_path, "w");
	if (!fp) {
		fprintf(stderr,
			"Error: cannot open %s for writing: %s\n",
			out_path, strerror(errno));
		X509_free(cert);
		X509_REQ_free(req);
		X509_free(ca_cert);
		EVP_PKEY_free(ca_key);
		return TLS_KEYGEN_ERR_WRITE;
	}
	PEM_write_X509(fp, cert);
	fclose(fp);

	X509_free(cert);
	X509_REQ_free(req);
	X509_free(ca_cert);
	EVP_PKEY_free(ca_key);

	printf("Signing certificate... done\n");
	printf("Certificate: %s\n", out_path);

	return TLS_KEYGEN_OK;
}

typedef enum { CMD_NONE, CMD_CREATE, CMD_CA, CMD_SIGN, CMD_INSPECT,
	       CMD_MTLS } subcommand_t;

static void print_create_usage(const char *prog)
{
	printf("Usage: %s create [OPTIONS]\n", prog);
	printf("Options:\n");
	printf("  -o, --output <path>   Output base path (without extension)\n");
	printf("  -f, --force           Overwrite existing files\n");
	printf("  -n, --cn <name>       Certificate Common Name\n");
	printf("  -a, --algo <algo>     Key algorithm: ed25519 (default) / sm2\n");
	printf("      --key <path>      Host private key path override\n");
	printf("      --csr <path>      CSR path override\n");
	printf("  -h, --help            Show this help message\n");
	printf("\nOutput files use algorithm prefix: {algo}_host.key, {algo}_host.csr\n");
	printf("\nExamples:\n");
	printf("  # Generate host private key and CSR\n");
	printf("  %s create\n", prog);
	printf("\n");
	printf("  # Generate SM2 host private key and CSR\n");
	printf("  %s create -a sm2\n", prog);
	printf("\n");
	printf("  # Generate to custom directory\n");
	printf("  %s create -o /tmp/certs\n", prog);
	printf("\n");
	printf("  # Generate with CN (output to DEFAULT_CERT_DIR/CN/)\n");
	printf("  %s create -n myhost\n", prog);
	printf("\n");
	printf("  # Force overwrite existing files\n");
	printf("  %s create -f\n", prog);
}

static void print_ca_usage(const char *prog)
{
	printf("Usage: %s ca [OPTIONS]\n", prog);
	printf("Options:\n");
	printf("  -n, --cn <name>       CA Common Name (required)\n");
	printf("  -o, --output <path>   Output directory\n");
	printf("  -f, --force           Overwrite existing files\n");
	printf("  -a, --algo <algo>     Key algorithm: ed25519 (default) / sm2\n");
	printf("      --days <days>     CA certificate validity days (default: %d)\n",
	       3650);
	printf("      --key <path>      CA private key path override\n");
	printf("      --cert <path>     CA certificate path override\n");
	printf("  -h, --help            Show this help message\n");
	printf("\nOutput files use algorithm prefix: {algo}_ca.key, {algo}_ca.crt\n");
	printf("\nExamples:\n");
	printf("  # Create a self-signed CA certificate\n");
	printf("  %s ca -n \"My_Root_CA\"\n", prog);
	printf("\n");
	printf("  # Create an SM2 self-signed CA certificate\n");
	printf("  %s ca -n \"My_SM2_Root_CA\" -a sm2\n", prog);
	printf("\n");
	printf("  # Create CA to custom directory\n");
	printf("  %s ca -n \"My_Root_CA\" -o /tmp/ca\n", prog);
	printf("\n");
	printf("  # Create CA with custom validity (10 years)\n");
	printf("  %s ca -n \"My_Root_CA\" --days 3650\n", prog);
}

static void print_sign_usage(const char *prog)
{
	printf("Usage: %s sign [OPTIONS]\n", prog);
	printf("Options:\n");
	printf("  -o, --output <path>   Output base path (without extension)\n");
	printf("  -f, --force           Overwrite existing files\n");
	printf("  -n, --cn <name>       Certificate Common Name\n");
	printf("  -a, --algo <algo>     Sign algorithm: ed25519 (default) / sm2\n");
	printf("      --ca-cert <path>  CA certificate path override\n");
	printf("      --ca-key <path>   CA private key path override\n");
	printf("      --key <path>      Host private key path override\n");
	printf("      --csr <path>      CSR path override\n");
	printf("      --out <path>      Output certificate path override\n");
	printf("      --days <days>     Certificate validity days (default: %d)\n",
	       365);
	printf("      --san <entries>   subjectAltName, comma-separated DNS:/IP: entries\n");
	printf("                        (default: %s; explicit value fully overrides it)\n",
	       TLS_KEYGEN_DEFAULT_SAN);
	printf("  -h, --help            Show this help message\n");
	printf("\nExamples:\n");
	printf("  # Sign host certificate using default CA\n");
	printf("  %s sign\n", prog);
	printf("\n");
	printf("  # Sign an SM2 host certificate using SM2 CA\n");
	printf("  %s sign -a sm2 --ca-cert /tmp/sm2/ca.crt --ca-key /tmp/sm2/ca.key\n",
	       prog);
	printf("\n");
	printf("  # Sign to custom directory\n");
	printf("  %s sign -o /tmp/certs\n", prog);
	printf("\n");
	printf("  # Sign with CN (output to DEFAULT_CERT_DIR/CN/)\n");
	printf("  %s sign -n myhost\n", prog);
	printf("\n");
	printf("  # Sign with custom CA paths\n");
	printf("  %s sign --ca-cert /tmp/ca/ca.crt --ca-key /tmp/ca/ca.key\n",
	       prog);
	printf("\n");
	printf("  # Sign with custom validity (2 years)\n");
	printf("  %s sign --days 730\n", prog);
}

static void print_global_help(const char *prog)
{
	printf("Usage: %s <subcommand> [OPTIONS]\n", prog);
	printf("Subcommands:\n");
	printf("  create                 Generate host private key and CSR (algo: ed25519/sm2)\n");
	printf("  ca                     Create self-signed CA certificate (algo: ed25519/sm2)\n");
	printf("  sign                   Sign host certificate using CA (algo: ed25519/sm2)\n");
	printf("  inspect                Show certificate/key details (debug)\n");
	printf("  mtls                   Self-test mTLS handshake with generated certs (debug)\n");
	printf("\nQuick start:\n");
	printf("  # 1. Create a CA (default paths under %s)\n", DEFAULT_CERT_DIR);
	printf("  %s ca -n \"My CA\"\n", prog);
	printf("  # 2. Generate host key + CSR\n");
	printf("  %s create\n", prog);
	printf("  # 3. Sign the host certificate with the CA\n");
	printf("  %s sign\n", prog);
	printf("  # 4. Inspect the signed host certificate\n");
	printf("  %s inspect %s\n", prog, HOST_CERT_PATH);
	printf("  # 5. Self-test mTLS handshake using the default host certs\n");
	printf("  %s mtls --ca %s --server-cert %s --server-key %s \\\n",
	       prog, CA_CERT_PATH, HOST_CERT_PATH, HOST_KEY_PATH);
	printf("         --client-cert %s --client-key %s\n",
	       HOST_CERT_PATH, HOST_KEY_PATH);
	printf("\nOptions:\n");
	printf("  -v, --version         Show version information\n");
	printf("  -V, --verbose         Enable verbose OpenSSL error output (any position)\n");
	printf("  -h, --help            Show this help message\n");
	printf("\nRun '%s <subcommand> --help' for more information on a subcommand.\n",
	       prog);
}

static int handle_create(int argc, char *argv[])
{
	int force = 0;
	char *output_path = NULL;
	char *key_path = NULL;
	char *csr_path = NULL;
	char *cn = NULL;
	const char *algo = TLS_KEYGEN_ALGO_ED25519;

	static struct option long_options[] = {
		{ "output", required_argument, 0, 'o' },
		{ "force", no_argument, 0, 'f' },
		{ "cn", required_argument, 0, 'n' },
		{ "algo", required_argument, 0, 'a' },
		{ "key", required_argument, 0, 1003 },
		{ "csr", required_argument, 0, 1004 },
		{ "help", no_argument, 0, 'h' },
		{ 0, 0, 0, 0 }
	};

	int opt;
	int has_help = 0;
	for (int i = 0; i < argc; i++) {
		if (strcmp(argv[i], "-h") == 0 ||
		    strcmp(argv[i], "--help") == 0) {
			has_help = 1;
			break;
		}
	}

	if (has_help) {
		print_create_usage("tls-keygen");
		return 0;
	}

	while ((opt = getopt_long(argc, argv, "o:fhn:a:", long_options, NULL)) !=
	       -1) {
		switch (opt) {
		case 'o':
			output_path = optarg;
			break;
		case 'f':
			force = 1;
			break;
		case 'n':
			cn = optarg;
			break;
		case 'a':
			algo = optarg;
			break;
		case 1003:
			key_path = optarg;
			break;
		case 1004:
			csr_path = optarg;
			break;
		default:
			break;
		}
	}

	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) != 0 &&
	    strcmp(algo, TLS_KEYGEN_ALGO_SM2) != 0) {
		fprintf(stderr,
			"Error: unknown algorithm '%s' (supported: ed25519, sm2)\n",
			algo);
		return 1;
	}

	char key_buf[1024];
	char csr_buf[1024];
	char *final_key_path;
	char *final_csr_path;

	const char *algo_host_key = keygen_host_key_file(algo);
	const char *algo_host_csr = keygen_host_csr_file(algo);

	if (output_path) {
		if (mkdir_path(output_path) != 0) {
			fprintf(stderr,
				"Error: failed to create output directory: %s\n",
				output_path);
			return 1;
		}
		snprintf(key_buf, sizeof(key_buf), "%s/%s", output_path,
			 algo_host_key);
		snprintf(csr_buf, sizeof(csr_buf), "%s/%s", output_path,
			 algo_host_csr);
		final_key_path = key_buf;
		final_csr_path = csr_buf;
	} else if (cn) {
		if (!cn_name_valid(cn)) {
			fprintf(stderr,
				"Error: invalid CN '%s' (allowed: [A-Za-z0-9._-], no spaces, no \"..\"); example: -n My_SM2_Root_CA\n",
				cn);
			return 1;
		}
		char cn_dir[512];
		snprintf(cn_dir, sizeof(cn_dir), "%s%s", DEFAULT_CERT_DIR, cn);
		if (mkdir_path(cn_dir) != 0) {
			fprintf(stderr,
				"Error: failed to create output directory: %s\n",
				cn_dir);
			return 1;
		}
		snprintf(key_buf, sizeof(key_buf), "%s/%s", cn_dir,
			 algo_host_key);
		snprintf(csr_buf, sizeof(csr_buf), "%s/%s", cn_dir,
			 algo_host_csr);
		final_key_path = key_buf;
		final_csr_path = csr_buf;
	} else {
		/* T0401：默认输出到 DEFAULT_CERT_DIR，目录可能不存在，先创建 */
		if (mkdir_path(DEFAULT_CERT_DIR) != 0) {
			fprintf(stderr,
				"Error: failed to create default cert directory: %s\n",
				DEFAULT_CERT_DIR);
			return 1;
		}
		snprintf(key_buf, sizeof(key_buf), "%s%s", DEFAULT_CERT_DIR,
			 algo_host_key);
		snprintf(csr_buf, sizeof(csr_buf), "%s%s", DEFAULT_CERT_DIR,
			 algo_host_csr);
		final_key_path = key_path ? key_path : key_buf;
		final_csr_path = csr_path ? csr_path : csr_buf;
	}

	printf("Generating private key: %s\n", final_key_path);
	printf("Generating CSR: %s\n", final_csr_path);

	int ret = tls_keygen_create_with_algo(force, final_key_path,
					       final_csr_path, algo);
	if (ret != TLS_KEYGEN_OK) {
		fprintf(stderr,
			"Error: failed to generate key and CSR: %s (code: %d)\n",
			tls_keygen_errmsg(ret), ret);
		return 1;
	}

	return 0;
}

static int handle_ca(int argc, char *argv[])
{
	int force = 0;
	int days = 3650;
	char *output_path = NULL;
	char *cn = NULL;
	char *key_path = NULL;
	char *cert_path = NULL;
	const char *algo = TLS_KEYGEN_ALGO_ED25519;

	static struct option long_options[] = {
		{ "output", required_argument, 0, 'o' },
		{ "force", no_argument, 0, 'f' },
		{ "cn", required_argument, 0, 'n' },
		{ "algo", required_argument, 0, 'a' },
		{ "days", required_argument, 0, 1006 },
		{ "key", required_argument, 0, 1002 },
		{ "cert", required_argument, 0, 1001 },
		{ "help", no_argument, 0, 'h' },
		{ 0, 0, 0, 0 }
	};

	int opt;
	int has_help = 0;
	for (int i = 0; i < argc; i++) {
		if (strcmp(argv[i], "-h") == 0 ||
		    strcmp(argv[i], "--help") == 0) {
			has_help = 1;
			break;
		}
	}

	if (has_help) {
		print_ca_usage("tls-keygen");
		return 0;
	}

	while ((opt = getopt_long(argc, argv, "o:fhn:a:", long_options, NULL)) !=
	       -1) {
		switch (opt) {
		case 'o':
			output_path = optarg;
			break;
		case 'f':
			force = 1;
			break;
		case 'n':
			cn = optarg;
			break;
		case 'a':
			algo = optarg;
			break;
		case 1006:
			days = atoi(optarg);
			break;
		case 1002:
			key_path = optarg;
			break;
		case 1001:
			cert_path = optarg;
			break;
		default:
			break;
		}
	}

	if (!cn) {
		fprintf(stderr, "Error: -n/--cn is required for CA creation\n");
		return 1;
	}

	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) != 0 &&
	    strcmp(algo, TLS_KEYGEN_ALGO_SM2) != 0) {
		fprintf(stderr,
			"Error: unknown algorithm '%s' (supported: ed25519, sm2)\n",
			algo);
		return 1;
	}

	char ca_key_buf[512];
	char ca_cert_buf[512];
	char *final_key_path;
	char *final_cert_path;

	const char *algo_ca_key = keygen_ca_key_file(algo);
	const char *algo_ca_cert = keygen_ca_cert_file(algo);

	if (output_path) {
		if (mkdir_path(output_path) != 0) {
			fprintf(stderr,
				"Error: failed to create output directory: %s\n",
				output_path);
			return 1;
		}
		snprintf(ca_key_buf, sizeof(ca_key_buf), "%s/%s", output_path,
			 algo_ca_key);
		snprintf(ca_cert_buf, sizeof(ca_cert_buf), "%s/%s", output_path,
			 algo_ca_cert);
		final_key_path = ca_key_buf;
		final_cert_path = ca_cert_buf;
	} else {
		/* T0401：默认输出到 DEFAULT_CERT_DIR，目录可能不存在，
		 * 先创建（本级 + 父级），否则 fopen 写密钥/证书返回 -3 */
		if (mkdir_path(DEFAULT_CERT_DIR) != 0) {
			fprintf(stderr,
				"Error: failed to create default cert directory: %s\n",
				DEFAULT_CERT_DIR);
			return 1;
		}
		char default_ca_key[512];
		char default_ca_cert[512];
		snprintf(default_ca_key, sizeof(default_ca_key), "%s%s",
			 DEFAULT_CERT_DIR, algo_ca_key);
		snprintf(default_ca_cert, sizeof(default_ca_cert), "%s%s",
			 DEFAULT_CERT_DIR, algo_ca_cert);
		final_key_path = key_path ? key_path : default_ca_key;
		final_cert_path = cert_path ? cert_path : default_ca_cert;
	}

	int ret = tls_keygen_create_ca_with_algo(cn, final_key_path,
						  final_cert_path, force, days,
						  algo);
	if (ret != TLS_KEYGEN_OK) {
		fprintf(stderr,
			"Error: failed to create CA: %s (code: %d)\n",
			tls_keygen_errmsg(ret), ret);
		return 1;
	}

	return 0;
}

static int handle_sign(int argc, char *argv[])
{
	int force = 0;
	int days = 365;
	char *output_path = NULL;
	char *cn = NULL;
	char *ca_cert_path = NULL;
	char *ca_key_path = NULL;
	char *key_path = NULL;
	char *csr_path = NULL;
	char *out_path = NULL;
	const char *algo = TLS_KEYGEN_ALGO_ED25519;

	static struct option long_options[] = {
		{ "output", required_argument, 0, 'o' },
		{ "force", no_argument, 0, 'f' },
		{ "cn", required_argument, 0, 'n' },
		{ "algo", required_argument, 0, 'a' },
		{ "ca-cert", required_argument, 0, 1001 },
		{ "ca-key", required_argument, 0, 1002 },
		{ "key", required_argument, 0, 1003 },
		{ "csr", required_argument, 0, 1004 },
		{ "out", required_argument, 0, 1005 },
		{ "days", required_argument, 0, 1006 },
		{ "san", required_argument, 0, 1007 },
		{ "help", no_argument, 0, 'h' },
		{ 0, 0, 0, 0 }
	};

	int opt;
	int has_help = 0;
	for (int i = 0; i < argc; i++) {
		if (strcmp(argv[i], "-h") == 0 ||
		    strcmp(argv[i], "--help") == 0) {
			has_help = 1;
			break;
		}
	}

	if (has_help) {
		print_sign_usage("tls-keygen");
		return 0;
	}

	char *san = NULL;

	while ((opt = getopt_long(argc, argv, "o:fhn:a:", long_options, NULL)) !=
	       -1) {
		switch (opt) {
		case 'o':
			output_path = optarg;
			break;
		case 'f':
			force = 1;
			break;
		case 'n':
			cn = optarg;
			break;
		case 'a':
			algo = optarg;
			break;
		case 1001:
			ca_cert_path = optarg;
			break;
		case 1002:
			ca_key_path = optarg;
			break;
		case 1003:
			key_path = optarg;
			break;
		case 1004:
			csr_path = optarg;
			break;
		case 1005:
			out_path = optarg;
			break;
		case 1006:
			days = atoi(optarg);
			break;
		case 1007:
			san = optarg;
			break;
		case 'h':
			has_help = 1;
			break;
		default:
			break;
		}
	}

	if (has_help) {
		print_sign_usage("tls-keygen");
		return 0;
	}

	if (strcmp(algo, TLS_KEYGEN_ALGO_ED25519) != 0 &&
	    strcmp(algo, TLS_KEYGEN_ALGO_SM2) != 0) {
		fprintf(stderr,
			"Error: unknown algorithm '%s' (supported: ed25519, sm2)\n",
			algo);
		return 1;
	}

	/* T3973: --san 显式传入则完全覆盖默认回环集；非法 fail-fast 不产证 */
	const char *san_value = (san && san[0]) ? san : TLS_KEYGEN_DEFAULT_SAN;
	if (!san_ext_valid(san_value)) {
		fprintf(stderr,
			"Error: invalid SAN '%s' (expected comma-separated DNS:<name>/IP:<addr> entries); example: --san \"DNS:host.example.com,IP:10.0.0.5\"\n",
			san_value);
		return 1;
	}

	char sign_key_buf[1024];
	char sign_csr_buf[1024];
	char sign_out_buf[1024];
	char *final_key_path;
	char *final_csr_path;
	char *final_out_path;

	const char *algo_host_key = keygen_host_key_file(algo);
	const char *algo_host_csr = keygen_host_csr_file(algo);
	const char *algo_host_cert = keygen_host_cert_file(algo);
	const char *algo_ca_key = keygen_ca_key_file(algo);
	const char *algo_ca_cert = keygen_ca_cert_file(algo);

	if (output_path) {
		if (mkdir_path(output_path) != 0) {
			fprintf(stderr,
				"Error: failed to create output directory: %s\n",
				output_path);
			return 1;
		}
		snprintf(sign_key_buf, sizeof(sign_key_buf), "%s/%s",
			 output_path, algo_host_key);
		snprintf(sign_csr_buf, sizeof(sign_csr_buf), "%s/%s",
			 output_path, algo_host_csr);
		snprintf(sign_out_buf, sizeof(sign_out_buf), "%s/%s",
			 output_path, algo_host_cert);
		final_key_path = sign_key_buf;
		final_csr_path = sign_csr_buf;
		final_out_path = sign_out_buf;
	} else if (cn) {
		if (!cn_name_valid(cn)) {
			fprintf(stderr,
				"Error: invalid CN '%s' (allowed: [A-Za-z0-9._-], no spaces, no \"..\"); example: -n My_SM2_Root_CA\n",
				cn);
			return 1;
		}
		char cn_dir[512];
		snprintf(cn_dir, sizeof(cn_dir), "%s%s", DEFAULT_CERT_DIR, cn);
		if (mkdir_path(cn_dir) != 0) {
			fprintf(stderr,
				"Error: failed to create output directory: %s\n",
				cn_dir);
			return 1;
		}
		snprintf(sign_key_buf, sizeof(sign_key_buf), "%s/%s", cn_dir,
			 algo_host_key);
		snprintf(sign_csr_buf, sizeof(sign_csr_buf), "%s/%s", cn_dir,
			 algo_host_csr);
		snprintf(sign_out_buf, sizeof(sign_out_buf), "%s/%s", cn_dir,
			 algo_host_cert);
		final_key_path = sign_key_buf;
		final_csr_path = sign_csr_buf;
		final_out_path = sign_out_buf;
	} else {
		/* T0401：默认输出到 DEFAULT_CERT_DIR，目录可能不存在，先创建 */
		if (mkdir_path(DEFAULT_CERT_DIR) != 0) {
			fprintf(stderr,
				"Error: failed to create default cert directory: %s\n",
				DEFAULT_CERT_DIR);
			return 1;
		}
		snprintf(sign_key_buf, sizeof(sign_key_buf), "%s%s",
			 DEFAULT_CERT_DIR, algo_host_key);
		snprintf(sign_csr_buf, sizeof(sign_csr_buf), "%s%s",
			 DEFAULT_CERT_DIR, algo_host_csr);
		snprintf(sign_out_buf, sizeof(sign_out_buf), "%s%s",
			 DEFAULT_CERT_DIR, algo_host_cert);
		final_key_path = key_path ? key_path : sign_key_buf;
		final_csr_path = csr_path ? csr_path : sign_csr_buf;
		final_out_path = out_path ? out_path : sign_out_buf;
	}

	char default_ca_cert[512];
	char default_ca_key[512];
	snprintf(default_ca_cert, sizeof(default_ca_cert), "%s%s",
		 DEFAULT_CERT_DIR, algo_ca_cert);
	snprintf(default_ca_key, sizeof(default_ca_key), "%s%s",
		 DEFAULT_CERT_DIR, algo_ca_key);
	char *final_ca_cert = ca_cert_path ? ca_cert_path : default_ca_cert;
	char *final_ca_key = ca_key_path ? ca_key_path : default_ca_key;

	int ret = tls_keygen_sign_with_algo(final_ca_cert, final_ca_key,
					     final_key_path, final_csr_path,
					     final_out_path, force, days,
					     algo, san_value);
	if (ret != TLS_KEYGEN_OK) {
		fprintf(stderr,
			"Error: failed to sign certificate: %s (code: %d)\n",
			tls_keygen_errmsg(ret), ret);
		return 1;
	}

	/* T0388: -n 自包含目录场景把 CA 证书一并拷入 <cn>/ 目录，
	 * 使客户端可按 cert_dir/<ca_cn>/ 布局直接取用三件套 */
	if (cn) {
		char ca_dst[512];
		snprintf(ca_dst, sizeof(ca_dst), "%s%s/%s", DEFAULT_CERT_DIR,
			 cn, keygen_ca_cert_file(algo));
		FILE *src = fopen(final_ca_cert, "r");
		if (!src) {
			fprintf(stderr,
				"Warning: failed to read CA cert for copy: %s\n",
				final_ca_cert);
			return 0;
		}
		FILE *dst = fopen(ca_dst, "w");
		if (!dst) {
			fclose(src);
			fprintf(stderr,
				"Warning: failed to write CA cert copy: %s\n",
				ca_dst);
			return 0;
		}
		char buf[4096];
		size_t n;
		while ((n = fread(buf, 1, sizeof(buf), src)) > 0)
			fwrite(buf, 1, n, dst);
		fclose(src);
		fclose(dst);
		printf("CA certificate copied: %s\n", ca_dst);
	}

	return 0;
}

static void print_inspect_usage(const char *prog)
{
	printf("Usage: %s inspect <file> [OPTIONS]\n", prog);
	printf("Show details of a certificate (PEM) or private key (PEM).\n");
	printf("Options:\n");
	printf("      --key             Force treat file as a private key\n");
	printf("      --cert            Force treat file as a certificate\n");
	printf("  -h, --help            Show this help message\n");
	printf("\nExamples:\n");
	printf("  # Inspect a host certificate\n");
	printf("  %s inspect host.crt\n", prog);
	printf("  # Inspect a private key\n");
	printf("  %s inspect --key host.key\n", prog);
	printf("  # Inspect an SM2 certificate\n");
	printf("  %s inspect sm2_host.crt\n", prog);
}

static const char *key_type_name(const EVP_PKEY *pkey)
{
	if (!pkey) {
		return "Unknown";
	}
	int base_id = EVP_PKEY_get_base_id(pkey);
	switch (base_id) {
	case EVP_PKEY_ED25519:
		return "Ed25519";
	case EVP_PKEY_RSA:
		return "RSA";
	case EVP_PKEY_EC:
		/* SM2 在 OpenSSL 中 base_id 为 0（未登记独立 type），
		 * 需按 curve group 名区分 SM2 与普通 EC */
	{
		char group[64] = { 0 };
		if (EVP_PKEY_get_group_name(pkey, group, sizeof(group), NULL) >
		    0) {
			if (strcmp(group, "SM2") == 0) {
				return "SM2 (curveSM2)";
			}
			return "EC";
		}
		return "EC";
	}
	default:
		/* SM2 base_id 可能为 0，按曲线名兜底 */
	{
		char group[64] = { 0 };
		if (EVP_PKEY_get_group_name(pkey, group, sizeof(group), NULL) >
		    0 && strcmp(group, "SM2") == 0) {
			return "SM2 (curveSM2)";
		}
		return "Unknown";
	}
	}
}

static int inspect_key_file(const char *path)
{
	FILE *fp = fopen(path, "r");
	if (!fp) {
		fprintf(stderr, "Error: cannot open key file: %s\n", path);
		return 1;
	}
	EVP_PKEY *pkey = PEM_read_PrivateKey(fp, NULL, NULL, NULL);
	fclose(fp);
	if (!pkey) {
		fprintf(stderr, "Error: not a valid PEM private key: %s\n",
			path);
		dump_openssl_errors("inspect key parse");
		return 1;
	}

	int bits = EVP_PKEY_get_bits(pkey);
	printf("=== Private Key ===\n");
	printf("Type:         %s\n", key_type_name(pkey));
	printf("Bits:         %d\n", bits);
	printf("File:         %s\n", path);

	EVP_PKEY_free(pkey);
	return 0;
}

static int inspect_cert_file(const char *path)
{
	FILE *fp = fopen(path, "r");
	if (!fp) {
		fprintf(stderr, "Error: cannot open certificate file: %s\n",
			path);
		return 1;
	}
	X509 *cert = PEM_read_X509(fp, NULL, NULL, NULL);
	fclose(fp);
	if (!cert) {
		fprintf(stderr,
			"Error: not a valid PEM certificate: %s\n", path);
		dump_openssl_errors("inspect cert parse");
		return 1;
	}

	EVP_PKEY *pkey = X509_get_pubkey(cert);
	char subject[256], issuer[256];
	X509_NAME_oneline(X509_get_subject_name(cert), subject,
			  sizeof(subject));
	X509_NAME_oneline(X509_get_issuer_name(cert), issuer, sizeof(issuer));

	const ASN1_INTEGER *serial = X509_get0_serialNumber(cert);
	BIGNUM *bn = ASN1_INTEGER_to_BN(serial, NULL);
	char *serial_hex = bn ? BN_bn2hex(bn) : NULL;
	BN_free(bn);

	const ASN1_TIME *not_before = X509_get0_notBefore(cert);
	const ASN1_TIME *not_after = X509_get0_notAfter(cert);
	char nb_buf[32] = { 0 }, na_buf[32] = { 0 };
	struct tm nb_tm, na_tm;
	if (ASN1_TIME_to_tm(not_before, &nb_tm) == 1) {
		strftime(nb_buf, sizeof(nb_buf), "%Y-%m-%d %H:%M:%S", &nb_tm);
	}
	if (ASN1_TIME_to_tm(not_after, &na_tm) == 1) {
		strftime(na_buf, sizeof(na_buf), "%Y-%m-%d %H:%M:%S", &na_tm);
	}

	int sig_nid = X509_get_signature_nid(cert);
	int key_bits = pkey ? EVP_PKEY_get_bits(pkey) : 0;

	printf("=== Certificate ===\n");
	printf("Subject:      %s\n", subject);
	printf("Issuer:       %s\n", issuer);
	printf("Serial:       %s\n", serial_hex ? serial_hex : "(none)");
	printf("Not Before:   %s\n", nb_buf);
	printf("Not After:    %s\n", na_buf);
	printf("Signature:    %s\n", OBJ_nid2ln(sig_nid));
	printf("Pubkey Type:  %s (%d bits)\n", key_type_name(pkey),
	       key_bits);

	/* T3973: SAN 是客户端 hostname/IP 校验的唯一依据（RFC 6125），
	 * 缺失时显式告警，避免部署后握手期才暴露 */
	{
		GENERAL_NAMES *names = X509_get_ext_d2i(
			cert, NID_subject_alt_name, NULL, NULL);
		if (!names) {
			printf("SAN:          (none)\n");
			printf("Warning:      no subjectAltName; modern TLS clients will fail hostname/IP verification\n");
		} else {
			int n = sk_GENERAL_NAME_num(names);
			printf("SAN (%d):     ", n);
			for (int i = 0; i < n; i++) {
				const GENERAL_NAME *gn =
					sk_GENERAL_NAME_value(names, i);
				if (i > 0) {
					printf(", ");
				}
				if (gn->type == GEN_DNS) {
					printf("DNS:%.*s",
					       ASN1_STRING_length(gn->d.dNSName),
					       ASN1_STRING_get0_data(gn->d.dNSName));
				} else if (gn->type == GEN_IPADD) {
					int ip_len =
						ASN1_STRING_length(gn->d.iPAddress);
					const unsigned char *ip =
					    ASN1_STRING_get0_data(gn->d.iPAddress);
					char ipbuf[INET6_ADDRSTRLEN] = { 0 };
					if (ip_len == 4 &&
					    inet_ntop(AF_INET, ip, ipbuf,
						      sizeof(ipbuf))) {
						printf("IP:%s", ipbuf);
					} else if (ip_len == 16 &&
						   inet_ntop(AF_INET6, ip,
							     ipbuf,
							     sizeof(ipbuf))) {
						printf("IP:%s", ipbuf);
					} else {
						printf("IP:<invalid>");
					}
				} else {
					printf("<unsupported type %d>",
					       gn->type);
				}
			}
			printf("\n");
			GENERAL_NAMES_free(names);
		}
	}

	if (pkey) {
		EVP_PKEY_free(pkey);
	}
	if (serial_hex) {
		OPENSSL_free(serial_hex);
	}
	X509_free(cert);
	return 0;
}

static int handle_inspect(int argc, char *argv[])
{
	const char *path = NULL;
	int force_key = 0, force_cert = 0;

	static struct option long_options[] = {
		{ "key", no_argument, 0, 2001 },
		{ "cert", no_argument, 0, 2002 },
		{ "help", no_argument, 0, 'h' },
		{ 0, 0, 0, 0 }
	};

	int opt;
	while ((opt = getopt_long(argc, argv, "h", long_options, NULL)) != -1) {
		switch (opt) {
		case 2001:
			force_key = 1;
			break;
		case 2002:
			force_cert = 1;
			break;
		case 'h':
			print_inspect_usage("tls-keygen");
			return 0;
		default:
			break;
		}
	}

	if (optind >= argc) {
		fprintf(stderr, "Error: inspect requires a file argument\n");
		print_inspect_usage("tls-keygen");
		return 1;
	}
	path = argv[optind];

	/* 默认自动识别：先尝试证书，再尝试密钥（PEM 头区分） */
	if (!force_key && !force_cert) {
		char buf[128];
		FILE *fp = fopen(path, "r");
		if (fp && fgets(buf, sizeof(buf), fp)) {
			fclose(fp);
			if (strncmp(buf, "-----BEGIN CERTIFICATE",
				    strlen("-----BEGIN CERTIFICATE")) == 0) {
				return inspect_cert_file(path);
			}
			if (strncmp(buf, "-----BEGIN PRIVATE KEY",
				    strlen("-----BEGIN PRIVATE KEY")) == 0 ||
			    strncmp(buf, "-----BEGIN EC PRIVATE KEY",
				    strlen("-----BEGIN EC PRIVATE KEY")) == 0) {
				return inspect_key_file(path);
			}
		}
	}

	if (force_key) {
		return inspect_key_file(path);
	}
	if (force_cert) {
		return inspect_cert_file(path);
	}

	fprintf(stderr,
		"Error: unrecognized PEM type in %s (use --cert or --key)\n",
		path);
	return 1;
}

static void print_mtls_usage(const char *prog)
{
	printf("Usage: %s mtls [OPTIONS]\n", prog);
	printf("Self-test: verify an mTLS handshake between two certificates\n"
	       "over an in-memory BIO pair (no network listener).\n");
	printf("Options:\n");
	printf("      --ca <path>          CA certificate for chain verify\n");
	printf("      --server-cert <path> Server certificate\n");
	printf("      --server-key <path>  Server private key\n");
	printf("      --client-cert <path> Client certificate\n");
	printf("      --client-key <path>  Client private key\n");
	printf("      --ciphers <list>     Ciphersuites (default: TLS1.3 default)\n");
	printf("  -h, --help            Show this help message\n");
	printf("\nOutput files use algorithm prefix: {algo}_host.key, {algo}_host.csr, {algo}_host.crt\n");
	printf("\nExamples:\n");
	printf("  # Ed25519 mTLS handshake test\n");
	printf("  %s mtls --ca ca.crt --server-cert host.crt --server-key host.key\n"
	       "             --client-cert host.crt --client-key host.key\n", prog);
	printf("  # SM2 mTLS handshake test with national ciphersuite\n");
	printf("  %s mtls --ca sm2_ca.crt --server-cert sm2_host.crt --server-key sm2_host.key\n"
	       "             --client-cert sm2_host.crt --client-key sm2_host.key\n"
	       "             --ciphers TLS_SM4_GCM_SM3\n", prog);
}

/* 按角色构建 mTLS SSL_CTX：is_server 时要求并校验客户端证书 */
static SSL_CTX *mtls_build_ctx(const char *ca, const char *cert,
			       const char *key, const char *ciphers,
			       int is_server)
{
	SSL_CTX *ctx = SSL_CTX_new(TLS_method());
	if (!ctx) {
		dump_openssl_errors("mtls ctx");
		return NULL;
	}
	SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION);

	if (SSL_CTX_load_verify_locations(ctx, ca, NULL) != 1) {
		fprintf(stderr, "mtls: cannot load CA: %s\n", ca);
		dump_openssl_errors("mtls load ca");
		SSL_CTX_free(ctx);
		return NULL;
	}
	if (SSL_CTX_use_certificate_chain_file(ctx, cert) != 1 ||
	    SSL_CTX_use_PrivateKey_file(ctx, key, SSL_FILETYPE_PEM) != 1) {
		fprintf(stderr, "mtls: cannot load cert/key (%s / %s)\n",
			cert, key);
		dump_openssl_errors("mtls load cert");
		SSL_CTX_free(ctx);
		return NULL;
	}

	if (ciphers && ciphers[0]) {
		if (SSL_CTX_set_ciphersuites(ctx, ciphers) != 1) {
			fprintf(stderr, "mtls: cannot set ciphersuites '%s'\n",
				ciphers);
			dump_openssl_errors("mtls ciphersuites");
			SSL_CTX_free(ctx);
			return NULL;
		}
	}

	/* mTLS：服务端要求并校验客户端证书；客户端校验服务端证书 */
	SSL_CTX_set_verify(ctx,
			   SSL_VERIFY_PEER |
				   (is_server ? SSL_VERIFY_FAIL_IF_NO_PEER_CERT
					     : 0),
			   NULL);
	return ctx;
}

/* 内存 BIO pair 推进双向握手，返回 0 成功 */
static int mtls_do_test(const char *ca, const char *server_cert,
			const char *server_key, const char *client_cert,
			const char *client_key, const char *ciphers)
{
	SSL_CTX *server_ctx =
		mtls_build_ctx(ca, server_cert, server_key, ciphers, 1);
	if (!server_ctx) {
		return 1;
	}
	SSL_CTX *client_ctx =
		mtls_build_ctx(ca, client_cert, client_key, ciphers, 0);
	if (!client_ctx) {
		SSL_CTX_free(server_ctx);
		return 1;
	}

	/* 内存 BIO 对：把客户端、服务端 SSL 端点接到同一对缓冲 */
	BIO *cbio = NULL, *sbio = NULL;
	if (BIO_new_bio_pair(&cbio, 0, &sbio, 0) != 1) {
		fprintf(stderr, "mtls: cannot create BIO pair\n");
		SSL_CTX_free(server_ctx);
		SSL_CTX_free(client_ctx);
		return 1;
	}

	SSL *c_ssl = SSL_new(client_ctx);
	SSL *s_ssl = SSL_new(server_ctx);
	if (!c_ssl || !s_ssl) {
		SSL_free(c_ssl);
		SSL_free(s_ssl);
		BIO_free(cbio);
		BIO_free(sbio);
		SSL_CTX_free(server_ctx);
		SSL_CTX_free(client_ctx);
		return 1;
	}
	SSL_set_bio(c_ssl, cbio, cbio);
	SSL_set_bio(s_ssl, sbio, sbio);
	SSL_set_connect_state(c_ssl);
	SSL_set_accept_state(s_ssl);

	/* 交替推进双方握手直至完成（内存 BIO 同步推进） */
	int rounds = 0;
	while (rounds++ < 100) {
		int rc = SSL_do_handshake(c_ssl);
		int rs = SSL_do_handshake(s_ssl);
		int ec = rc == 1 ? SSL_ERROR_NONE : SSL_get_error(c_ssl, rc);
		int es = rs == 1 ? SSL_ERROR_NONE : SSL_get_error(s_ssl, rs);
		if (rc == 1 && rs == 1) {
			break;
		}
		/* 任何一方实质失败即终止（仅接受 WANT_READ/WANT_WRITE 推进） */
		if (rc != 1 && ec != SSL_ERROR_WANT_READ &&
		    ec != SSL_ERROR_WANT_WRITE) {
			fprintf(stderr, "mtls: client handshake error: %s\n",
				SSL_state_string_long(c_ssl));
			dump_openssl_errors("mtls client handshake");
			SSL_free(c_ssl);
			SSL_free(s_ssl);
			SSL_CTX_free(server_ctx);
			SSL_CTX_free(client_ctx);
			return 1;
		}
		if (rs != 1 && es != SSL_ERROR_WANT_READ &&
		    es != SSL_ERROR_WANT_WRITE) {
			fprintf(stderr, "mtls: server handshake error: %s\n",
				SSL_state_string_long(s_ssl));
			dump_openssl_errors("mtls server handshake");
			SSL_free(c_ssl);
			SSL_free(s_ssl);
			SSL_CTX_free(server_ctx);
			SSL_CTX_free(client_ctx);
			return 1;
		}
	}

	if (!SSL_is_init_finished(c_ssl) || !SSL_is_init_finished(s_ssl)) {
		fprintf(stderr, "mtls: handshake did not complete\n");
		SSL_free(c_ssl);
		SSL_free(s_ssl);
		SSL_CTX_free(server_ctx);
		SSL_CTX_free(client_ctx);
		return 1;
	}

	const SSL_CIPHER *ciph = SSL_get_current_cipher(c_ssl);
	printf("mtls: handshake OK\n");
	printf("mtls: negotiated cipher = %s\n",
	       ciph ? SSL_CIPHER_get_name(ciph) : "(unknown)");

	/* 服务端 FAIL_IF_NO_PEER_CERT：确认已收到并校验客户端证书 */
	X509 *peer_cert = SSL_get1_peer_certificate(s_ssl);
	if (!peer_cert) {
		fprintf(stderr,
			"mtls: server did not receive client certificate\n");
		SSL_free(c_ssl);
		SSL_free(s_ssl);
		SSL_CTX_free(server_ctx);
		SSL_CTX_free(client_ctx);
		return 1;
	}
	X509_free(peer_cert);

	SSL_free(c_ssl);
	SSL_free(s_ssl);
	SSL_CTX_free(server_ctx);
	SSL_CTX_free(client_ctx);
	printf("mtls: mTLS self-test PASSED\n");
	return 0;
}

static int handle_mtls(int argc, char *argv[])
{
	const char *ca = NULL;
	const char *server_cert = NULL, *server_key = NULL;
	const char *client_cert = NULL, *client_key = NULL;
	const char *ciphers = NULL;

	static struct option long_options[] = {
		{ "ca", required_argument, 0, 2001 },
		{ "server-cert", required_argument, 0, 2002 },
		{ "server-key", required_argument, 0, 2003 },
		{ "client-cert", required_argument, 0, 2004 },
		{ "client-key", required_argument, 0, 2005 },
		{ "ciphers", required_argument, 0, 2006 },
		{ "help", no_argument, 0, 'h' },
		{ 0, 0, 0, 0 }
	};

	int opt;
	while ((opt = getopt_long(argc, argv, "h", long_options, NULL)) != -1) {
		switch (opt) {
		case 2001:
			ca = optarg;
			break;
		case 2002:
			server_cert = optarg;
			break;
		case 2003:
			server_key = optarg;
			break;
		case 2004:
			client_cert = optarg;
			break;
		case 2005:
			client_key = optarg;
			break;
		case 2006:
			ciphers = optarg;
			break;
		case 'h':
			print_mtls_usage("tls-keygen");
			return 0;
		default:
			break;
		}
	}

	if (!ca || !server_cert || !server_key || !client_cert ||
	    !client_key) {
		fprintf(stderr,
			"Error: mtls requires --ca, --server-cert, --server-key, --client-cert, --client-key\n");
		print_mtls_usage("tls-keygen");
		return 1;
	}

	printf("mtls: CA=%s\n", ca);
	printf("mtls: server=%s / client=%s\n", server_cert, client_cert);
	return mtls_do_test(ca, server_cert, server_key, client_cert,
			   client_key, ciphers);
}


int main(int argc, char *argv[])
{
	if (argc < 2) {
		print_global_help(argv[0]);
		return 1;
	}

	/* 全局 --verbose/-V：任何位置出现即开启详细错误输出
	 * （-v 保留给 --version，避免破坏存量行为） */
	for (int i = 1; i < argc; i++) {
		if (strcmp(argv[i], "--verbose") == 0 ||
		    strcmp(argv[i], "-V") == 0) {
			g_verbose = 1;
			break;
		}
	}

	/* 若首参为 -V/--verbose，从 argv[2] 起解析子命令与参数 */
	int verbose_shift = 0;
	if (strcmp(argv[1], "--verbose") == 0 ||
	    strcmp(argv[1], "-V") == 0) {
		verbose_shift = 1;
	}

	// Check for global options before subcommand
	if (strcmp(argv[1], "--version") == 0 || strcmp(argv[1], "-v") == 0) {
		printf("%s\n", TLS_KEYGEN_VERSION);
		return 0;
	}

	if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
		print_global_help(argv[0]);
		return 0;
	}

	if (verbose_shift && argc < 3) {
		print_global_help(argv[0]);
		return 1;
	}

	// Parse subcommand
	const char *subcmd = argv[1 + verbose_shift];
	int subcommand;

	if (strcmp(subcmd, "create") == 0) {
		subcommand = CMD_CREATE;
	} else if (strcmp(subcmd, "ca") == 0) {
		subcommand = CMD_CA;
	} else if (strcmp(subcmd, "sign") == 0) {
		subcommand = CMD_SIGN;
	} else if (strcmp(subcmd, "inspect") == 0) {
		subcommand = CMD_INSPECT;
	} else if (strcmp(subcmd, "mtls") == 0) {
		subcommand = CMD_MTLS;
	} else {
		fprintf(stderr, "Error: unknown subcommand '%s'\n", subcmd);
		print_global_help(argv[0]);
		return 1;
	}

	// Route to handler
	int handler_argc = argc - 1 - verbose_shift;
	char **handler_argv = &argv[1 + verbose_shift];

	switch (subcommand) {
	case CMD_CREATE:
		return handle_create(handler_argc, handler_argv);
	case CMD_CA:
		return handle_ca(handler_argc, handler_argv);
	case CMD_SIGN:
		return handle_sign(handler_argc, handler_argv);
	case CMD_INSPECT:
		return handle_inspect(handler_argc, handler_argv);
	case CMD_MTLS:
		return handle_mtls(handler_argc, handler_argv);
	default:
		print_global_help(argv[0]);
		return 1;
	}
}

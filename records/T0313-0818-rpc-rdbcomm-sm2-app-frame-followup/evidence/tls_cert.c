#include "tls_cert.h"
#include "common.h"
#include "logger.h"
#include "rdb-config.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <dirent.h>
#include <openssl/err.h>
#include <openssl/tls1.h>
#include <openssl/x509.h>
#include <openssl/pem.h>
#include <arpa/inet.h>
#include <netinet/in.h>

static X509 *get_ca_cert_from_cache(const char *cert_dir, const char *cn);
static int get_host_cert_from_cache(const char *cert_dir, const char *cn,
				    X509 **cert, EVP_PKEY **pkey);

/* 校验 cn 是否可作为单级目录名：拒绝路径分隔符与相对路径片段 */
static int is_safe_dir_component(const char *cn)
{
	if (!cn || !cn[0] || strlen(cn) > 200) {
		return 0;
	}
	for (const char *p = cn; *p; p++) {
		if (*p == '/' || *p == '\\') {
			return 0;
		}
	}
	if (strcmp(cn, ".") == 0 || strcmp(cn, "..") == 0) {
		return 0;
	}
	return 1;
}

static const char *get_config_value(const char *env_var,
				    const char *config_value,
				    const char *default_value)
{
	const char *env = getenv(env_var);
	if (env && env[0] != '\0') {
		return env;
	}
	if (config_value && config_value[0] != '\0') {
		return config_value;
	}
	return default_value;
}

struct tls_cert_ctx {
	SSL_CTX *ssl_ctx;
	char *hostname;
	char last_error[256];
	char *cert_dir;
};

static tls_cert_ctx_t *g_ctx = NULL;

static void tls_cert_log_ssl_errors(const char *where, int ssl_error)
{
	unsigned long error;
	char message[256];
	ErrorLog("TLS handshake failed at %s: ssl_error=%d", where,
		 ssl_error);
	while ((error = ERR_get_error()) != 0) {
		ERR_error_string_n(error, message, sizeof(message));
		ErrorLog("TLS OpenSSL error: %s", message);
	}
}

// CA 证书缓存：CN -> CA 证书
typedef struct {
	char cn[256];
	X509 *ca_cert;
} ca_cache_entry_t;

static ca_cache_entry_t g_cc[64];
static int g_ccc = 0;
static pthread_rwlock_t g_ca_cache_lock = PTHREAD_RWLOCK_INITIALIZER;

// Host 证书缓存：CN -> 证书+私钥
typedef struct {
	char cn[256];
	X509 *cert;
	EVP_PKEY *pkey;
} host_cert_cache_entry_t;

static host_cert_cache_entry_t g_hcc[32];
static int g_hccc = 0;
static pthread_rwlock_t g_host_cert_cache_lock = PTHREAD_RWLOCK_INITIALIZER;

int tls_cert_init_from_env(void)
{
	return tls_cert_init_client();
}

static const char *get_local_host_id(void)
{
	static char host_id[256];
	FILE *fp = fopen(HOST_ID_FILE, "r");
	if (!fp) {
		return NULL;
	}
	if (!fgets(host_id, sizeof(host_id), fp)) {
		fclose(fp);
		return NULL;
	}
	fclose(fp);

	size_t len = strlen(host_id);
	while (len > 0 &&
	       (host_id[len - 1] == '\n' || host_id[len - 1] == '\r')) {
		host_id[--len] = '\0';
	}

	if (len == 0) {
		return NULL;
	}

	return host_id;
}

static const char *get_checkname(void)
{
	const char *env = getenv("RPC_TLS_CHECK_NAME");
	if (env && env[0] != '\0') {
		return env;
	}

	return get_local_host_id();
}

int tls_cert_verify_is_local_x509(X509 *cert)
{
	const char *checkname = get_checkname();
	if (!checkname) {
		return TLS_CERT_ERR_NO_CONFIG;
	}

	if (!cert) {
		return TLS_CERT_ERR_NO_CERT;
	}

	// 获取证书 Subject Name
	// 注：OpenSSL 4 中 X509_get_subject_name 返回 const 指针
	const X509_NAME *subject = X509_get_subject_name(cert);
	if (!subject) {
		return TLS_CERT_ERR_NO_CERT;
	}

	// 提取 CN
	char cert_cn[256];
	if (X509_NAME_get_text_by_NID(subject, NID_commonName, cert_cn,
				      sizeof(cert_cn)) <= 0) {
		return TLS_CERT_ERR_NO_CERT;
	}

	// 比较 CN 与 checkname（区分大小写）
	if (strcmp(cert_cn, checkname) == 0) {
		return TLS_CERT_IS_LOCAL;
	}

	return TLS_CERT_NOT_LOCAL;
}

int __attribute__((unused)) tls_cert_verify_is_local(const char *cert_file)
{
	const char *checkname = get_checkname();
	if (!checkname) {
		return TLS_CERT_ERR_NO_CONFIG;
	}

	if (!cert_file || cert_file[0] == '\0') {
		return TLS_CERT_ERR_LOAD;
	}

	// 从文件加载证书
	FILE *fp = fopen(cert_file, "r");
	if (!fp) {
		return TLS_CERT_ERR_LOAD;
	}

	X509 *cert = PEM_read_X509(fp, NULL, NULL, NULL);
	fclose(fp);

	if (!cert) {
		return TLS_CERT_ERR_LOAD;
	}

	int result = tls_cert_verify_is_local_x509(cert);
	X509_free(cert);

	return result;
}

static int tls_cert_select_cert_callback(SSL *ssl, void *arg)
{
	tls_cert_ctx_t *ctx = (tls_cert_ctx_t *)arg;

	if (!ctx || !ctx->cert_dir || !ctx->cert_dir[0]) {
		return 1;
	}

	STACK_OF(X509_NAME) *ca_names = SSL_get_client_CA_list(ssl);
	if (!ca_names || sk_X509_NAME_num(ca_names) == 0) {
		return 1;
	}

	/* 遍历 server 下发的 CA 列表，匹配本目录下对应 CA 证书目录的 host 证书 */
	for (int i = 0; i < sk_X509_NAME_num(ca_names); i++) {
		X509_NAME *ca_name = sk_X509_NAME_value(ca_names, i);
		char ca_cn[256];
		if (X509_NAME_get_text_by_NID(ca_name, NID_commonName, ca_cn,
					      sizeof(ca_cn)) <= 0) {
			continue;
		}

		X509 *client_cert = NULL;
		EVP_PKEY *client_pkey = NULL;

		if (get_host_cert_from_cache(ctx->cert_dir, ca_cn,
					     &client_cert, &client_pkey) != 0) {
			continue;
		}

		X509 *client_cert_dup =
			client_cert ? X509_dup(client_cert) : NULL;
		EVP_PKEY *client_pkey_dup = client_pkey ?
						    EVP_PKEY_dup(client_pkey) :
						    NULL;

		if (SSL_use_certificate(ssl, client_cert_dup) != 1) {
			X509_free(client_cert_dup);
			EVP_PKEY_free(client_pkey_dup);
			continue;
		}

		if (SSL_use_PrivateKey(ssl, client_pkey_dup) != 1) {
			X509_free(client_cert_dup);
			EVP_PKEY_free(client_pkey_dup);
			continue;
		}

		// if (tls_cert_verify_is_local(cert_path) != TLS_CERT_IS_LOCAL) {
		// 	return 0;
		// }

		return 1;
	}

	return 0;
}

static X509 *load_ca_to_cache(const char *cert_dir, const char *cn)
{
	if (!is_safe_dir_component(cn)) {
		return NULL;
	}

	char ca_path[512];
	snprintf(ca_path, sizeof(ca_path), "%s%s/%s", cert_dir, cn,
		 CERT_FILE_CA);

	if (access(ca_path, F_OK) != 0) {
		return NULL;
	}

	X509 *ca_cert = NULL;
	BIO *bio = BIO_new_file(ca_path, "r");
	if (!bio)
		return NULL;

	ca_cert = PEM_read_bio_X509(bio, NULL, NULL, NULL);
	BIO_free(bio);

	return ca_cert;
}

static X509 *get_ca_cert_from_cache(const char *cert_dir, const char *cn)
{
	pthread_rwlock_rdlock(&g_ca_cache_lock);
	for (int i = 0; i < g_ccc; i++) {
		if (strcmp(g_cc[i].cn, cn) == 0) {
			X509 *cert = g_cc[i].ca_cert;
			pthread_rwlock_unlock(&g_ca_cache_lock);
			return cert;
		}
	}
	pthread_rwlock_unlock(&g_ca_cache_lock);

	pthread_rwlock_wrlock(&g_ca_cache_lock);
	for (int i = 0; i < g_ccc; i++) {
		if (strcmp(g_cc[i].cn, cn) == 0) {
			X509 *cert = g_cc[i].ca_cert;
			pthread_rwlock_unlock(&g_ca_cache_lock);
			return cert;
		}
	}

	X509 *ca_cert = load_ca_to_cache(cert_dir, cn);
	if (ca_cert) {
		if (g_ccc < 64) {
			memcpy(g_cc[g_ccc].cn, cn, 255);
			g_cc[g_ccc].cn[255] = '\0';
			g_cc[g_ccc].ca_cert = ca_cert;
			g_ccc++;
		} else {
			InfoLog("CA cert cache full, using uncached cert for %s",
				cn);
		}
	}

	pthread_rwlock_unlock(&g_ca_cache_lock);
	return ca_cert;
}

static int load_host_cert_to_cache(const char *cert_dir, const char *cn,
				   X509 **cert, EVP_PKEY **pkey)
{
	if (!is_safe_dir_component(cn)) {
		return -1;
	}

	char cert_path[512];
	char key_path[512];
	snprintf(cert_path, sizeof(cert_path), "%s%s/%s", cert_dir, cn,
		 CERT_FILE_HOST);
	snprintf(key_path, sizeof(key_path), "%s%s/%s", cert_dir, cn,
		 CERT_FILE_HOST_KEY);

	if (access(cert_path, F_OK) != 0 || access(key_path, F_OK) != 0) {
		return -1;
	}

	X509 *client_cert = NULL;
	EVP_PKEY *client_pkey = NULL;

	BIO *bio = BIO_new_file(cert_path, "r");
	if (!bio)
		return -1;
	client_cert = PEM_read_bio_X509(bio, NULL, NULL, NULL);
	BIO_free(bio);
	if (!client_cert)
		return -1;

	bio = BIO_new_file(key_path, "r");
	if (!bio) {
		X509_free(client_cert);
		return -1;
	}
	client_pkey = PEM_read_bio_PrivateKey(bio, NULL, NULL, NULL);
	BIO_free(bio);
	if (!client_pkey) {
		X509_free(client_cert);
		return -1;
	}

	*cert = client_cert;
	*pkey = client_pkey;
	return 0;
}

static int get_host_cert_from_cache(const char *cert_dir, const char *cn,
				    X509 **cert, EVP_PKEY **pkey)
{
	pthread_rwlock_rdlock(&g_host_cert_cache_lock);
	for (int i = 0; i < g_hccc; i++) {
		if (strcmp(g_hcc[i].cn, cn) == 0) {
			*cert = g_hcc[i].cert;
			*pkey = g_hcc[i].pkey;
			pthread_rwlock_unlock(&g_host_cert_cache_lock);
			return 0;
		}
	}
	pthread_rwlock_unlock(&g_host_cert_cache_lock);

	pthread_rwlock_wrlock(&g_host_cert_cache_lock);
	for (int i = 0; i < g_hccc; i++) {
		if (strcmp(g_hcc[i].cn, cn) == 0) {
			*cert = g_hcc[i].cert;
			*pkey = g_hcc[i].pkey;
			pthread_rwlock_unlock(&g_host_cert_cache_lock);
			return 0;
		}
	}

	X509 *client_cert = NULL;
	EVP_PKEY *client_pkey = NULL;
	int ret = load_host_cert_to_cache(cert_dir, cn, &client_cert,
					  &client_pkey);

	if (ret == 0) {
		if (g_hccc < 32) {
			memcpy(g_hcc[g_hccc].cn, cn, 255);
			g_hcc[g_hccc].cn[255] = '\0';
			g_hcc[g_hccc].cert = client_cert;
			g_hcc[g_hccc].pkey = client_pkey;
			g_hccc++;
		} else {
			InfoLog("Host cert cache full, using uncached cert for %s",
				cn);
		}
		*cert = client_cert;
		*pkey = client_pkey;
	} else {
		if (client_cert)
			X509_free(client_cert);
		if (client_pkey)
			EVP_PKEY_free(client_pkey);
	}

	pthread_rwlock_unlock(&g_host_cert_cache_lock);
	return ret;
}

static int client_cert_verify_callback(X509_STORE_CTX *x509_ctx, void *arg)
{
	tls_cert_ctx_t *ctx = (tls_cert_ctx_t *)arg;
	if (!ctx || !ctx->cert_dir || !ctx->cert_dir[0]) {
		return X509_verify_cert(x509_ctx);
	}

	STACK_OF(X509) *untrusted = X509_STORE_CTX_get0_untrusted(x509_ctx);
	X509 *cert = untrusted ? sk_X509_value(untrusted, 0) : NULL;
	if (!cert) {
		return X509_verify_cert(x509_ctx);
	}

	// 注：OpenSSL 4 中 X509_get_issuer_name 返回 const 指针
	const X509_NAME *issuer = X509_get_issuer_name(cert);
	if (!issuer) {
		return X509_verify_cert(x509_ctx);
	}

	char server_issuer_cn[256] = { 0 };
	X509_NAME_get_text_by_NID(issuer, NID_commonName, server_issuer_cn,
				  sizeof(server_issuer_cn));
	if (server_issuer_cn[0] == '\0') {
		return X509_verify_cert(x509_ctx);
	}

	X509 *ca_cert = get_ca_cert_from_cache(ctx->cert_dir, server_issuer_cn);
	if (!ca_cert) {
		return X509_verify_cert(x509_ctx);
	}

	X509_STORE *store = X509_STORE_CTX_get0_store(x509_ctx);
	if (store) {
		X509 *ca_cert_dup = X509_dup(ca_cert);
		if (ca_cert_dup) {
			X509_STORE_add_cert(store, ca_cert_dup);
		}
	}

	return X509_verify_cert(x509_ctx);
}

/**
 * tls_cert_set_ciphersuites_from_conf - 按算法参数配置应用 TLS1.3 ciphersuites
 *
 * 配置来源：RPC_TLS_CIPHERSUITES env / [security] ciphersuites（见 sec_tls_ciphersuites）。
 * 未配置时保持 OpenSSL 默认套件列表，确保存量 RSA/ECDSA mTLS 行为不变。
 * 国密示例：RPC_TLS_CIPHERSUITES="TLS_SM4_GCM_SM3:TLS_AES_256_GCM_SHA384"
 */
static void tls_cert_set_ciphersuites_from_conf(SSL_CTX *ctx)
{
	const char *ciphers = sec_tls_ciphersuites();
	if (!ciphers) {
		return;
	}
	if (SSL_CTX_set_ciphersuites(ctx, ciphers) != 1) {
		ErrorLog("Failed to apply ciphersuites config: %s", ciphers);
	} else {
		InfoLog("Applied ciphersuites config: %s", ciphers);
	}
}

/**
 * tls_cert_sm_ciphersuites_configured - 判断是否配置了国密 SM 套件
 *
 * 依据 sec_tls_ciphersuites() 结果是否含 SM 套件名（TLS_SM4_GCM_SM3 等）
 */
static int tls_cert_sm_ciphersuites_configured(void)
{
	const char *ciphers = sec_tls_ciphersuites();
	return ciphers && strstr(ciphers, "TLS_SM") != NULL;
}

/**
 * tls_cert_load_sm2_chain - 加载国密 SM2 证书链到 SSL_CTX
 * @ctx: SSL_CTX
 * @ca_cert: SM2 CA 证书路径
 * @cert: SM2 主机证书路径
 * @key: SM2 主机私钥路径
 *
 * 配置了国密套件时，将 SM2 证书链（sm2_ca.crt / sm2_host.crt / sm2_host.key）
 * 叠加到 SSL_CTX：加载 SM2 主机证书+私钥、设置 SM2 CA 信任链。
 * 任一 SM2 证书缺失或加载失败返回 0（上层按 ENC-005 作业失败，不降级明文）。
 */
static int tls_cert_load_sm2_chain(SSL_CTX *ctx, const char *ca_cert,
				   const char *cert, const char *key)
{
	if (!ca_cert || !cert || !key) {
		return 0;
	}

	/* SM2 主机证书链（host 证书 + 私钥），覆盖同 SSL_CTX 上的普通证书 */
	if (SSL_CTX_use_certificate_chain_file(ctx, cert) != 1 ||
	    SSL_CTX_use_PrivateKey_file(ctx, key, SSL_FILETYPE_PEM) != 1) {
		ErrorLog("Failed to load SM2 host certificate chain (%s/%s)",
			 cert, key);
		return 0;
	}

	/* SM2 CA 信任链：覆盖 verify locations 为 SM2 CA */
	if (SSL_CTX_load_verify_locations(ctx, ca_cert, NULL) != 1) {
		ErrorLog("Failed to load SM2 CA certificate (%s)", ca_cert);
		return 0;
	}

	/* 同步 client_CA_list 为 SM2 CA（server 场景请求客户端证书时下发）。
	 * 否则 client 侧 cert_cb 会依据普通 CA 名找证书，与 SM2 信任链不一致。 */
	STACK_OF(X509_NAME) *sm2_names = SSL_load_client_CA_file(ca_cert);
	if (sm2_names) {
		SSL_CTX_set_client_CA_list(ctx, sm2_names);
	}

	InfoLog("Loaded SM2 certificate chain: ca=%s cert=%s key=%s", ca_cert,
		cert, key);
	return 1;
}

/**
 * tls_cert_apply_sm2_if_configured - 按国密配置决定是否叠加 SM2 证书链
 *
 * 条件：配置了国密 SM 套件（sec_tls_ciphersuites 含 TLS_SM）且启用了 TLS。
 * 未配置国密时返回 1（保持存量证书路径）；配置国密但 SM2 证书链缺失返回 0。
 * 证书路径优先级：RPC_TLS_SM2_CA_CERT / RPC_TLS_SM2_CERT / RPC_TLS_SM2_KEY
 * > 证书目录默认 sm2_ca.crt / sm2_host.crt / sm2_host.key。
 */
static int tls_cert_apply_sm2_if_configured(SSL_CTX *ctx,
					    const char *cert_dir)
{
	if (!tls_cert_sm_ciphersuites_configured()) {
		return 1;
	}

	const char *ca = get_config_value("RPC_TLS_SM2_CA_CERT", NULL,
					  SM2_CA_CERT_PATH);
	const char *cert = get_config_value("RPC_TLS_SM2_CERT", NULL,
					    SM2_HOST_CERT_PATH);
	const char *key = get_config_value("RPC_TLS_SM2_KEY", NULL,
					   SM2_HOST_KEY_PATH);

	/* 显式配置了 SM2 证书路径时按显式路径；否则回退 cert_dir 目录 */
	if (!getenv("RPC_TLS_SM2_CA_CERT") && !getenv("RPC_TLS_SM2_CERT") &&
	    !getenv("RPC_TLS_SM2_KEY") && cert_dir && cert_dir[0]) {
		static char ca_path[1024], cert_path[1024], key_path[1024];
		snprintf(ca_path, sizeof(ca_path), "%s/%s", cert_dir,
			 CERT_FILE_SM2_CA);
		snprintf(cert_path, sizeof(cert_path), "%s/%s", cert_dir,
			 CERT_FILE_SM2_HOST);
		snprintf(key_path, sizeof(key_path), "%s/%s", cert_dir,
			 CERT_FILE_SM2_HOST_KEY);
		ca = ca_path;
		cert = cert_path;
		key = key_path;
	}

	if (!tls_cert_load_sm2_chain(ctx, ca, cert, key)) {
		ErrorLog(
			"SM2 ciphersuites configured but SM2 certificate chain unavailable (ENC-005)");
		return 0;
	}

	return 1;
}

int tls_cert_init_client(void)
{
	if (!sec_tls_enabled()) {
		return TLS_CERT_OK;
	}

	const char *cert_dir = get_config_value("RPC_TLS_CERT_DIR", NULL,
						DEFAULT_CERT_DIR);

	const char *client_ca = get_config_value("RPC_TLS_CA_CERT", NULL, NULL);
	const char *client_cert = get_config_value("RPC_TLS_CLIENT_CERT", NULL,
						   NULL);
	const char *client_key = get_config_value("RPC_TLS_CLIENT_KEY", NULL,
						  NULL);

	g_ctx = malloc(sizeof(tls_cert_ctx_t));
	if (!g_ctx) {
		return TLS_CERT_ERR_INVALID_PARAM;
	}
	memset(g_ctx, 0, sizeof(tls_cert_ctx_t));

	g_ctx->ssl_ctx = SSL_CTX_new(TLS_method());
	if (!g_ctx->ssl_ctx) {
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_SSL_CREATE;
	}

	tls_cert_set_ciphersuites_from_conf(g_ctx->ssl_ctx);

	g_ctx->cert_dir = strdup(cert_dir);
	if (!g_ctx->cert_dir) {
		SSL_CTX_free(g_ctx->ssl_ctx);
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_INVALID_PARAM;
	}
	if (client_ca && client_cert && client_key) {
		if (SSL_CTX_use_certificate_chain_file(g_ctx->ssl_ctx,
						       client_cert) != 1 ||
		    SSL_CTX_use_PrivateKey_file(g_ctx->ssl_ctx, client_key,
						SSL_FILETYPE_PEM) != 1 ||
		    SSL_CTX_load_verify_locations(g_ctx->ssl_ctx, client_ca,
						  NULL) != 1) {
			SSL_CTX_free(g_ctx->ssl_ctx);
			free(g_ctx);
			g_ctx = NULL;
			return TLS_CERT_ERR_LOAD_CERT;
		}
		// if (tls_cert_verify_is_local(client_cert) !=
		//     TLS_CERT_IS_LOCAL) {
		//      ErrorLog(
		//              "Client certificate CN does not match local host ID");
		//      SSL_CTX_free(g_ctx->ssl_ctx);
		//      free(g_ctx);
		//      g_ctx = NULL;
		//      return TLS_CERT_ERR_INVALID_PARAM;
		// }
	} else {
		SSL_CTX_set_cert_cb(g_ctx->ssl_ctx,
				    tls_cert_select_cert_callback, g_ctx);
		SSL_CTX_set_cert_verify_callback(
			g_ctx->ssl_ctx, client_cert_verify_callback, g_ctx);
	}

	SSL_CTX_set_verify(g_ctx->ssl_ctx,
			   SSL_VERIFY_PEER | SSL_VERIFY_CLIENT_ONCE |
				   SSL_VERIFY_FAIL_IF_NO_PEER_CERT,
			   NULL);

	/* 配置国密套件时叠加 SM2 证书链（ENC-005：缺失则失败，不降级明文） */
	if (!tls_cert_apply_sm2_if_configured(g_ctx->ssl_ctx,
					      g_ctx->cert_dir)) {
		SSL_CTX_free(g_ctx->ssl_ctx);
		free(g_ctx->cert_dir);
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_LOAD_CERT;
	}

	return TLS_CERT_OK;
}

int tls_cert_init_server(void)
{
	if (!sec_tls_enabled()) {
		return TLS_CERT_OK;
	}

	const char *ca_cert = get_config_value("RPC_TLS_CA_CERT", NULL,
					       CA_CERT_PATH);

	const char *cert = get_config_value("RPC_TLS_SERVER_CERT", NULL,
					    HOST_CERT_PATH);
	const char *key = get_config_value("RPC_TLS_SERVER_KEY", NULL,
					   HOST_KEY_PATH);
	const char *cert_dir = get_config_value("RPC_TLS_CERT_DIR", NULL,
						DEFAULT_CERT_DIR);

	g_ctx = malloc(sizeof(tls_cert_ctx_t));
	if (!g_ctx) {
		return TLS_CERT_ERR_INVALID_PARAM;
	}
	memset(g_ctx, 0, sizeof(tls_cert_ctx_t));

	g_ctx->cert_dir = strdup(cert_dir);
	if (!g_ctx->cert_dir) {
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_INVALID_PARAM;
	}

	g_ctx->ssl_ctx = SSL_CTX_new(TLS_method());
	if (!g_ctx->ssl_ctx) {
		free(g_ctx->cert_dir);
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_SSL_CREATE;
	}

	tls_cert_set_ciphersuites_from_conf(g_ctx->ssl_ctx);

	if (SSL_CTX_load_verify_locations(g_ctx->ssl_ctx, ca_cert, NULL) != 1) {
		SSL_CTX_free(g_ctx->ssl_ctx);
		free(g_ctx->cert_dir);
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_LOAD_CA;
	}

	if (SSL_CTX_use_certificate_chain_file(g_ctx->ssl_ctx, cert) != 1 ||
	    SSL_CTX_use_PrivateKey_file(g_ctx->ssl_ctx, key,
					SSL_FILETYPE_PEM) != 1) {
		SSL_CTX_free(g_ctx->ssl_ctx);
		free(g_ctx->cert_dir);
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_LOAD_CERT;
	}

	// if (tls_cert_verify_is_local(cert) != TLS_CERT_IS_LOCAL) {
	// 	ErrorLog("Server certificate CN does not match local host ID");
	// 	SSL_CTX_free(g_ctx->ssl_ctx);
	// 	free(g_ctx);
	// 	g_ctx = NULL;
	// 	return TLS_CERT_ERR_INVALID_PARAM;
	// }

	/* 设置客户端 CA 列表，请求客户端证书 */
	STACK_OF(X509_NAME) *ca_names = SSL_load_client_CA_file(ca_cert);
	if (ca_names) {
		SSL_CTX_set_client_CA_list(g_ctx->ssl_ctx, ca_names);
	}

	SSL_CTX_set_verify(g_ctx->ssl_ctx,
			   SSL_VERIFY_PEER | SSL_VERIFY_CLIENT_ONCE |
				   SSL_VERIFY_FAIL_IF_NO_PEER_CERT,
			   NULL);

	/* 配置国密套件时叠加 SM2 证书链（ENC-005：缺失则失败，不降级明文） */
	if (!tls_cert_apply_sm2_if_configured(g_ctx->ssl_ctx,
					      g_ctx->cert_dir)) {
		SSL_CTX_free(g_ctx->ssl_ctx);
		free(g_ctx->cert_dir);
		free(g_ctx);
		g_ctx = NULL;
		return TLS_CERT_ERR_LOAD_CERT;
	}

	return TLS_CERT_OK;
}

int tls_cert_init_client_from_env(void)
{
	return tls_cert_init_client();
}

int tls_cert_init_server_from_env(void)
{
	return tls_cert_init_server();
}

void tls_cert_cleanup(void)
{
	for (int i = 0; i < g_ccc; i++) {
		if (g_cc[i].ca_cert) {
			X509_free(g_cc[i].ca_cert);
			g_cc[i].ca_cert = NULL;
		}
	}
	g_ccc = 0;

	for (int i = 0; i < g_hccc; i++) {
		if (g_hcc[i].cert) {
			X509_free(g_hcc[i].cert);
			g_hcc[i].cert = NULL;
		}
		if (g_hcc[i].pkey) {
			EVP_PKEY_free(g_hcc[i].pkey);
			g_hcc[i].pkey = NULL;
		}
	}
	g_hccc = 0;

	if (g_ctx) {
		if (g_ctx->ssl_ctx) {
			SSL_CTX_free(g_ctx->ssl_ctx);
		}
		free(g_ctx->hostname);
		if (g_ctx->cert_dir) {
			free(g_ctx->cert_dir);
			g_ctx->cert_dir = NULL;
		}
		free(g_ctx);
		g_ctx = NULL;
	}

	/* rwlock 是 PTHREAD_RWLOCK_INITIALIZER 静态初始化，无需 destroy */
}

tls_cert_ctx_t *tls_cert_get_global_ctx(void)
{
	return g_ctx;
}

SSL_CTX *tls_cert_get_ssl_ctx(void)
{
	return g_ctx ? g_ctx->ssl_ctx : NULL;
}

static SSL *tls_cert_client_handshake_impl(int fd, const char *ca_cn,
					   tls_cert_result_t *result)
{
	if (!g_ctx) {
		return NULL;
	}

	SSL *ssl = SSL_new(g_ctx->ssl_ctx);
	if (!ssl) {
		return NULL;
	}

	SSL_set_fd(ssl, fd);
	if (ca_cn && ca_cn[0] && g_ctx->cert_dir) {
		X509 *cert = NULL;
		EVP_PKEY *pkey = NULL;
		X509 *cert_dup = NULL;
		EVP_PKEY *pkey_dup = NULL;
		int cert_ret = get_host_cert_from_cache(g_ctx->cert_dir, ca_cn,
						 &cert, &pkey);
		if (cert_ret != 0 || !cert || !pkey) {
			SSL_free(ssl);
			return NULL;
		}
		if ((cert_dup = X509_dup(cert)) == NULL ||
			(pkey_dup = EVP_PKEY_dup(pkey)) == NULL ||
			SSL_use_certificate(ssl, cert_dup) != 1 ||
			SSL_use_PrivateKey(ssl, pkey_dup) != 1) {
			if (cert_dup)
				X509_free(cert_dup);
			if (pkey_dup)
				EVP_PKEY_free(pkey_dup);
			SSL_free(ssl);
			return NULL;
		}
	}

	int ret = SSL_connect(ssl);
	if (ret != 1) {
		tls_cert_log_ssl_errors("client", SSL_get_error(ssl, ret));
		SSL_free(ssl);
		return NULL;
	}

	return ssl;
}

SSL *tls_cert_client_handshake(int fd, tls_cert_result_t *result)
{
	return tls_cert_client_handshake_impl(fd, NULL, result);
}

SSL *tls_cert_client_handshake_for_cn(int fd, const char *ca_cn,
				      tls_cert_result_t *result)
{
	return tls_cert_client_handshake_impl(fd, ca_cn, result);
}

static void tls_cert_log_auth_result(const char *cert_cn, const char *client_ip,
				     int client_port, int success)
{
	AuditLog("cert_cn=%s client=%s:%d action=\"mtls_auth\" result=%s",
		 cert_cn ? cert_cn : "none", client_ip ? client_ip : "unknown",
		 client_port, success ? "success" : "failed");
}

SSL *tls_cert_server_handshake(int fd, tls_cert_result_t *result)
{
	if (!g_ctx) {
		return NULL;
	}

	SSL *ssl = SSL_new(g_ctx->ssl_ctx);
	if (!ssl) {
		return NULL;
	}

	SSL_set_fd(ssl, fd);

	int ret = SSL_accept(ssl);

	/* 获取客户端地址信息 */
	struct sockaddr_in addr;
	socklen_t len = sizeof(addr);
	char client_ip[64] = "unknown";
	int client_port = 0;
	if (getpeername(fd, (struct sockaddr *)&addr, &len) == 0) {
		inet_ntop(AF_INET, &addr.sin_addr, client_ip,
			  sizeof(client_ip));
		client_port = ntohs(addr.sin_port);
	}

	/* 获取客户端证书 CN */
	char cert_cn[256] = "none";
	X509 *client_cert = SSL_get_peer_certificate(ssl);
	if (client_cert) {
		X509_NAME_get_text_by_NID(X509_get_subject_name(client_cert),
					  NID_commonName, cert_cn,
					  sizeof(cert_cn));
	}

	if (ret != 1 || !client_cert ||
	    SSL_get_verify_result(ssl) != X509_V_OK) {
		if (ret != 1)
			tls_cert_log_ssl_errors("server", SSL_get_error(ssl, ret));
		else if (SSL_get_verify_result(ssl) != X509_V_OK)
			tls_cert_log_ssl_errors("server certificate verify", 0);
		tls_cert_log_auth_result(cert_cn, client_ip, client_port, 0);
		if (client_cert)
			X509_free(client_cert);
		SSL_free(ssl);
		return NULL;
	}
	X509_free(client_cert);

	/* 握手成功，记录日志 */
	tls_cert_log_auth_result(cert_cn, client_ip, client_port, 1);

	return ssl;
}

int tls_cert_detach_ssl(SSL *ssl)
{
	if (!ssl) {
		return -1;
	}

	int fd = SSL_get_fd(ssl);
	if (fd < 0) {
		return -1;
	}

	int ret = SSL_shutdown(ssl);
	if (ret == 0) {
		SSL_shutdown(ssl);
	}

	SSL_free(ssl);

	return fd;
}

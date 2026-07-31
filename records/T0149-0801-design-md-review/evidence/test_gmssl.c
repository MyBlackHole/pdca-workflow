#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <gmssl/sm2.h>
#include <gmssl/x509_cer.h>
#include <gmssl/x509_ext.h>
#include <gmssl/oid.h>
#include <gmssl/tls.h>
#include <gmssl/sm4.h>

static int fail_count = 0;
static uint8_t *g_ca_der = NULL;
static size_t g_ca_len = 0;

static uint8_t *load_file(const char *path, size_t *len)
{
    FILE *fp = fopen(path, "rb");
    if (!fp) return NULL;
    fseek(fp, 0, SEEK_END);
    *len = ftell(fp);
    rewind(fp);
    uint8_t *buf = malloc(*len);
    if (!buf) { fclose(fp); return NULL; }
    fread(buf, 1, *len, fp);
    fclose(fp);
    return buf;
}
#define TEST(name, expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "  FAIL: %s\n", name); \
        fail_count++; \
    } else { \
        printf("  PASS: %s\n", name); \
    } \
} while(0)

static int cert_sign_to_der(
    int version, const uint8_t *serial, size_t serial_len, int sig_algor,
    const uint8_t *issuer, size_t issuer_len,
    time_t nb, time_t na,
    const uint8_t *subject, size_t subject_len,
    const SM2_KEY *subject_pubkey,
    const uint8_t *iuid, size_t iuid_len,
    const uint8_t *suid, size_t suid_len,
    const uint8_t *exts, size_t exts_len,
    const SM2_KEY *sign_key, const char *signer_id, size_t signer_id_len,
    uint8_t **out, size_t *outlen)
{
    size_t len = 0;
    if (x509_cert_sign_to_der(version, serial, serial_len, sig_algor,
        issuer, issuer_len, nb, na,
        subject, subject_len, subject_pubkey,
        iuid, iuid_len, suid, suid_len,
        exts, exts_len, sign_key, signer_id, signer_id_len,
        NULL, &len) != 1) return -1;
    *out = malloc(len);
    if (!*out) return -1;
    size_t written = 0;
    uint8_t *pp = *out;
    if (x509_cert_sign_to_der(version, serial, serial_len, sig_algor,
        issuer, issuer_len, nb, na,
        subject, subject_len, subject_pubkey,
        iuid, iuid_len, suid, suid_len,
        exts, exts_len, sign_key, signer_id, signer_id_len,
        &pp, &written) != 1) {
        free(*out); *out = NULL; return -1;
    }
    *outlen = written;
    return 1;
}

static time_t days_from_now(int d)
{
    return time(NULL) + (time_t)d * 86400;
}

/* === 7. Cross-compat: tls-keygen (Ed25519) → GMSSL load only === */
/* GMSSL cannot parse/verify Ed25519 certs (unknown signature OID 1.3.101.112).
   This test validates DER files load correctly; parsing is expected to fail. */
static void test_compat_tls_keygen_parse(void)
{
    size_t ca_len, host_len;
    uint8_t *ca = load_file("tls_keygen_certs/ca.der", &ca_len);
    uint8_t *host = load_file("tls_keygen_certs/host.der", &host_len);
    TEST("Ed25519 ca.der loaded", ca && ca_len > 0);
    TEST("Ed25519 host.der loaded", host && host_len > 0);
    free(ca); free(host);
}

/* === 8. Cross-compat: GMSSL SM2 cert → OpenSSL verify === */
static void test_compat_openssl_verify(void)
{
    static const char *ca_pem = "/tmp/gmssl_ca_test.pem";
    FILE *fp = fopen(ca_pem, "wb");
    if (!fp) { TEST("write gmssl pem", 0); return; }
    int r = x509_cert_to_pem(g_ca_der, g_ca_len, fp);
    fclose(fp);
    TEST("write gmssl ca.pem", r == 1);

    /* openssl verify in verbose mode to see alg info */
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "openssl verify -CAfile %s %s 2>&1", ca_pem, ca_pem);
    r = system(cmd);
    TEST("openssl verify gmssl SM2 cert", r == 0);
    unlink(ca_pem);
}

/* === 9. Cross-compat: OpenSSL SM2 cert → GMSSL verify === */
static void test_compat_gmssl_verify(void)
{
    size_t der_len;
    uint8_t *der = load_file("openssl_certs/sm2-ca.der", &der_len);
    TEST("load openssl SM2 ca.der", der && der_len > 0);
    if (!der) return;

    int r = x509_cert_verify_by_ca_cert(der, der_len, der, der_len, NULL, 0);
    TEST("GMSSL verify openssl SM2 cert", r == 1);
    free(der);
}

/* === 10. Cross-compat: verify Ed25519 + RSA chains === */
static void test_compat_pem_roundtrip(void)
{
    int r = system("openssl verify -CAfile tls_keygen_certs/ca.crt tls_keygen_certs/host.crt 2>&1 >/dev/null");
    TEST("openssl verify tls-keygen Ed25519 chain", r == 0);

    r = system("openssl verify -CAfile openssl_certs/rsa-ca.pem openssl_certs/rsa-server.pem 2>&1 >/dev/null");
    TEST("openssl verify RSA chain (reference)", r == 0);
}

/* === 1. SM2 Key Generation + PEM === */
static void test_sm2_keygen(void)
{
    SM2_KEY key;
    int ret = sm2_key_generate(&key);
    TEST("sm2_key_generate", ret == 1);

    FILE *fp = tmpfile();
    ret = sm2_private_key_info_encrypt_to_pem(&key, "test", fp);
    TEST("private key encrypted PEM", ret == 1);
    fclose(fp);
}

/* === 2. X.509 Self-Signed CA + PEM + Self-Verify === */
static void test_x509_ca_cert(void)
{
    SM2_KEY ca_key;
    sm2_key_generate(&ca_key);

    uint8_t name[256];
    size_t name_len = sizeof(name);
    int ret = x509_name_set(name, &name_len, sizeof(name),
        "CN", NULL, NULL, NULL, "GMSSL", "TestCA");
    TEST("x509_name_set", ret == 1);

    uint8_t serial[] = {0x01};
    ret = cert_sign_to_der(1, serial, sizeof(serial), OID_sm2sign_with_sm3,
        name, name_len, days_from_now(-1), days_from_now(3650),
        name, name_len, &ca_key,
        NULL, 0, NULL, 0, NULL, 0,
        &ca_key, NULL, 0, &g_ca_der, &g_ca_len);
    TEST("CA cert sign+alloc", ret == 1 && g_ca_der && g_ca_len > 0);

    FILE *fp = tmpfile();
    ret = x509_cert_to_pem(g_ca_der, g_ca_len, fp);
    TEST("x509_cert_to_pem", ret == 1);
    fclose(fp);

    ret = x509_cert_verify_by_ca_cert(g_ca_der, g_ca_len, g_ca_der, g_ca_len, NULL, 0);
    TEST("self-sign verify", ret == 1);
}

/* === 3. CA signs Server Cert + Verify + Get Subject === */
static void test_server_cert(void)
{
    SM2_KEY ca_key, svr_key;
    uint8_t *svr_der = NULL;
    size_t svr_len;
    int ret;

    sm2_key_generate(&ca_key);
    sm2_key_generate(&svr_key);

    uint8_t ca_name[256], svr_name[256];
    size_t ca_name_len = sizeof(ca_name), svr_name_len = sizeof(svr_name);

    ret = x509_name_set(ca_name, &ca_name_len, sizeof(ca_name),
        "CN", NULL, NULL, NULL, "GMSSL", "RootCA");
    TEST("CA x509_name_set", ret == 1);

    uint8_t cs[] = {0x01};
    ret = cert_sign_to_der(1, cs, sizeof(cs), OID_sm2sign_with_sm3,
        ca_name, ca_name_len, days_from_now(-1), days_from_now(3650),
        ca_name, ca_name_len, &ca_key,
        NULL, 0, NULL, 0, NULL, 0,
        &ca_key, NULL, 0, &g_ca_der, &g_ca_len);
    TEST("CA cert sign", ret == 1);

    ret = x509_name_set(svr_name, &svr_name_len, sizeof(svr_name),
        "CN", NULL, NULL, NULL, "BackupSvr", "test-server.local");
    TEST("server x509_name_set", ret == 1);

    uint8_t exts[256];
    size_t exts_len = 0;
    ret = x509_exts_add_key_usage(exts, &exts_len, sizeof(exts), 0,
        X509_KU_DIGITAL_SIGNATURE | X509_KU_KEY_ENCIPHERMENT);
    TEST("x509_exts_add_key_usage", ret == 1);

    uint8_t ss[] = {0x02};
    ret = cert_sign_to_der(1, ss, sizeof(ss), OID_sm2sign_with_sm3,
        ca_name, ca_name_len, days_from_now(-1), days_from_now(365),
        svr_name, svr_name_len, &svr_key,
        NULL, 0, NULL, 0, exts, exts_len,
        &ca_key, NULL, 0, &svr_der, &svr_len);
    TEST("server cert sign+alloc", ret == 1 && svr_der && svr_len > 0);

    ret = x509_cert_verify_by_ca_cert(svr_der, svr_len, g_ca_der, g_ca_len, NULL, 0);
    TEST("server cert verify by CA", ret == 1);

    const uint8_t *subj;
    size_t subj_len;
    ret = x509_cert_get_subject(svr_der, svr_len, &subj, &subj_len);
    TEST("x509_cert_get_subject", ret == 1 && subj_len > 0);

    free(svr_der);
}

/* === 4. SM4-GCM + Tamper Detection === */
static void test_sm4_gcm(void)
{
    SM4_KEY key;
    uint8_t raw_key[16], iv[12];
    uint8_t pt[] = "Hello GMSSL SM4-GCM! Backup data test.";
    uint8_t ct[64], dec[64], tag[16];
    int ret;

    memset(raw_key, 0x01, 16);
    memset(iv, 0x02, 12);
    sm4_set_encrypt_key(&key, raw_key);

    ret = sm4_gcm_encrypt(&key, iv, sizeof(iv),
        NULL, 0, pt, strlen((char*)pt), ct, sizeof(tag), tag);
    TEST("sm4_gcm_encrypt", ret == 1);

    ret = sm4_gcm_decrypt(&key, iv, sizeof(iv),
        NULL, 0, ct, strlen((char*)pt), tag, sizeof(tag), dec);
    TEST("sm4_gcm_decrypt", ret == 1);
    TEST("content match", memcmp(pt, dec, strlen((char*)pt)) == 0);

    ct[5] ^= 0xFF;
    ret = sm4_gcm_decrypt(&key, iv, sizeof(iv),
        NULL, 0, ct, strlen((char*)pt), tag, sizeof(tag), dec);
    TEST("tamper rejected", ret != 1);
}

/* === 5. TLS Protocol Constants === */
static void test_tls_constants(void)
{
    TEST("TLCP", TLS_protocol_tlcp == 0x0101);
    TEST("TLS13", TLS_protocol_tls13 == 0x0304);
    TEST("SM4-GCM-SM3", TLS_cipher_sm4_gcm_sm3 == 0x00C6);
    TEST("AES128-GCM", TLS_cipher_aes_128_gcm_sha256 == 0x1301);
}

/* === 6. TLS/TLCP Context === */
static void test_tls_context(void)
{
    TLS_CTX ctx;
    int ret = tls_ctx_init(&ctx, TLS_protocol_tls13, 1);
    TEST("TLS13 client ctx", ret == 1);

    int suites[] = {TLS_cipher_sm4_gcm_sm3, TLS_cipher_aes_128_gcm_sha256};
    ret = tls_ctx_set_cipher_suites(&ctx, suites, 2);
    TEST("set cipher suites", ret == 1);
    tls_ctx_cleanup(&ctx);

    TLS_CTX tlcp;
    ret = tls_ctx_init(&tlcp, TLS_protocol_tlcp, 0);
    TEST("TLCP server ctx", ret == 1);
    tls_ctx_cleanup(&tlcp);
}

int main(void)
{
    printf("\n=== GMSSL v3.1.1 (xmake) Replacement PoC ===\n\n");

    printf("[1/6] SM2 Key Generation & PEM Export\n");
    test_sm2_keygen();

    printf("\n[2/6] X.509 Self-Signed CA Certificate\n");
    test_x509_ca_cert();

    printf("\n[3/6] CA → Server Cert + Verify + Get Subject\n");
    test_server_cert();

    printf("\n[4/6] SM4-GCM + Tamper Detection\n");
    test_sm4_gcm();

    printf("\n[5/6] TLS Protocol Constants\n");
    test_tls_constants();

    printf("\n[6/6] TLS/TLCP Context\n");
    test_tls_context();

    printf("\n--- Cross-Compatibility ---\n");
    printf("\n[7/10] tls-keygen (Ed25519) → GMSSL parse\n");
    test_compat_tls_keygen_parse();

    printf("\n[8/10] GMSSL SM2 cert → OpenSSL verify\n");
    test_compat_openssl_verify();

    printf("\n[9/10] OpenSSL SM2 cert → GMSSL verify\n");
    test_compat_gmssl_verify();

    printf("\n[10/10] tls-keygen Ed25519 chain self-verify\n");
    test_compat_pem_roundtrip();

    printf("\n=== %d / 10 groups ", 10);
    if (fail_count > 0)
        printf("(%d FAILED) ===\n", fail_count);
    else
        printf("(ALL PASSED) ===\n");

    free(g_ca_der);
    return fail_count > 0 ? 1 : 0;
}

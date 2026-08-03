#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <gmssl/sm4.h>
#include <gmssl/sm3.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>

#define MB (1024*1024)
#define DATA_MB 128
#define ROUNDS 3

static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

static void bench(const char *name, double t0, double el)
{
    printf("%-20s : %7.1f MB/s\n", name, DATA_MB * ROUNDS / (el / 1000.0));
    fflush(stdout);
}

int main(void)
{
    size_t n = DATA_MB * MB;
    uint8_t *in = malloc(n), *out = malloc(n + 64);
    memset(in, 0x5a, n);
    uint8_t key[16], iv[16], mac[32];
    memset(key, 1, sizeof(key)); memset(iv, 2, sizeof(iv));
    int olen = 0, tlen = 0, rounds;
    unsigned int dlen = 0;
    double t0, el;

    SM4_KEY sm4key;
    sm4_set_encrypt_key(&sm4key, key);
    SM3_HMAC_CTX hctx;
    size_t blocks = (n + 15) / 16;

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++)
        sm4_cbc_encrypt(&sm4key, iv, in, blocks, out);
    el = now_ms() - t0;
    bench("GMSSL sm4_cbc", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++)
        sm3_digest(in, n, mac);
    el = now_ms() - t0;
    bench("GMSSL sm3", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++) {
        sm3_hmac_init(&hctx, key, sizeof(key));
        sm3_hmac_update(&hctx, in, n);
        sm3_hmac_finish(&hctx, mac);
    }
    el = now_ms() - t0;
    bench("GMSSL sm3_hmac", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++) {
        sm4_cbc_encrypt(&sm4key, iv, in, blocks, out);
        sm3_hmac_init(&hctx, key, sizeof(key));
        sm3_hmac_update(&hctx, in, n);
        sm3_hmac_finish(&hctx, mac);
    }
    el = now_ms() - t0;
    bench("GMSSL sm4_cbc+hmac", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++)
        sm4_gcm_encrypt(&sm4key, iv, sizeof(iv), NULL, 0, in, n, out, 16, mac);
    el = now_ms() - t0;
    bench("GMSSL sm4-gcm", t0, el);

    EVP_CIPHER_CTX *cctx = EVP_CIPHER_CTX_new();
    EVP_CIPHER *sm4_gcm = EVP_CIPHER_fetch(NULL, "SM4-GCM", NULL);
    if (!sm4_gcm) { fprintf(stderr, "SM4-GCM unavailable\n"); return 1; }

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++) {
        EVP_EncryptInit_ex(cctx, EVP_aes_128_gcm(), NULL, key, iv);
        EVP_EncryptUpdate(cctx, out, &olen, in, (int)n);
        EVP_EncryptFinal_ex(cctx, out + olen, &tlen);
    }
    el = now_ms() - t0;
    bench("OpenSSL aes-128-gcm", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++) {
        EVP_EncryptInit_ex(cctx, EVP_sm4_cbc(), NULL, key, iv);
        EVP_EncryptUpdate(cctx, out, &olen, in, (int)n);
        EVP_EncryptFinal_ex(cctx, out + olen, &tlen);
    }
    el = now_ms() - t0;
    bench("OpenSSL sm4-cbc", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++) {
        EVP_EncryptInit_ex(cctx, sm4_gcm, NULL, key, iv);
        EVP_EncryptUpdate(cctx, out, &olen, in, (int)n);
        EVP_EncryptFinal_ex(cctx, out + olen, &tlen);
    }
    el = now_ms() - t0;
    bench("OpenSSL sm4-gcm", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++)
        EVP_Digest(in, n, mac, &dlen, EVP_sm3(), NULL);
    el = now_ms() - t0;
    bench("OpenSSL sm3", t0, el);

    t0 = now_ms();
    for (rounds = 0; rounds < ROUNDS; rounds++) {
        EVP_EncryptInit_ex(cctx, EVP_sm4_cbc(), NULL, key, iv);
        EVP_EncryptUpdate(cctx, out, &olen, in, (int)n);
        EVP_EncryptFinal_ex(cctx, out + olen, &tlen);
        HMAC(EVP_sm3(), key, sizeof(key), in, n, mac, &dlen);
    }
    el = now_ms() - t0;
    bench("OpenSSL sm4_cbc+hmac", t0, el);

    EVP_CIPHER_free(sm4_gcm);
    EVP_CIPHER_CTX_free(cctx);
    free(in); free(out);
    return 0;
}

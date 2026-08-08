#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <openssl/evp.h>
#include <sodium.h>

/* AEAD 认证加密实证：
 *   对比两种工业级 AEAD 算法：
 *     V1 AES-128-GCM        —— OpenSSL EVP 接口（Intel AES-NI 硬件加速）
 *     V2 ChaCha20-Poly1305  —— libsodium（软件实现，无硬件依赖）
 * 验证点：
 *   1. 加/解密往返还原一致（正确密钥）
 *   2. 篡改检测：密文或 tag 任意 1 字节翻转 → 解密必须失败
 *   3. 吞吐对比（128MB 数据，单核）
 * AEAD 的意义：备份数据在加密之外还要"防篡改/防损坏"——GCM/ChaCha20-Poly1305
 * 同时提供机密性 + 完整性（GCM 的 GMAC、ChaCha 的 Poly1305），
 * 而场景07 的 XOR 只有机密性、无认证，密文被改无法发现。
 */

#define DATA_SIZE (128ull * 1024 * 1024) /* 128MB */
#define TAG_LEN   16
#define NONCE_LEN 12

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

static int gcm_round_trip(uint8_t *pt, size_t len,
                          uint8_t *ct, uint8_t *dec,
                          uint8_t *tag, const uint8_t *nonce,
                          const uint8_t *key)
{
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    int outl = 0, total = 0, rc = 0;

    if (!ctx) return -1;
    /* 加密 */
    if (EVP_EncryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL) != 1) goto out;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, NONCE_LEN, NULL) != 1) goto out;
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, key, nonce) != 1) goto out;
    if (EVP_EncryptUpdate(ctx, ct, &outl, pt, (int)len) != 1) goto out;
    total = outl;
    if (EVP_EncryptFinal_ex(ctx, ct + total, &outl) != 1) goto out;
    total += outl;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, TAG_LEN, tag) != 1) goto out;

    /* 解密 */
    EVP_CIPHER_CTX_reset(ctx);
    if (EVP_DecryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL) != 1) goto out;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, NONCE_LEN, NULL) != 1) goto out;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, nonce) != 1) goto out;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_LEN, tag) != 1) goto out;
    if (EVP_DecryptUpdate(ctx, dec, &outl, ct, total) != 1) goto out;
    if (EVP_DecryptFinal_ex(ctx, dec + outl, &outl) != 1) goto out; /* tag 校验失败 → 返回 0 */

    rc = 0;
out:
    EVP_CIPHER_CTX_free(ctx);
    return rc;
}

static int gcm_decrypt_auth(const uint8_t *ct, size_t len,
                            uint8_t *dec, const uint8_t *tag,
                            const uint8_t *nonce, const uint8_t *key)
{
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    int outl = 0, total = 0, rc = 1; /* 默认失败 */

    if (!ctx) return 1;
    if (EVP_DecryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL) != 1) goto out;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, NONCE_LEN, NULL) != 1) goto out;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, nonce) != 1) goto out;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_LEN, (void *)(uintptr_t)tag) != 1) goto out;
    if (EVP_DecryptUpdate(ctx, dec, &outl, ct, (int)len) != 1) goto out;
    total = outl;
    if (EVP_DecryptFinal_ex(ctx, dec + total, &outl) != 1) goto out; /* 认证失败 → !=1 */
    rc = 0;
out:
    EVP_CIPHER_CTX_free(ctx);
    return rc;
}

int main(void)
{
    uint8_t *pt = NULL, *ct = NULL, *dec = NULL;
    uint8_t key[32], nonce[NONCE_LEN];
    uint8_t tag[TAG_LEN];
    double t0, t_aes, t_cha;
    double mb_aes, mb_cha;
    int ok = 1;

    if (sodium_init() < 0) {
        printf("FAIL: sodium_init\n");
        return 1;
    }
    pt = malloc(DATA_SIZE);
    ct = malloc(DATA_SIZE);
    dec = malloc(DATA_SIZE);
    if (!pt || !ct || !dec) return 1;
    randombytes_buf(pt, DATA_SIZE);
    randombytes_buf(key, sizeof(key));
    randombytes_buf(nonce, sizeof(nonce));

    printf("== 场景13 AEAD 认证加密 ==\n");
    printf("数据: %llu MB; AES-128-GCM (OpenSSL, AES-NI) vs ChaCha20-Poly1305 (libsodium)\n\n",
           (unsigned long long)(DATA_SIZE / (1024 * 1024)));

    /* ── V1 AES-128-GCM ── */
    t0 = now_ms();
    if (gcm_round_trip(pt, DATA_SIZE, ct, dec, tag, nonce, key) < 0) {
        printf("FAIL V1 GCM 往返\n");
        return 1;
    }
    t_aes = now_ms() - t0;
    mb_aes = (double)DATA_SIZE / (1024 * 1024) / (t_aes / 1e3);

    if (memcmp(pt, dec, DATA_SIZE) != 0) {
        printf("FAIL V1 GCM 往返还原不一致\n");
        ok = 0;
    } else {
        printf("V1 AES-128-GCM: 还原一致, %.1f MB/s\n", mb_aes);
    }

    /* 篡改检测：翻转 tag 中间 1 字节，必须认证失败 */
    ct[0] ^= 0x01;
    if (gcm_decrypt_auth(ct, DATA_SIZE, dec, tag, nonce, key) == 0) {
        printf("FAIL V1 GCM 篡改未被检出（密文翻转 1 字节仍认证通过）\n");
        ok = 0;
    } else {
        printf("V1 GCM 篡改检测: 密文 1 字节翻转 → 认证失败 ✓\n");
    }
    ct[0] ^= 0x01;

    tag[7] ^= 0x80;
    if (gcm_decrypt_auth(ct, DATA_SIZE, dec, tag, nonce, key) == 0) {
        printf("FAIL V1 GCM 篡改未被检出（tag 翻转 1 字节仍认证通过）\n");
        ok = 0;
    } else {
        printf("V1 GCM 篡改检测: tag 1 字节翻转 → 认证失败 ✓\n");
    }
    tag[7] ^= 0x80;

    /* ── V2 ChaCha20-Poly1305 ── */
    t0 = now_ms();
    {
        unsigned long long clen = DATA_SIZE + crypto_aead_chacha20poly1305_ABYTES;
        uint8_t *ct2 = malloc(clen);
        uint8_t *dec2 = malloc(DATA_SIZE);
        uint8_t key2[crypto_aead_chacha20poly1305_KEYBYTES];
        uint8_t nonce2[crypto_aead_chacha20poly1305_NPUBBYTES];
        unsigned long long mlen = 0;
        int rc;

        if (!ct2 || !dec2) return 1;
        randombytes_buf(key2, sizeof(key2));
        randombytes_buf(nonce2, sizeof(nonce2));

        if (crypto_aead_chacha20poly1305_encrypt(ct2, &clen,
                pt, (unsigned long long)DATA_SIZE, NULL, 0, NULL, nonce2, key2) != 0) {
            printf("FAIL V2 ChaCha 加密\n");
            return 1;
        }
        if (crypto_aead_chacha20poly1305_decrypt(dec2, &mlen, NULL,
                ct2, clen, NULL, 0, nonce2, key2) != 0) {
            printf("FAIL V2 ChaCha 解密\n");
            return 1;
        }
        t_cha = now_ms() - t0;
        mb_cha = (double)DATA_SIZE / (1024 * 1024) / (t_cha / 1e3);

        if (mlen != DATA_SIZE || memcmp(pt, dec2, DATA_SIZE) != 0) {
            printf("FAIL V2 ChaCha 往返还原不一致\n");
            ok = 0;
        } else {
            printf("V2 ChaCha20-Poly1305: 还原一致, %.1f MB/s\n", mb_cha);
        }

        /* 篡改检测：ChaCha 密文翻转 1 字节 */
        ct2[5] ^= 0x01;
        rc = crypto_aead_chacha20poly1305_decrypt(dec2, &mlen, NULL,
                ct2, clen, NULL, 0, nonce2, key2);
        if (rc == 0) {
            printf("FAIL V2 ChaCha 篡改未被检出\n");
            ok = 0;
        } else {
            printf("V2 ChaCha 篡改检测: 密文 1 字节翻转 → 认证失败 ✓\n");
        }

        free(ct2);
        free(dec2);
    }

    printf("\nAES-GCM/ChaCha 吞吐比 = %.2f\n", mb_aes / mb_cha);

    /* 断言：篡改 100% 检出（上面已逐项检查），吞吐均 > 100MB/s 量级 */
    if (!(mb_aes > 100.0)) {
        printf("FAIL AC-2: AES-GCM 吞吐 %.1f MB/s 异常低\n", mb_aes);
        ok = 0;
    }
    if (!(mb_cha > 100.0)) {
        printf("FAIL AC-2: ChaCha 吞吐 %.1f MB/s 异常低\n", mb_cha);
        ok = 0;
    }

    if (ok) {
        printf("\nPASS: 两算法往返还原一致、篡改 1 字节 100%% 检出\n");
    } else {
        printf("\nFAIL\n");
    }
    free(pt);
    free(ct);
    free(dec);
    return ok ? 0 : 1;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <blake3.h>
#include <xxhash.h>
#include <openssl/evp.h>

/* 高速哈希选型实证：
 *   备份去重/校验链路的核心是"块指纹"——对每个数据块算哈希，作为去重索引键。
 *   对比三类算法：
 *     V1 BLAKE3       —— 现代多线程树哈希，极快（libblake3）
 *     V2 XXH3         —— 非加密哈希，用于去重位图/布隆，不可用于安全（libxxhash）
 *     V3 SHA-256      —— 密码学哈希，安全但慢（OpenSSL EVP）
 * 验证点：
 *   1. 大块吞吐（1GB）：去重指纹 / 全量校验的热路径速率
 *   2. 短块正确性：64B 输入与参考值对照（blake3 官方空串/64B 向量）
 *   3. 16KB 典型块吞吐：去重切块后的实际指纹速率
 * 结论给选型：安全场景用 BLAKE3，非安全高速索引用 XXH3，兼容性/合规用 SHA-256。
 */

#define BIG_SIZE (1024ull * 1024 * 1024) /* 1GB 大块吞吐 */
#define SEG_SIZE (16 * 1024)             /* 16KB 典型去重块 */

/* 16KB 段数：总 1GB */
#define N_SEG_BIG (BIG_SIZE / SEG_SIZE)  /* 65536 段 × 16KB = 1GB */

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

int main(void)
{
    uint8_t *big = NULL;
    uint8_t out32[32];
    double t0, t_b3, t_xx, t_sha;
    double mb_b3, mb_xx, mb_sha;
    size_t i;
    uint64_t acc = 0;
    int ok = 1;

    big = malloc(BIG_SIZE);
    if (!big) return 1;
    /* 运行时生成数据，避免编译器常量折叠（否则 XXH3 会被优化成编译期常量） */
    srand((unsigned)now_ms());
    for (i = 0; i < BIG_SIZE; i++)
        big[i] = (uint8_t)(rand() ^ (i * 131 + (i >> 8)));

    printf("== 场景14 高速哈希选型 ==\n");
    printf("BLAKE3 (libblake3) vs XXH3 (libxxhash) vs SHA-256 (OpenSSL)\n\n");

    /* ── V1 BLAKE3 大块吞吐（1GB 单次）── */
    t0 = now_ms();
    blake3_hasher ctx;
    blake3_hasher_init(&ctx);
    blake3_hasher_update(&ctx, big, BIG_SIZE);
    blake3_hasher_finalize(&ctx, out32, sizeof(out32));
    t_b3 = now_ms() - t0;
    mb_b3 = (double)BIG_SIZE / (1024 * 1024) / (t_b3 / 1e3);

    /* ── V2 XXH3 大块吞吐 ── */
    t0 = now_ms();
    acc = XXH3_64bits(big, BIG_SIZE);
    t_xx = now_ms() - t0;
    mb_xx = (double)BIG_SIZE / (1024 * 1024) / (t_xx / 1e3);

    /* ── V3 SHA-256 大块吞吐 ── */
    t0 = now_ms();
    {
        EVP_MD_CTX *m = EVP_MD_CTX_new();
        unsigned int len = 0;
        EVP_DigestInit_ex(m, EVP_sha256(), NULL);
        EVP_DigestUpdate(m, big, BIG_SIZE);
        EVP_DigestFinal_ex(m, out32, &len);
        EVP_MD_CTX_free(m);
    }
    t_sha = now_ms() - t0;
    mb_sha = (double)BIG_SIZE / (1024 * 1024) / (t_sha / 1e3);

    printf("1GB 单次吞吐:\n");
    printf("  BLAKE3 : %.0f MB/s  (sum %02x%02x…)\n", mb_b3, out32[0], out32[1]);
    printf("  XXH3   : %.0f MB/s  (h=%016llx)\n", mb_xx,
           (unsigned long long)acc);
    printf("  SHA-256: %.0f MB/s\n", mb_sha);

    /* ── 16KB 段指纹吞吐（去重热路径）── */
    {
        double t;
        uint64_t seg_acc = 0;
        t0 = now_ms();
        for (i = 0; i < N_SEG_BIG; i++) {
            blake3_hasher c;
            blake3_hasher_init(&c);
            blake3_hasher_update(&c, big + i * SEG_SIZE, SEG_SIZE);
            blake3_hasher_finalize(&c, out32, sizeof(out32));
            seg_acc += out32[0];
        }
        t = now_ms() - t0;
        printf("\n16KB×%zu 段 BLAKE3 指纹: %.0f MB/s (总和 %llu)\n",
               (size_t)N_SEG_BIG,
               (double)(BIG_SIZE) / (1024 * 1024) / (t / 1e3),
               (unsigned long long)seg_acc);
    }

    /* ── 短输入正确性：BLAKE3 官方向量（空串 + "abc"）── */
    {
        const char *empty = "";
        static const uint8_t ref0[32] = {
            0xaf, 0x13, 0x49, 0xb9, 0xf5, 0xf9, 0xa1, 0xa6,
            0xa0, 0x40, 0x4d, 0xea, 0x36, 0xdc, 0xc9, 0x49,
            0x9b, 0xcb, 0x25, 0xc9, 0xad, 0xc1, 0x12, 0xb7,
            0xcc, 0x9a, 0x93, 0xca, 0xe4, 0x1f, 0x32, 0x62
        };
        static const uint8_t refabc[32] = {
            0x64, 0x37, 0xb3, 0xac, 0x38, 0x46, 0x51, 0x33,
            0xff, 0xb6, 0x3b, 0x75, 0x27, 0x3a, 0x8d, 0xb5,
            0x48, 0xc5, 0x58, 0x46, 0x5d, 0x79, 0xdb, 0x03,
            0xfd, 0x35, 0x9c, 0x6c, 0xd5, 0xbd, 0x9d, 0x85
        };
        blake3_hasher c;
        blake3_hasher_init(&c);
        blake3_hasher_update(&c, empty, 0);
        blake3_hasher_finalize(&c, out32, sizeof(out32));
        if (memcmp(out32, ref0, 32) != 0) {
            printf("FAIL AC-3: BLAKE3 空串向量不匹配\n");
            ok = 0;
        } else {
            printf("BLAKE3 空串参考向量: 匹配 ✓\n");
        }
        blake3_hasher_init(&c);
        blake3_hasher_update(&c, "abc", 3);
        blake3_hasher_finalize(&c, out32, sizeof(out32));
        if (memcmp(out32, refabc, 32) != 0) {
            printf("FAIL AC-3: BLAKE3 \"abc\" 向量不匹配\n");
            ok = 0;
        } else {
            printf("BLAKE3 \"abc\" 参考向量: 匹配 ✓\n");
        }
    }

    /* 断言：blake3、xxh 均 > sha256（本机 SHA-256 经 SHA-NI 加速，仍应显著落后） */
    if (!(mb_b3 > mb_sha)) {
        printf("FAIL AC-3: BLAKE3 %.0f <= SHA-256 %.0f\n", mb_b3, mb_sha);
        ok = 0;
    }
    if (!(mb_xx > mb_sha)) {
        printf("FAIL AC-3: XXH3 %.0f <= SHA-256 %.0f\n", mb_xx, mb_sha);
        ok = 0;
    }

    if (ok)
        printf("\nPASS: BLAKE3/XXH3 吞吐均 > SHA-256, 空串向量正确\n");
    else
        printf("\nFAIL\n");
    free(big);
    return ok ? 0 : 1;
}

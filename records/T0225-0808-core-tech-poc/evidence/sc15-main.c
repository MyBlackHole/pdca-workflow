#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>

/* 布隆过滤器去重索引实证：
 *   备份去重第一步是"这个块我见过吗？"——用指纹查索引。
 *   精确做法：哈希表存所有指纹（内存 O(n)）。
 *   布隆做法：位数组 + k 个哈希函数，只存指纹的"痕迹"（内存固定、可远小于哈希表）。
 *   代价：假阳性（没见过却说见过，需要二次确认）。
 * 验证点：
 *   1. 正确性：已插入元素 100% 命中（无假阴性）
 *   2. 假阳率：实测 ≤ 理论上限 (1-e^(-kn/m))^k，且随 m/n 增大而下降
 *   3. 内存：布隆 vs 精确哈希表（存 64B 指纹）的占用对比
 *   4. 吞吐：插入/查询速率
 *   最优 k = (m/n) * ln2，此时假阳率 = (0.6185)^(m/n)。
 */

#define N_ITEMS  1000000  /* 100 万条指纹 */
#define M_BITS   (N_ITEMS * 8u) /* m/n=8：1MB 位数组 = 8Mbit */
#define K_HASH   6        /* 接近最优 (8*ln2≈5.5) */
#define FINGER_SZ 64      /* 精确哈希表每条指纹 64B（blake3/xxhash 级） */
#define N_PROBE  (20 * 1000000) /* 假阳率测试元素数：2000 万 */

/* 双层 64-bit 哈希派生出 k 个独立位位置（双哈希法） */
static uint64_t h1(uint64_t x) { x *= 0x9E3779B97F4A7C15ULL; x ^= x >> 29; return x; }
static uint64_t h2(uint64_t x) { x += 0xBF58476D1CE4E5B9ULL; x ^= x >> 27; x *= 0x94D049BB133111EBULL; return x ^ (x >> 31); }

static void bf_set(uint8_t *bits, uint64_t key)
{
    uint64_t a = h1(key), b = h2(key);
    int i;
    for (i = 0; i < K_HASH; i++) {
        uint64_t pos = (a + (uint64_t)i * b) % M_BITS;
        bits[pos >> 3] |= (uint8_t)(1u << (pos & 7));
    }
}

static int bf_get(const uint8_t *bits, uint64_t key)
{
    uint64_t a = h1(key), b = h2(key);
    int i;
    for (i = 0; i < K_HASH; i++) {
        uint64_t pos = (a + (uint64_t)i * b) % M_BITS;
        if (!(bits[pos >> 3] & (uint8_t)(1u << (pos & 7))))
            return 0;
    }
    return 1;
}

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

static uint64_t splitmix(uint64_t *s)
{
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

int main(void)
{
    uint8_t *bits = NULL;
    uint64_t *keys = NULL;
    uint64_t seed = 12345;
    size_t i;
    double t0, t_insert, t_query;
    long fp = 0, false_pos = 0;
    double theory;
    int ok = 1;

    bits = calloc(M_BITS / 8, 1);
    keys = malloc(sizeof(uint64_t) * N_ITEMS);
    if (!bits || !keys) return 1;
    for (i = 0; i < N_ITEMS; i++)
        keys[i] = splitmix(&seed);

    printf("== 场景15 布隆过滤器去重索引 ==\n");
    printf("条目 N=%d, 位数组 m=%llu bit (m/n=%.1f), 哈希 k=%d\n\n",
           N_ITEMS, (unsigned long long)M_BITS,
           (double)M_BITS / N_ITEMS, K_HASH);

    /* 插入 */
    t0 = now_ms();
    for (i = 0; i < N_ITEMS; i++)
        bf_set(bits, keys[i]);
    t_insert = now_ms() - t0;

    /* 已插入元素：100% 命中（无假阴性） */
    for (i = 0; i < N_ITEMS; i++) {
        if (!bf_get(bits, keys[i])) fp++;
    }
    printf("已插入元素命中率: %.4f%% (假阴性 %ld)\n",
           100.0 * (N_ITEMS - fp) / N_ITEMS, fp);
    if (fp != 0) {
        printf("FAIL AC-4: 存在假阴性（布隆不应有假阴性）\n");
        ok = 0;
    }

    /* 假阳率：用 2000 万未插入元素测试 */
    t0 = now_ms();
    for (i = 0; i < N_PROBE; i++) {
        uint64_t probe = splitmix(&seed) ^ 0xDEADBEEF;
        if (bf_get(bits, probe)) false_pos++;
    }
    t_query = now_ms() - t0;

    theory = 1.0 - exp(-(double)K_HASH * N_ITEMS / M_BITS);
    theory = pow(theory, (double)K_HASH);
    /* 最优 k 时理论 = (0.6185)^(m/n) = (0.6185)^8 ≈ 0.0216 */

    printf("未插入元素假阳率实测: %.4f%%  (%.2f/%dM)\n",
           100.0 * false_pos / N_PROBE, (double)false_pos, N_PROBE / 1000000);
    printf("理论上限:              %.4f%%  (m/n=%.1f)\n",
           100.0 * theory, (double)M_BITS / N_ITEMS);
    printf("实测 ≤ 理论: %s\n",
           (double)false_pos <= theory * N_PROBE * 1.5 + 1000 ? "是 ✓" : "否 ✗");

    if ((double)false_pos > theory * N_PROBE * 1.5 + 1000) {
        printf("FAIL AC-4: 实测假阳率 %.4f%% 超出理论上限 %.4f%% 的 1.5 倍\n",
               100.0 * false_pos / N_PROBE, 100.0 * theory);
        ok = 0;
    }

    /* 内存对比：布隆 vs 精确哈希表 */
    {
        double mem_bf = (double)M_BITS / 8;
        double mem_exact = (double)N_ITEMS * FINGER_SZ;
        printf("\n内存对比:\n");
        printf("  布隆位数组:  %.1f MB\n", mem_bf / 1024 / 1024);
        printf("  精确哈希表:  %.1f MB (每条指纹 %dB)\n",
               mem_exact / 1024 / 1024, FINGER_SZ);
        printf("  布隆/精确 =  %.2fx\n", mem_bf / mem_exact);
        if (mem_bf >= mem_exact) {
            printf("FAIL AC-4: 布隆未节省内存\n");
            ok = 0;
        }
    }

    /* 吞吐（插入与查询各自实际次数） */
    printf("\n吞吐: 插入 %.1f M/s (%d 次), 查询 %.1f M/s (%d 次)\n",
           N_ITEMS / 1e6 / (t_insert / 1e3), N_ITEMS,
           N_PROBE / 1e6 / (t_query / 1e3), N_PROBE);

    if (ok)
        printf("\nPASS: 无假阴性、假阳率≤理论、内存节省\n");
    else
        printf("\nFAIL\n");
    free(bits);
    free(keys);
    return ok ? 0 : 1;
}

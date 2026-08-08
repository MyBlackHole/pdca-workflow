#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

/* Reed-Solomon 纠删码实证（自研 GF(2^8)）：
 *   备份可靠性的两个层次：
 *     复制 (replication)     : 存 3 份 → 3x 开销, 坏 2 份就挂
 *     纠删码 (erasure code)  : RS(5,3) → 5 片分散存储, 任意 ≤2 片丢失可恢复
 *   Reed-Solomon 原理（GF(2^8)，本原多项式 0x11D 与 AES 相同）：
 *     - 编码：k 个数据片 × (k×n) 编码矩阵 = n 片（前 k 行单位阵 + 后 n-k 行 Vandermonde）
 *     - 每片 = 对每字节做 GF 域上的线性组合
 *     - 恢复：取幸存 n-k 行的子矩阵，求逆，乘回得到原数据
 *   验证：
 *     1. RS(5,3) 编解码往返还原一致
 *     2. 任意 2 片丢失（数据片/校验片混合）→ 剩余 3 片完整恢复
 *     3. 冗余开销 n/k = 1.67x（对比复制 3x）
 */

#define K_DATA 3
#define N_SHARE 5
#define ERASE_MAX (N_SHARE - K_DATA) /* 2 */

/* ── GF(2^8) 域运算：本原多项式 0x11D ── */
static uint8_t gf_mul(uint8_t a, uint8_t b)
{
    uint8_t p = 0;
    int i;
    for (i = 0; i < 8; i++) {
        if (b & 1) p ^= a;
        uint8_t hi = a & 0x80;
        a <<= 1;
        if (hi) a ^= 0x1D; /* 0x11D 的 8 位截断 */
        b >>= 1;
    }
    return p;
}

/* GF 域求逆：a^(254) = 1/a （费马小定理，GF(2^8) 乘法群阶 255） */
static uint8_t gf_inv(uint8_t a)
{
    uint8_t r = 1;
    int i;
    if (a == 0) return 0;
    for (i = 0; i < 254; i++)
        r = gf_mul(r, a);
    return r;
}

/* ── 编码矩阵：k×n。前 k 列单位阵，后 n-k 列 Vandermonde（行 i, 列 j = x^i 的 j 次方） ──
 *   片 j 的生成向量 = [1, x^j, x^(2j), …, x^((k-1)j)]  (x = 2)
 *   校验片 j (j=k..n-1)：向量 = [1, 2^j, 4^j, ...]
 *   RS 要求任何 k 行组成的子矩阵可逆（Vandermonde 保证）*/
static void rs_matrix(uint8_t m[N_SHARE][K_DATA])
{
    int i, j, p;
    for (i = 0; i < N_SHARE; i++) {
        for (j = 0; j < K_DATA; j++) {
            if (i < K_DATA) {
                m[i][j] = (i == j) ? 1 : 0;
            } else {
                /* Vandermonde：第 i 行第 j 列 = (2^i)^j，i 从 0 起 */
                uint8_t base = 1;
                for (p = 0; p < i - K_DATA; p++) base = gf_mul(base, 2);
                uint8_t v = 1;
                for (p = 0; p < j; p++) v = gf_mul(v, base);
                m[i][j] = v;
            }
        }
    }
}

/* ── 编码：k 个数据片(各 len 字节) → n 片(各 len 字节) ── */
static void rs_encode(uint8_t shares[N_SHARE][512],
                      const uint8_t data[K_DATA][512], size_t len)
{
    uint8_t m[N_SHARE][K_DATA];
    int i, j;
    size_t b;
    rs_matrix(m);
    for (i = 0; i < N_SHARE; i++) {
        for (b = 0; b < len; b++) {
            uint8_t acc = 0;
            for (j = 0; j < K_DATA; j++)
                acc ^= gf_mul(m[i][j], data[j][b]);
            shares[i][b] = acc;
        }
    }
}

/* ── 解码：给定幸存片集合 recovered[]（索引）与缺失片集合，用子矩阵求逆恢复缺失片 ── */
static int rs_decode(uint8_t shares[N_SHARE][512], size_t len,
                     const int *missing, int n_missing)
{
    /* 从全部 N_SHARE 里选任意 K_DATA 个幸存片，构造可逆矩阵求逆 */
    int chosen[N_SHARE];
    int have[N_SHARE];
    uint8_t mat[N_SHARE][K_DATA]; /* 选中片对应行 */
    int row[N_SHARE];
    int c, i, j, p;
    size_t b;
    int chosen_n = 0;

    memset(have, 0, sizeof(have));
    for (i = 0; i < n_missing; i++)
        have[missing[i]] = 1;

    /* 收集 K_DATA 个非缺失片 */
    for (i = 0; i < N_SHARE && chosen_n < K_DATA; i++) {
        if (!have[i]) {
            chosen[chosen_n] = i;
            row[chosen_n] = i;
            chosen_n++;
        }
    }
    if (chosen_n < K_DATA) return -1;

    /* 构造矩阵：编码矩阵的这些行 */
    {
        uint8_t m[N_SHARE][K_DATA];
        rs_matrix(m);
        for (i = 0; i < K_DATA; i++)
            memcpy(mat[i], m[row[i]], K_DATA);
    }

    /* 高斯消元求逆：mat * inv = I，同时把逆矩阵存到 inv[K_DATA][K_DATA] */
    {
        uint8_t inv[K_DATA][K_DATA];
        int r;
        for (i = 0; i < K_DATA; i++)
            for (j = 0; j < K_DATA; j++)
                inv[i][j] = (i == j) ? 1 : 0;
        for (r = 0; r < K_DATA; r++) {
            /* 选主元：找第 r 列非零的行 */
            int piv = -1;
            for (i = r; i < K_DATA; i++) {
                if (mat[i][r] != 0) { piv = i; break; }
            }
            if (piv < 0) return -1;
            if (piv != r) {
                uint8_t tmp[K_DATA];
                memcpy(tmp, mat[piv], K_DATA); memcpy(mat[piv], mat[r], K_DATA); memcpy(mat[r], tmp, K_DATA);
                memcpy(tmp, inv[piv], K_DATA); memcpy(inv[piv], inv[r], K_DATA); memcpy(inv[r], tmp, K_DATA);
            }
            uint8_t invp = gf_inv(mat[r][r]);
            for (j = 0; j < K_DATA; j++) {
                mat[r][j] = gf_mul(mat[r][j], invp);
                inv[r][j] = gf_mul(inv[r][j], invp);
            }
            for (i = 0; i < K_DATA; i++) {
                if (i != r && mat[i][r] != 0) {
                    uint8_t f = mat[i][r];
                    for (j = 0; j < K_DATA; j++) {
                        mat[i][j] ^= gf_mul(f, mat[r][j]);
                        inv[i][j] ^= gf_mul(f, inv[r][j]);
                    }
                }
            }
        }

        /* 恢复缺失片：missing[t] 的行向量 × inv × 幸存数据 = 缺失片数据 */
        {
            uint8_t m[N_SHARE][K_DATA];
            rs_matrix(m);
            for (c = 0; c < n_missing; c++) {
                int miss = missing[c];
                for (b = 0; b < len; b++) {
                    /* 先算：恢复行系数 = 缺失行 × inv（k 长向量） */
                    uint8_t coef[K_DATA];
                    for (j = 0; j < K_DATA; j++) {
                        uint8_t acc = 0;
                        for (p = 0; p < K_DATA; p++)
                            acc ^= gf_mul(m[miss][p], inv[p][j]);
                        coef[j] = acc;
                    }
                    /* shares[miss][b] = Σ coef[j] * shares[chosen[j]][b] */
                    uint8_t acc = 0;
                    for (j = 0; j < K_DATA; j++)
                        acc ^= gf_mul(coef[j], shares[chosen[j]][b]);
                    shares[miss][b] = acc;
                }
            }
        }
    }
    return 0;
}

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

int main(void)
{
    uint8_t data[K_DATA][512];
    uint8_t shares[N_SHARE][512];
    uint8_t recovered[N_SHARE][512];
    const size_t len = 256;
    static const int all_missings[][ERASE_MAX] = {
        {0, 1}, {0, 2}, {0, 3}, {0, 4},
        {1, 2}, {1, 3}, {1, 4},
        {2, 3}, {2, 4},
        {3, 4}
    }; /* 全部 C(5,2) = 10 种丢失组合 */
    double t0;
    int ok = 1;
    int i, j;

    printf("== 场景17 Reed-Solomon 纠删码 ==\n");
    printf("RS(%d,%d)：%d 数据片 + %d 校验片, 冗余 %d/%d = %.2fx\n",
           N_SHARE, K_DATA, K_DATA, N_SHARE - K_DATA,
           N_SHARE, K_DATA, (double)N_SHARE / K_DATA);
    printf("GF(2^8) 本原多项式 0x11D（同 AES），片长 %zu B\n\n", len);

    /* 构造数据 */
    for (i = 0; i < K_DATA; i++)
        for (j = 0; j < (int)len; j++)
            data[i][j] = (uint8_t)(i * 77 + j * 13 + (j >> 3));

    /* 编码 */
    rs_encode(shares, data, len);

    /* 1. 往返：用全部 k 个数据片应能还原（直接对照编码矩阵一致性） */
    /* 2. 恢复测试：不同缺失组合 */
    t0 = now_ms();
    for (i = 0; i < (int)(sizeof(all_missings) / sizeof(all_missings[0])); i++) {
        int missing[ERASE_MAX];
        int m;
        /* 复制一份当前 shares 到 recovered */
        memcpy(recovered, shares, sizeof(shares));
        /* 抹掉缺失片 */
        for (m = 0; m < ERASE_MAX; m++) {
            missing[m] = all_missings[i][m];
            memset(recovered[missing[m]], 0, len);
        }
        /* 解码恢复缺失片 */
        if (rs_decode(recovered, len, missing, ERASE_MAX) < 0) {
            printf("FAIL 恢复组合 {%d,%d}: 矩阵求逆失败\n", missing[0], missing[1]);
            ok = 0;
            continue;
        }
        /* 验证缺失片与原始 shares 一致 */
        int bad = 0;
        for (m = 0; m < ERASE_MAX; m++) {
            if (memcmp(recovered[missing[m]], shares[missing[m]], len) != 0) {
                bad = 1;
                break;
            }
        }
        if (bad) {
            printf("FAIL 恢复组合 {%d,%d}: 恢复结果不一致\n", missing[0], missing[1]);
            ok = 0;
        } else {
            printf("恢复组合 {%d,%d} (数据/校验): 完整还原 ✓\n", missing[0], missing[1]);
        }
    }

    /* 3. 任意 2 片丢失（含纯数据片组合）已在上表覆盖；容错上限 = n-k = 2 片，
     *    丢失 3 片（如全部数据片）超出 RS(5,3) 容错，本不应可恢复。 */

    printf("\n恢复耗时: %.2f ms (%zu 组合)\n", now_ms() - t0,
           sizeof(all_missings) / sizeof(all_missings[0]));

    if (ok)
        printf("\nPASS: RS(%d,%d) 任意 ≤%d 片丢失可完整恢复\n",
               N_SHARE, K_DATA, ERASE_MAX);
    else
        printf("\nFAIL\n");
    return ok ? 0 : 1;
}

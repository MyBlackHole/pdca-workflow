#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <signal.h>
#include <unistd.h>

/*
 * 复现 "malloc_consolidate(): invalid chunk size" 堆校验失败
 *   或 glibc 2.44: "corrupted size vs. prev_size"
 *
 * 崩溃日志来源: mysqld (xtrabackup 完成时 SIGABRT signal 6)
 * 根本原因: 堆 chunk header 被破坏（缓冲区溢出 / use-after-free）
 *
 * 原理:
 *   A 和 B 是相邻的普通 chunk (> max_fast).
 *   1. free(A) → 进入 unsorted bin, B 的 PREV_INUSE 被清空,
 *      B->prev_size = A->chunk_size
 *   2. 破坏 A 的 size 字段 (模拟堆溢出)
 *   3. free(B) → PREV_INUSE=0 → 向后合并 →
 *      校验 chunksize(A) == prev_size 失败 → ABORT
 */

static void sigabrt(int sig) {
    (void)sig;
    fprintf(stderr, "\n✓ 成功捕获 SIGABRT — 堆校验失败已触发!\n");
    _exit(0);
}

int main(void)
{
    /* 大量填充 tcache (glibc 2.44 tcache 容量比 7 大) */
    int fill_count = 128;
    void **fillers = malloc(fill_count * sizeof(void*));
    void *A, *B, *guard;
    int i;

    signal(SIGABRT, sigabrt);  /* 优雅捕获错误 */

    fprintf(stderr, "=== [PDCA] 复现 堆合并时 chunk size 校验失败 ===\n\n");
    fprintf(stderr, "崩溃来源: mysqld (xtrabackup 完成时 SIGABRT signal 6)\n");
    fprintf(stderr, "根因: 堆 chunk header 被破坏 (溢出/UAF)\n");
    fprintf(stderr, "glibc 旧版报错: malloc_consolidate(): invalid chunk size\n");
    fprintf(stderr, "glibc 2.44 报错: corrupted size vs. prev_size\n\n");

    /* ================================================================ */
    /* 阶段 1: 分配 A + B + guard (从 top chunk)                         */
    /* ================================================================ */
    A = malloc(0x80);
    B = malloc(0x80);
    guard = malloc(0x10);
    if (!A || !B || !guard) { perror("malloc"); return 1; }

    size_t szA = *(size_t *)((uintptr_t)A - 8) & ~7UL;
    size_t szB = *(size_t *)((uintptr_t)B - 8) & ~7UL;
    fprintf(stderr, "[1] A=%p (sz=%#lx) B=%p (sz=%#lx) guard=%p\n",
            A, szA, B, szB, guard);

    /* ================================================================ */
    /* 阶段 2: 大量填充+释放同大小 chunk (填满 tcache 并溢出到闲置链表)*/
    /* ================================================================ */
    fprintf(stderr, "\n[2] 填充 %d 个同大小 chunk (填满 tcache)...\n", fill_count);
    for (i = 0; i < fill_count; i++) {
        fillers[i] = malloc(0x80);
        if (!fillers[i]) return 1;
    }
    for (i = 0; i < fill_count; i++) free(fillers[i]);
    fprintf(stderr, "    tcache 已满, 后续 free 绕过 tcache\n");

    /* ================================================================ */
    /* 阶段 3: free(A) → tcache 满 → 进入 unsorted bin                   */
    /*         glibc 自动清空 B 的 PREV_INUSE, 设置 B->prev_size        */
    /* ================================================================ */
    fprintf(stderr, "\n[3] free(A) → unsorted bin (tcache 满)...\n");
    free(A);

    uintptr_t bchunk = (uintptr_t)B - 0x10;
    size_t B_prev = *(size_t *)bchunk;
    size_t B_sz   = *(size_t *)(bchunk + 8);
    fprintf(stderr, "    B->prev_size=%#lx, B->size=%#lx (PREV_INUSE=%lu)\n",
            B_prev, B_sz, B_sz & 1UL);

    /* ================================================================ */
    /* 阶段 4: 破坏 A 的 size 字段 (模拟堆溢出)                           */
    /*         A 在 unsorted bin 中, 改写其 size 使与 prev_size 不匹配   */
    /* ================================================================ */
    uintptr_t achunk = (uintptr_t)A - 0x10;
    size_t *A_sz = (size_t *)(achunk + 8);
    size_t orig_szA = *A_sz;

    fprintf(stderr, "\n[4] 破坏 A 的 size 字段 (模拟堆溢出)...\n");
    fprintf(stderr, "    A chunk @ %p, size = %#lx → ", (void *)achunk, orig_szA);

    *A_sz = 0x41;  /* 改写为与 B->prev_size 不匹配的值 */
    fprintf(stderr, "%#lx (PREV_INUSE=%lu)\n", *A_sz, *A_sz & 1UL);

    /* ================================================================ */
    /* 阶段 5: free(B) → 检测到 PREV_INUSE=0 → 向后合并 → 校验失败     */
    /* ================================================================ */
    fprintf(stderr, "\n[5] free(B) → 触发向后合并...\n");
    fprintf(stderr, "    B->PREV_INUSE=0, prev_size=%#lx\n", B_prev);
    fprintf(stderr, "    → 定位前块 A, 校验 chunksize(A)=%#lx ?= prev_size=%#lx\n",
            *A_sz & ~7UL, B_prev);
    free(B);

    /* ================================================================ */
    /* 没触发 — 恢复现场                                                */
    /* ================================================================ */
    fprintf(stderr, "\n=== 未触发 (可能需要调整 corruption 值) ===\n");
    *A_sz = orig_szA;
    free(guard);
    free(fillers);
    return 0;
}

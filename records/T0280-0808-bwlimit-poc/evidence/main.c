#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <pthread.h>
#include <time.h>

#include "bwlimiter.h"

/* 速率档位 (bit/s)：4MB/s 与 32MB/s */
#define RATE_SLOW (4u * 1024 * 1024 * 8)
#define RATE_FAST (32u * 1024 * 1024 * 8)
#define BUF       16384

/* 每档传输总量：慢档 64MB，快档 512MB —— 保证 16s/16s 量级 */
#define DATA_SLOW (64ull * 1024 * 1024)
#define DATA_FAST (512ull * 1024 * 1024)

/* 并发公平性：4 线程各传 32MB @ 32MB/s 共享限流器 */
#define N_THREAD 4
#define DATA_CONC (32ull * 1024 * 1024)

#define WINDOWS 16 /* 平稳性分窗数 */

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

/* 在 buflen 块上做"传输"：先 wait 再模拟写。返回每秒字节数速率 */
static double run_single(const struct poc_bwcfg *cfg, uint64_t total,
                         double *win_rates)
{
    char buf[BUF];
    uint64_t done = 0;
    double t0 = now_ms();
    size_t win_i = 0;
    uint64_t win_start_done = 0;
    double win_start = t0;

    memset(buf, 'x', sizeof(buf));
    poc_bw_init(cfg);
    while (done < total) {
        size_t cl = (total - done > BUF) ? BUF : (size_t)(total - done);
        double now;

        poc_bw_wait(cl);
        /* 模拟写入（memcpy 不耗 IO 时间，纯测限流） */
        done += cl;
        (void)buf;

        now = now_ms();
        if (win_rates && win_i < WINDOWS && now - win_start >= 1000.0) {
            double dur = (now - win_start) / 1e3;
            win_rates[win_i++] =
                (double)(done - win_start_done) / dur;
            win_start = now;
            win_start_done = done;
        }
    }
    poc_bw_destroy();
    if (win_rates) {
        double dur = (now_ms() - win_start) / 1e3;
        if (win_i < WINDOWS && dur > 0)
            win_rates[win_i++] =
                (double)(done - win_start_done) / dur;
    }
    return (double)total / ((now_ms() - t0) / 1e3);
}

/* 多线程共享全局限流器：每线程各传总量, 记录各自耗时 */
typedef struct {
    const struct poc_bwcfg *cfg;
    uint64_t total;
    double secs;
} thr_arg;

static void *thr_run(void *p)
{
    thr_arg *a = p;
    char buf[BUF];
    uint64_t done = 0;
    double t0 = now_ms();

    memset(buf, 'y', sizeof(buf));
    while (done < a->total) {
        size_t cl = (a->total - done > BUF) ? BUF : (size_t)(a->total - done);
        poc_bw_wait(cl);
        done += cl;
        (void)buf;
    }
    a->secs = (now_ms() - t0) / 1e3;
    return NULL;
}

static double jain_index(double *v, int n)
{
    double sum = 0, sq = 0;
    int i;
    for (i = 0; i < n; i++) {
        sum += v[i];
        sq += v[i] * v[i];
    }
    return sum * sum / ((double)n * sq);
}

int main(void)
{
    int pass = 1;
    int a, rate_idx;
    struct { uint64_t rate; uint64_t total; const char *name; } rates[2] = {
        { RATE_SLOW, DATA_SLOW, "4 MB/s (64MB)" },
        { RATE_FAST, DATA_FAST, "32 MB/s (512MB)" },
    };
    const char *algo_name[POC_BW_ALGO_NUM] = { "动态窗口", "令牌桶" };

    printf("V1/V2: 单线程速率精度与平稳性\n");
    {
        struct poc_bwcfg cfg = {
            .algo = POC_BW_DYNWIN,
            .rate = 0, /* 未限流对照组 */
            .buflen = BUF,
        };
        double avg = run_single(&cfg, DATA_FAST, NULL);
        printf("  未限流对照: %8.2f B/s（机器写速上界参考）\n", avg);
    }
    for (rate_idx = 0; rate_idx < 2; rate_idx++) {
        for (a = 0; a < POC_BW_ALGO_NUM; a++) {
            struct poc_bwcfg cfg = {
                .algo = (enum poc_bw_algo)a,
                .rate = rates[rate_idx].rate,
                .burst = rates[rate_idx].rate / 8u, /* 1 秒突发 */
                .buflen = BUF,
            };
            double win[WINDOWS];
            double avg = run_single(&cfg, rates[rate_idx].total, win);
            double target = (double)rates[rate_idx].rate / 8.0;
            double dev = (avg - target) / target;
            int nwin = 0, i;
            double mean = 0, std = 0;

            for (i = 0; i < WINDOWS; i++) {
                if (win[i] > 0) {
                    mean += win[i];
                    nwin++;
                }
            }
            mean /= nwin;
            for (i = 0; i < WINDOWS; i++)
                if (win[i] > 0)
                    std += (win[i] - mean) * (win[i] - mean);
            std = sqrt(std / nwin);

            printf("  %s @ %-14s 实测 %8.2f B/s  偏差 %+5.2f%%  "
                   "分窗均值 %8.2f  标准差 %8.2f  (%.2f%%)\n",
                   algo_name[a], rates[rate_idx].name,
                   avg, dev * 100, mean, std, std / mean * 100);
            if (fabs(dev) > 0.05) {
                printf("    FAIL: 平均速率偏差超出 ±5%%\n");
                pass = 0;
            }
        }
    }

    printf("V3: 多线程共享限流（%d 线程 @ 32MB/s, 各 %lluMB）\n",
           N_THREAD, (unsigned long long)(DATA_CONC / (1024 * 1024)));
    {
        struct poc_bwcfg cfg = {
            .algo = POC_BW_DYNWIN,
            .rate = RATE_FAST,
            .burst = RATE_FAST / 8u,
            .buflen = BUF,
        };
        int t;

        for (a = 0; a < POC_BW_ALGO_NUM; a++) {
            pthread_t tid[N_THREAD];
            thr_arg arg[N_THREAD];
            double rates_t[N_THREAD];
            double total_rate;

            cfg.algo = (enum poc_bw_algo)a;
            poc_bw_init(&cfg);
            for (t = 0; t < N_THREAD; t++) {
                arg[t].cfg = &cfg;
                arg[t].total = DATA_CONC;
                pthread_create(&tid[t], NULL, thr_run, &arg[t]);
            }
            for (t = 0; t < N_THREAD; t++)
                pthread_join(tid[t], NULL);
            poc_bw_destroy();

            for (t = 0; t < N_THREAD; t++)
                rates_t[t] = (double)DATA_CONC / arg[t].secs;
            /* 总速率 = 总字节 / max(各线程耗时), 因共享限流器并发推进 */
            {
                double maxs = 0;
                for (t = 0; t < N_THREAD; t++)
                    if (arg[t].secs > maxs)
                        maxs = arg[t].secs;
                total_rate = (double)(N_THREAD * DATA_CONC) / maxs;
            }
            printf("  %s: 总速率 %.2f B/s（目标 %.0f）  超速%s  "
                   "公平指数 %.3f  各线程 %.2f/%.2f/%.2f/%.2f B/s\n",
                   algo_name[a], total_rate, (double)RATE_FAST / 8.0,
                   total_rate > (double)RATE_FAST / 8.0 * 1.05 ? "!" : "无",
                   jain_index(rates_t, N_THREAD),
                   rates_t[0], rates_t[1], rates_t[2], rates_t[3]);
            if (total_rate > (double)RATE_FAST / 8.0 * 1.05) {
                printf("    FAIL: 并发总速率超出上限 5%%\n");
                pass = 0;
            }
        }
    }

    printf("\nRESULT: %s\n", pass ? "ALL PASS" : "FAIL");
    return pass ? 0 : 1;
}

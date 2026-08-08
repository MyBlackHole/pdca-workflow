#include "bwlimiter.h"

#include <pthread.h>
#include <time.h>
#include <errno.h>

/* ---- 计时原语 ---- */
static uint64_t mono_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ull + (uint64_t)ts.tv_nsec / 1000ull;
}

static void sleep_us(uint64_t us)
{
    struct timespec ts = {
        .tv_sec = (time_t)(us / 1000000ull),
        .tv_nsec = (long)(us % 1000000ull) * 1000L,
    };
    while (nanosleep(&ts, &ts) == -1 && errno == EINTR)
        ;
}

/* ---- 全局状态（单一全局限流器，多线程共享，锁保护） ---- */
static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static struct {
    int    enabled;
    enum poc_bw_algo algo;
    uint64_t rate;   /* bit/s */
    uint64_t burst;  /* bit，令牌桶 */
    size_t   buflen; /* 字节 */

    /* 动态窗口状态 */
    uint64_t lamt;       /* 当前窗口累计写入字节 */
    uint64_t thresh;     /* 当前窗口阈值（字节） */
    uint64_t bwstart;    /* 窗口起始 us */
    int      bwstart_set;

    /* 令牌桶状态：允许写入的下一个时刻 us（带宽守恒推进） */
    uint64_t next_free;
    uint64_t burst_us; /* 允许提前消费的最大时长（突发） */
} g;

/* ---- 动态阈值窗口限流（镜像产品 bwlimit 语义） ---- */
static void dynwin_wait(size_t nbytes)
{
    uint64_t now, elapsed, wait_ideal, wait;

    if (!g.bwstart_set) {
        g.bwstart = mono_us();
        g.bwstart_set = 1;
    }
    g.lamt += nbytes;
    if (g.lamt < g.thresh)
        return;

    now = mono_us();
    elapsed = now - g.bwstart;
    wait_ideal = (uint64_t)((double)g.lamt * 8.0 / (double)g.rate * 1e6);
    wait = (wait_ideal > elapsed) ? wait_ideal - elapsed : 0;

    /* 自适应窗口：等待时间过长(≥1s)缩小阈值, 过短(<10ms)扩大阈值 */
    if (wait >= 1000000ull) {
        g.thresh /= 2;
        if (g.thresh < g.buflen / 4)
            g.thresh = g.buflen / 4;
    } else if (wait < 10000ull) {
        g.thresh *= 2;
        if (g.thresh > g.buflen * 8)
            g.thresh = g.buflen * 8;
    }

    if (wait > 0)
        sleep_us(wait);
    g.lamt = 0;
    g.bwstart = mono_us();
}

/* ---- 令牌桶（next_free 时间推进模型，无累积误差） ----
 * 每次写入 need bit 后，允许写入时刻推进 need/rate；
 * burst 允许提前消费 burst_us 的带宽（下次写入可早于当前时刻）。 */
static void token_wait(size_t nbytes)
{
    uint64_t need = (uint64_t)nbytes * 8u; /* bit */
    uint64_t now = mono_us();
    uint64_t adv_us; /* 本次写入推进的带宽时间 */
    uint64_t earliest;

    /* 突发上限：允许写入时刻最多提前 burst_us */
    earliest = (now > g.burst_us) ? now - g.burst_us : 0;
    if (g.next_free < earliest)
        g.next_free = earliest;

    if (g.next_free > now)
        sleep_us(g.next_free - now);

    adv_us = (uint64_t)((double)need / (double)g.rate * 1e6);
    g.next_free = (g.next_free > now ? g.next_free : now) + adv_us;
}

void poc_bw_init(const struct poc_bwcfg *cfg)
{
    pthread_mutex_lock(&g_mu);
    g.algo = cfg->algo;
    g.rate = cfg->rate;
    g.burst = cfg->burst ? cfg->burst : g.rate / 8u;
    g.buflen = cfg->buflen ? cfg->buflen : 16384;
    g.enabled = (g.rate > 0);
    g.lamt = 0;
    g.thresh = g.buflen;
    g.bwstart_set = 0;
    g.next_free = mono_us();
    g.burst_us = (uint64_t)((double)g.burst / (double)g.rate * 1e6);
    pthread_mutex_unlock(&g_mu);
}

void poc_bw_destroy(void)
{
    pthread_mutex_lock(&g_mu);
    g.enabled = 0;
    pthread_mutex_unlock(&g_mu);
}

void poc_bw_wait(size_t nbytes)
{
    if (nbytes == 0)
        return;
    pthread_mutex_lock(&g_mu);
    if (!g.enabled) {
        pthread_mutex_unlock(&g_mu);
        return;
    }
    if (g.algo == POC_BW_TOKEN)
        token_wait(nbytes);
    else
        dynwin_wait(nbytes);
    pthread_mutex_unlock(&g_mu);
}

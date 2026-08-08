#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>
#include <sys/socket.h>
#include <pthread.h>

/* 自研帧协议 + 单连接多路复用实证：
 *   备份引擎要支持"一个 TCP 连接上并发跑多个备份/恢复任务"，
 *   否则每个任务一条连接 → 连接数爆炸 + 头阻塞。多路复用
 *   (HTTP/2 式) 用流 ID 把单连接切成逻辑流，帧交织传输。
 *
 * 帧格式（全部大端）:
 *   [magic 4B: 0x46535231 "FSR1"]
 *   [len    4B: payload 字节数]
 *   [sid    2B: 流 ID]
 *   [type   1B: 0=数据 1=EOF]
 *   [flags  1B: 保留]
 *   [crc    4B: CRC32(magic..flags)]   ← 帧头校验
 *   [payload len B]                     ← 无帧尾校验（大流量下 CRC 只在头）
 * 帧头 16B 固定，粘包/半包统一经"累积缓冲 + 状态机"拆帧。
 * 验证：
 *   1. 多流交织后各流数据隔离、顺序完整（无串流/丢序）
 *   2. 粘包（多帧同批）与半包（帧被拆散）均能正确重组
 *   3. 帧头 CRC 校验：篡改流 ID 能检出
 *   4. 吞吐打印
 */

#define MAGIC 0x46535231u /* "FSR1" */
#define HDR_SZ 16
#define MAX_PAYLOAD 4096
#define N_STREAMS 4
#define CHUNKS_PER_STREAM 2000
#define CHUNK_PAYLOAD 64

static uint32_t crc32_table[256];
static void crc32_init(void)
{
    uint32_t i, j;
    for (i = 0; i < 256; i++) {
        uint32_t c = i;
        for (j = 0; j < 8; j++)
            c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
        crc32_table[i] = c;
    }
}
static uint32_t crc32_of(const uint8_t *p, size_t n)
{
    uint32_t c = 0xFFFFFFFFu;
    size_t i;
    for (i = 0; i < n; i++)
        c = crc32_table[(c ^ p[i]) & 0xFF] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

static void put32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v >> 24); p[1] = (uint8_t)(v >> 16);
    p[2] = (uint8_t)(v >> 8);  p[3] = (uint8_t)v;
}
static void put16(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v >> 8); p[1] = (uint8_t)v;
}
static uint32_t get32(const uint8_t *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8) | (uint32_t)p[3];
}
static uint16_t get16(const uint8_t *p)
{
    return (uint16_t)(((uint16_t)p[0] << 8) | p[1]);
}

/* 编码一帧到 out（含头），返回总长 */
static size_t frame_build(uint8_t *out, uint16_t sid, uint8_t type,
                          const uint8_t *payload, size_t plen)
{
    uint32_t hcrc;
    out[0] = (uint8_t)(MAGIC >> 24); out[1] = (uint8_t)(MAGIC >> 16);
    out[2] = (uint8_t)(MAGIC >> 8);  out[3] = (uint8_t)MAGIC;
    put32(out + 4, (uint32_t)plen);
    put16(out + 8, sid);
    out[10] = type;
    out[11] = 0;
    hcrc = crc32_of(out, 12); /* 头校验：magic..flags */
    put32(out + 12, hcrc);
    if (plen) memcpy(out + HDR_SZ, payload, plen);
    return HDR_SZ + plen;
}

/* 累积缓冲拆帧器 */
typedef struct {
    uint8_t buf[1 << 20];
    size_t len;
} Accum;

/* 尝试从累积缓冲拆出完整帧；成功填充 fhdr + 拷贝 payload 到 out（调用者提供，容量 ≥ plen） */
static int frame_try(Accum *a, uint8_t *fhdr, uint8_t *out,
                     size_t out_cap, size_t *plen)
{
    size_t need;
    if (a->len < HDR_SZ) return 0;
    if (get32(a->buf) != MAGIC) return -1; /* 魔数错 → 帧头损坏 */
    need = HDR_SZ + get32(a->buf + 4);
    if (a->len < need) return 0; /* 半包 */
    memcpy(fhdr, a->buf, HDR_SZ);
    *plen = get32(a->buf + 4);
    if (out && *plen <= out_cap)
        memcpy(out, a->buf + HDR_SZ, *plen);
    /* 先拷贝 payload 再移动缓冲，确保 out 指向的数据不被 memmove 破坏 */
    memmove(a->buf, a->buf + need, a->len - need);
    a->len -= need;
    return 1;
}

/* 校验帧头 CRC */
static int frame_hdr_ok(const uint8_t *fhdr)
{
    uint32_t ref = get32(fhdr + 12);
    return crc32_of(fhdr, 12) == ref;
}

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

/* 接收线程：拆帧，统计正确性 */
typedef struct {
    int fd;
    Accum *acc;
    uint64_t *got;
    uint64_t *seq;
    uint64_t *expected;
    int *eof;
    int *headerrs;
    int *fail;
    int *frames;
} RecvArg;

static void *recv_thread(void *arg)
{
    RecvArg *ra = arg;
    uint8_t *wbuf = malloc(1 << 16);
    uint8_t fhdr[HDR_SZ];
    uint8_t pbuf[MAX_PAYLOAD];
    size_t plen;
    int fd, rc, i;

    if (!wbuf) { ra->fail[0] = 1; return NULL; }
    while ((fd = read(ra->fd, wbuf, 1 << 16)) > 0) {
        size_t pos = 0;
        while (pos < (size_t)fd) {
            size_t take = (size_t)fd - pos;
            if (take > sizeof(ra->acc->buf) - ra->acc->len)
                take = sizeof(ra->acc->buf) - ra->acc->len;
            memcpy(ra->acc->buf + ra->acc->len, wbuf + pos, take);
            ra->acc->len += take;
            pos += take;
            while (1) {
                rc = frame_try(ra->acc, fhdr, pbuf, sizeof(pbuf), &plen);
                if (rc == 0) break;
                if (rc < 0) { (*ra->headerrs)++; break; }
                if (!frame_hdr_ok(fhdr)) {
                    printf("FAIL 帧头 CRC 校验失败\n");
                    ra->fail[0] = 1;
                    (*ra->headerrs)++;
                    continue;
                }
                uint16_t sid = get16(fhdr + 8);
                uint8_t type = fhdr[10];
                if (sid >= N_STREAMS) {
                    printf("FAIL 非法流 ID %u\n", sid);
                    ra->fail[0] = 1;
                    continue;
                }
                if (type == 0) {
                    uint64_t seq = ra->seq[sid];
                    if (seq >= CHUNKS_PER_STREAM) {
                        printf("FAIL 流 %d 超量数据帧\n", sid);
                        ra->fail[0] = 1;
                    } else {
                        for (i = 0; i < CHUNK_PAYLOAD; i++) {
                            uint8_t exp = (uint8_t)((sid << 4) ^ (seq + i));
                            if (pbuf[i] != exp) {
                                printf("FAIL 流 %d 块 %llu 内容错位 (i=%d)\n",
                                       sid, (unsigned long long)seq, i);
                                ra->fail[0] = 1;
                                break;
                            }
                        }
                    }
                    ra->got[sid]++;
                    ra->seq[sid]++;
                } else if (type == 1) {
                    ra->expected[sid] = ra->seq[sid];
                    ra->eof[sid]++;
                } else {
                    printf("FAIL 未知帧类型 %u\n", type);
                    ra->fail[0] = 1;
                }
                (*ra->frames)++;
            }
        }
    }
    free(wbuf);
    return NULL;
}

int main(void)
{
    int sv[2];
    uint8_t *snd = malloc((HDR_SZ + MAX_PAYLOAD) * 16);
    Accum acc = { {0}, 0 };
    uint8_t fhdr[HDR_SZ];
    size_t plen;
    uint64_t per_stream_expected[N_STREAMS];
    uint64_t per_stream_got[N_STREAMS];
    uint64_t per_stream_seq[N_STREAMS]; /* 下一期望序号 */
    int per_stream_eof[N_STREAMS];
    uint64_t bytes_sent = 0;
    double t0, t0_done;
    int rc, i, frames = 0, headerrs = 0;
    int ok = 1;

    memset(per_stream_expected, 0, sizeof(per_stream_expected));
    memset(per_stream_got, 0, sizeof(per_stream_got));
    memset(per_stream_seq, 0, sizeof(per_stream_seq));
    memset(per_stream_eof, 0, sizeof(per_stream_eof));
    crc32_init();

    printf("== 场景16 帧协议多路复用 ==\n");
    printf("帧格式: magic(4)+len(4)+sid(2)+type(1)+flags(1)+crc(4)=16B 头 + payload\n");
    printf("多路复用: %d 逻辑流 × %d 块 × %dB 交织于单连接\n\n",
           N_STREAMS, CHUNKS_PER_STREAM, CHUNK_PAYLOAD);

    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) {
        printf("FAIL socketpair\n");
        return 1;
    }

    /* 启动接收线程（边发边收，避免写阻塞死锁） */
    {
        RecvArg ra;
        pthread_t th;
        ra.fd = sv[1];
        ra.acc = &acc;
        ra.got = per_stream_got;
        ra.seq = per_stream_seq;
        ra.expected = per_stream_expected;
        ra.eof = per_stream_eof;
        ra.headerrs = &headerrs;
        ra.fail = &ok;
        ra.frames = &frames;
        pthread_create(&th, NULL, recv_thread, &ra);

        /* 发送端：N 流交织写（真实并发由主循环交错 chunk 模拟交织） */
        t0 = now_ms();
        for (int chunk = 0; chunk < CHUNKS_PER_STREAM; chunk++) {
            for (int s = 0; s < N_STREAMS; s++) {
                uint8_t payload_buf[CHUNK_PAYLOAD];
                size_t flen;
                /* 每块内容 = 流ID + 序号，用于验证顺序 */
                for (i = 0; i < CHUNK_PAYLOAD; i++)
                    payload_buf[i] = (uint8_t)((s << 4) ^ (chunk + i));
                flen = frame_build(snd, (uint16_t)s, 0, payload_buf, CHUNK_PAYLOAD);
                /* 每次 write 只写一帧的一部分（模拟半包），确保拆帧器处理粘包/半包 */
                size_t sent = 0;
                while (sent < flen) {
                    size_t cut = (size_t)((chunk * 7 + s * 3 + sent) % 5) + 1; /* 1..5 字节小写 */
                    size_t n = cut;
                    if (n > flen - sent) n = flen - sent;
                    if (write(sv[0], snd + sent, n) != (ssize_t)n) {
                        printf("FAIL write\n");
                        return 1;
                    }
                    sent += n;
                }
                bytes_sent += flen;
            }
        }
        /* 各流 EOF 帧 */
        for (int s = 0; s < N_STREAMS; s++) {
            size_t flen = frame_build(snd, (uint16_t)s, 1, NULL, 0);
            if (write(sv[0], snd, flen) != (ssize_t)flen) return 1;
            bytes_sent += flen;
        }
        shutdown(sv[0], SHUT_WR);

        /* 等接收线程结束 */
        pthread_join(th, NULL);
        t0_done = now_ms();
    }

    printf("\n拆帧结果:\n");
    for (int s = 0; s < N_STREAMS; s++) {
        printf("  流 %d: 收 %llu 数据帧, 期望 %llu → %s, EOF 到达: %s\n", s,
               (unsigned long long)per_stream_got[s],
               (unsigned long long)CHUNKS_PER_STREAM,
               per_stream_got[s] == CHUNKS_PER_STREAM ? "完整 ✓" : "不完整 ✗",
               per_stream_eof[s] >= 1 ? "✓" : "✗");
        if (per_stream_got[s] != CHUNKS_PER_STREAM) ok = 0;
        if (per_stream_eof[s] < 1) ok = 0;
    }
    printf("  帧头 CRC 错误检出: %d\n", headerrs);

    /* 篡改检测：改一个帧头的 sid，应被 CRC 检出（重发一轮最小帧） */
    {
        uint8_t one[64];
        uint8_t pbuf[MAX_PAYLOAD];
        size_t flen = frame_build(one, 0, 0, (const uint8_t *)"ab", 2);
        one[8] ^= 0x01; /* 篡改 sid 最高字节 */
        memset(&acc, 0, sizeof(acc));
        memcpy(acc.buf, one, flen);
        acc.len = flen;
        rc = frame_try(&acc, fhdr, pbuf, sizeof(pbuf), &plen);
        if (rc == 1 && !frame_hdr_ok(fhdr)) {
            printf("篡改 sid → CRC 检出 ✓\n");
        } else {
            printf("FAIL: 篡改 sid 未被 CRC 检出\n");
            ok = 0;
        }
    }

    printf("\n吞吐: %.1f MB/s (%.0f 帧/s)\n",
           (double)bytes_sent / (1024 * 1024) / ((t0_done - t0) / 1e3),
           (double)frames / ((t0_done - t0) / 1e3));

    if (ok)
        printf("\nPASS: 多流数据隔离/顺序完整、粘包/半包重组正确、帧头 CRC 检出篡改\n");
    else
        printf("\nFAIL\n");
    free(snd);
    close(sv[0]);
    close(sv[1]);
    return ok ? 0 : 1;
}

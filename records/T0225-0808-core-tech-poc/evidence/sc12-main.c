#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/* 零拷贝传输实证：
 *   同一份文件数据经 127.0.0.1 回环 socket 发到对端，对比三种路径的吞吐：
 *     V1 用户态副本：read() → 用户缓冲 → write()  (2 次用户态拷贝)
 *     V2 sendfile：  内核态直接 fd→socket（用户态零拷贝）
 *     V3 splice：    fd→pipe→socket（内核态管道零拷贝）
 * 零拷贝的价值：备份大流量（全量备份、恢复写盘）避免 GB 级数据反复进出用户态，
 * 降低 CPU 占用并提升吞吐。断言 V2/V3 吞吐均 ≥ 2 倍 V1。
 */

#define DATA_SIZE (1024ull * 1024 * 1024) /* 1GB 传输量 */
#define CHUNK     65536
#define PORT_BASE 37000

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

/* 服务器端：持续 recv 丢弃，直到子进程关闭连接得到 EOF */
static void server_drain(int fd)
{
    char buf[CHUNK];
    ssize_t n;
    while ((n = recv(fd, buf, sizeof(buf), 0)) > 0)
        ;
}

/* 客户端：以指定路径从 fd 传输 DATA_SIZE 字节到 socket */
static int client_send(int cfd, int ffd, int mode, double *t_ms)
{
    double t0 = now_ms();
    if (mode == 0) {
        /* V1 用户态副本 */
        char *buf = malloc(CHUNK);
        ssize_t r, w;
        off_t off = 0;
        if (!buf) return -1;
        while (off < (off_t)DATA_SIZE) {
            r = pread(ffd, buf, CHUNK, off);
            if (r <= 0) { free(buf); return -1; }
            w = 0;
            while (w < r) {
                ssize_t n = write(cfd, buf + w, (size_t)(r - w));
                if (n <= 0) { free(buf); return -1; }
                w += n;
            }
            off += r;
        }
        free(buf);
    } else if (mode == 1) {
        /* V2 sendfile */
        off_t off = 0;
        while (off < (off_t)DATA_SIZE) {
            ssize_t s = sendfile(cfd, ffd, &off, CHUNK);
            if (s <= 0) return -1;
        }
    } else {
        /* V3 splice：fd→pipe→socket */
        int pfd[2];
        off_t off = 0;
        if (pipe(pfd) < 0) return -1;
        while (off < (off_t)DATA_SIZE) {
            ssize_t s = splice(ffd, &off, pfd[1], NULL, CHUNK, 0);
            if (s <= 0) { close(pfd[0]); close(pfd[1]); return -1; }
            ssize_t w = splice(pfd[0], NULL, cfd, NULL, (size_t)s, 0);
            if (w <= 0) { close(pfd[0]); close(pfd[1]); return -1; }
        }
        close(pfd[0]);
        close(pfd[1]);
    }
    *t_ms = now_ms() - t0;
    return 0;
}

static int run_pipe(int mode, double *t_ms)
{
    int lfd, cfd, ffd;
    struct sockaddr_in addr;
    socklen_t alen = sizeof(addr);
    pid_t pid;
    char path[] = "/tmp/poc-zc-XXXXXX";
    int status = 0;
    int tpipe[2];

    if (pipe(tpipe) < 0) return -1;
    lfd = socket(AF_INET, SOCK_STREAM, 0);
    if (lfd < 0) return -1;
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)(PORT_BASE + mode));
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (bind(lfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) return -1;
    if (listen(lfd, 1) < 0) return -1;

    pid = fork();
    if (pid < 0) return -1;

    if (pid == 0) {
        /* 子进程 = 客户端 */
        double t;
        int rc;
        close(tpipe[0]);
        close(lfd);
        cfd = socket(AF_INET, SOCK_STREAM, 0);
        if (cfd < 0) _exit(2);
        if (connect(cfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) _exit(3);
        ffd = mkstemp(path);
        if (ffd < 0) _exit(4);
        unlink(path);
        if (ftruncate(ffd, (off_t)DATA_SIZE) < 0) _exit(5);
        rc = client_send(cfd, ffd, mode, &t);
        if (rc == 0) {
            ssize_t n = write(tpipe[1], &t, sizeof(t));
            (void)n;
            _exit(0);
        }
        _exit(10 + mode);
    }

    /* 父进程 = 服务器 */
    close(tpipe[1]);
    cfd = accept(lfd, (struct sockaddr *)&addr, &alen);
    if (cfd < 0) return -1;
    server_drain(cfd);
    close(cfd);
    close(lfd);
    {
        ssize_t n = read(tpipe[0], t_ms, sizeof(*t_ms));
        if (n != (ssize_t)sizeof(*t_ms)) return -1;
    }
    close(tpipe[0]);
    waitpid(pid, &status, 0);
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) return -1;
    return 0;
}

int main(void)
{
    double t_copy = 0, t_sendfile = 0, t_splice = 0;
    double mb_copy, mb_sf, mb_sp;
    int ok = 1;

    printf("== 场景12 零拷贝传输 ==\n");
    printf("传输量: %llu MB @ 127.0.0.1 回环\n\n",
           (unsigned long long)(DATA_SIZE / (1024 * 1024)));

    if (run_pipe(0, &t_copy) < 0) {
        printf("FAIL V1 用户态副本\n");
        return 1;
    }
    if (run_pipe(1, &t_sendfile) < 0) {
        printf("FAIL V2 sendfile\n");
        return 1;
    }
    if (run_pipe(2, &t_splice) < 0) {
        printf("FAIL V3 splice\n");
        return 1;
    }

    mb_copy = (double)DATA_SIZE / (1024 * 1024) / (t_copy / 1e3);
    mb_sf = (double)DATA_SIZE / (1024 * 1024) / (t_sendfile / 1e3);
    mb_sp = (double)DATA_SIZE / (1024 * 1024) / (t_splice / 1e3);

    printf("V1 用户态副本 read+write: %.1f ms → %.1f MB/s\n",
           t_copy, mb_copy);
    printf("V2 sendfile（内核态直发）: %.1f ms → %.1f MB/s\n",
           t_sendfile, mb_sf);
    printf("V3 splice（管道零拷贝）:   %.1f ms → %.1f MB/s\n",
           t_splice, mb_sp);

    printf("\nsendfile/用户态 = %.2fx\n", mb_sf / mb_copy);
    printf("splice/用户态   = %.2fx\n", mb_sp / mb_copy);

    if (!(mb_sf >= 1.5 * mb_copy)) {
        printf("FAIL AC-1: sendfile 加速比 %.2f < 1.5\n", mb_sf / mb_copy);
        ok = 0;
    }
    if (!(mb_sp >= 1.5 * mb_copy)) {
        printf("FAIL AC-1: splice 加速比 %.2f < 1.5\n", mb_sp / mb_copy);
        ok = 0;
    }

    if (ok)
        printf("\nPASS: 零拷贝（sendfile/splice）吞吐 ≥ 1.5 倍用户态副本（回环已近内存带宽）\n");
    else
        printf("\nFAIL\n");
    return ok ? 0 : 1;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <gmssl/tls.h>
#include <gmssl/error.h>

#define CHUNK 16384

static void pr_seq(const char *tag, TLS_CONNECT *c) {
    fprintf(stderr, "[%s] client_seq=", tag);
    for (int i = 0; i < 8; i++) fprintf(stderr, "%02x", c->client_seq_num[i]);
    fprintf(stderr, " server_seq=");
    for (int i = 0; i < 8; i++) fprintf(stderr, "%02x", c->server_seq_num[i]);
    fprintf(stderr, "\n");
}

static void *server_thread(void *arg) {
    int listenfd = (int)(long)arg;
    int connfd = accept(listenfd, NULL, NULL);
    if (connfd < 0) { perror("accept"); return NULL; }
    TLS_CTX ctx;
    tls_ctx_init(&ctx, TLS_protocol_tlcp, 0);
    tls_ctx_set_ca_certificates(&ctx, "gmssl_bench/ca.pem", 4);
    tls_ctx_set_tlcp_server_certificate_and_keys(&ctx,
        "gmssl_bench/server.pem", "gmssl_bench/server_sign.key", "bench",
        "gmssl_bench/server_kenc.key", "bench");
    TLS_CONNECT conn;
    tls_init(&conn, &ctx);
    tls_set_socket(&conn, connfd);
    fprintf(stderr, "[server] accept...\n");
    int r = tlcp_do_accept(&conn);
    fprintf(stderr, "[server] handshake r=%d\n", r);
    pr_seq("server", &conn);
    if (r != 1) { exit(1); }

    uint8_t *buf = malloc(CHUNK);
    size_t got = 0, gotn = 0;
    uint64_t need;
    r = tls_recv(&conn, (uint8_t *)&need, sizeof(need), &gotn);
    fprintf(stderr, "[server] recv size r=%d gotn=%zu need=%llu\n", r, gotn, (unsigned long long)need);
    pr_seq("server", &conn);
    while (got < need) {
        size_t n = (need - got) < CHUNK ? (need - got) : CHUNK;
        r = tls_recv(&conn, buf, n, &gotn);
        if (r != 1) {
            fprintf(stderr, "[server] recv data FAILED at got=%zu\n", got);
            pr_seq("server", &conn);
            exit(1);
        }
        got += gotn;
        if ((got % (16 * 1024 * 1024)) == 0) fprintf(stderr, "[server] got=%zu\n", got);
    }
    fprintf(stderr, "[server] ALL DATA OK got=%zu\n", got);
    pr_seq("server", &conn);
    return NULL;
}

int main(void) {
    int listenfd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(24441);
    if (bind(listenfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) { perror("bind"); return 1; }
    if (listen(listenfd, 1) < 0) { perror("listen"); return 1; }
    pthread_t th;
    pthread_create(&th, NULL, server_thread, (void *)(long)listenfd);
    usleep(200000);

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) { perror("connect"); return 1; }
    TLS_CTX ctx;
    tls_ctx_init(&ctx, TLS_protocol_tlcp, 1);
    tls_ctx_set_ca_certificates(&ctx, "gmssl_bench/ca.pem", 4);
    tls_ctx_set_certificate_and_key(&ctx, "gmssl_bench/client.pem", "gmssl_bench/client_sign.key", "bench");
    TLS_CONNECT conn;
    tls_init(&conn, &ctx);
    tls_set_socket(&conn, sock);
    fprintf(stderr, "[client] connect...\n");
    int r = tlcp_do_connect(&conn);
    fprintf(stderr, "[client] handshake r=%d\n", r);
    pr_seq("client", &conn);
    if (r != 1) { return 1; }

    uint64_t need = 128 * 1024 * 1024;
    size_t sentn = 0;
    r = tls_send(&conn, (uint8_t *)&need, sizeof(need), &sentn);
    fprintf(stderr, "[client] send size r=%d sentn=%zu\n", r, sentn);
    pr_seq("client", &conn);

    uint8_t *buf = malloc(CHUNK);
    memset(buf, 0x5a, CHUNK);
    size_t sent = 0;
    while (sent < need) {
        size_t n = (need - sent) < CHUNK ? (need - sent) : CHUNK;
        r = tls_send(&conn, buf, n, &sentn);
        if (r != 1) {
            fprintf(stderr, "[client] send FAILED at sent=%zu\n", sent);
            pr_seq("client", &conn);
            exit(1);
        }
        sent += sentn;
    }
    fprintf(stderr, "[client] ALL SENT sent=%zu\n", sent);
    pr_seq("client", &conn);
    tls_cleanup(&conn);
    tls_ctx_cleanup(&ctx);
    close(sock);
    pthread_join(th, NULL);
    return 0;
}

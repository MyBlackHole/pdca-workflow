#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <gmssl/tls.h>

#define SMALL 8
#define COUNT 2000

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
    int r = tlcp_do_accept(&conn);
    if (r != 1) { fprintf(stderr, "[server] handshake FAILED\n"); exit(1); }
    pr_seq("server", &conn);

    uint8_t buf[SMALL];
    for (int i = 0; i < COUNT; i++) {
        size_t gotn = 0;
        r = tls_recv(&conn, buf, sizeof(buf), &gotn);
        if (r != 1) {
            fprintf(stderr, "[server] recv #%d FAILED gotn=%zu\n", i, gotn);
            pr_seq("server", &conn);
            exit(1);
        }
        if (gotn != SMALL || buf[0] != (uint8_t)i) {
            fprintf(stderr, "[server] recv #%d mismatch gotn=%zu first=%02x\n", i, gotn, buf[0]);
            exit(1);
        }
    }
    fprintf(stderr, "[server] ALL %d SMALL RECORDS OK\n", COUNT);
    pr_seq("server", &conn);
    return NULL;
}

int main(void) {
    int listenfd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(24442);
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
    int r = tlcp_do_connect(&conn);
    if (r != 1) { fprintf(stderr, "[client] handshake FAILED\n"); return 1; }
    pr_seq("client", &conn);

    uint8_t buf[SMALL];
    for (int i = 0; i < COUNT; i++) {
        buf[0] = (uint8_t)i;
        size_t sentn = 0;
        r = tls_send(&conn, buf, sizeof(buf), &sentn);
        if (r != 1) {
            fprintf(stderr, "[client] send #%d FAILED sentn=%zu\n", i, sentn);
            pr_seq("client", &conn);
            exit(1);
        }
    }
    fprintf(stderr, "[client] ALL %d SMALL RECORDS SENT\n", COUNT);
    pr_seq("client", &conn);
    tls_cleanup(&conn);
    tls_ctx_cleanup(&ctx);
    close(sock);
    pthread_join(th, NULL);
    return 0;
}

---
schema: pdca.asset/v1
id: ontology:pattern/gmssl-tlcp-mtls
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/gmssl-tlcp-mtls/1.0.0
summary: GMSSL 3.1.2 TLCP mTLS 支持速查与集成策略
source_task: F139
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/mtls-handshake]
attributes:
  - name: applicability
    desc: GMSSL 3.1.2 TLCP mTLS 集成场景
    constraint: ""
    testable_signal: 连接生命周期 vtable 抽象封装 GMSSL/OpenSSL 差异，编译链接通过
---

# GMSSL TLCP mTLS 支持速查
# GMSSL TLCP mTLS 支持速查

> 复用来源：records/0727-backup-transfer-encryption/

## GMSSL 3.1.2 TLCP mTLS 支持情况

预编译库路径：`third_party/gmssl/lib_{x86_64,aarch64}/libgmssl.so.3.1`

### mTLS 相关 API（全部存在）

| 功能 | 函数 | 说明 |
|---|---|---|
| 初始化 | `tls_ctx_init(&ctx, TLS_protocol_tlcp, is_client)` | TLCP 协议 |
| CA 证书 | `tls_ctx_set_ca_certificates(&ctx, cacertfile, depth)` | 服务端验证客户端 |
| 自身证书 | `tls_ctx_set_certificate_and_key(&ctx, chainfile, keyfile, pass)` | 单证书 |
| TLCP 双证书 | `tls_ctx_set_tlcp_server_certificate_and_keys(...)` | 签名+加密分离 |
| 握手 | `tlcp_do_connect(&conn)` / `tlcp_do_accept(&conn)` | TLCP 握手 |
| 认证请求 | `tls_record_set_handshake_certificate_request(...)` | 服务端请求客户端证书 |
| 认证证明 | `tls_record_set_handshake_certificate_verify(...)` | 客户端证明所有权 |
| 数据传输 | `tls_send()` / `tls_recv()` | 加密读写 |
| 关闭 | `tls_shutdown()` / `tls_cleanup()` | 清理 |

### API 不兼容（重点）

GMSSL v3 使用 `TLS_CTX` / `TLS_CONNECT`，**不是** OpenSSL 的 `SSL_CTX` / `SSL`：

```
OpenSSL                          GMSSL v3
─────────                        ─────────
SSL_CTX *ctx                     TLS_CTX ctx
SSL_CTX_new(TLS_method())        tls_ctx_init(&ctx, proto, is_client)
SSL_CTX_load_verify_locations()  tls_ctx_set_ca_certificates()
SSL_CTX_use_certificate_file()   tls_ctx_set_certificate_and_key()
SSL_new()                        tls_init() + tls_set_socket()
SSL_connect()                    tls_do_handshake() / tlcp_do_connect()
SSL_read()/SSL_write()           tls_recv()/tls_send()
```

### 集成策略

推荐**连接生命周期 vtable 抽象**方案：

```c
typedef struct tls_backend_ctx tls_backend_ctx_t;
typedef struct {
    int (*init_client)(tls_backend_ctx_t *, const char *);
    int (*init_server)(tls_backend_ctx_t *);
    int (*handshake)(tls_backend_ctx_t *, int fd);
    int (*send)(tls_backend_ctx_t *, const void *, int, int);
    int (*recv)(tls_backend_ctx_t *, void *, int, int);
    void (*close)(tls_backend_ctx_t *);
} tls_backend_vtable_t;
```

两个独立编译单元：
- `tls_backend_openssl.c` — 现有 OpenSSL mTLS
- `tls_backend_gmssl.c` — GMSSL TLCP

### TLCP 服务端双密钥

TLCP 要求服务端有两对 SM2 密钥：
- **签名密钥** (`signkey`)：消息签名
- **加密密钥** (`kenckey`)：密钥交换

tls-keygen 需生成：
```
sm2_host_sign.key / sm2_host_sign.crt
sm2_host_kenc.key / sm2_host_kenc.crt
```

### 密码套件

```
TLCP 1.1:   TLS_ECC_SM4_CBC_SM3  {0xE013}  (GB/T 38636-2020)
            TLS_ECDHE_SM4_GCM_SM3 {0xE051}
TLS 1.3:    TLS_SM4_GCM_SM3      {0x00C6}  (RFC 8998)
```

# T2044 三线各 1 mermaid（注记：TLS 2 子图合一）

> 源：`d3b99ac8` 的 `TLS/mTLS 全栈` + `签发加固` + `模板自解释` 三线，`file: libs/tls_keygen.c` `file: libs/rdb-config.h` 可溯

## 1. TLS/mTLS 全栈综合图（`init_config` 收口 + `mTLS fail-closed` 合一）

```mermaid
flowchart TD
    A[init_config 统一收口] --> B{tls_enable?}
    B -- 0=关闭 --> C[明文链路]
    B -- 1=开启 --> D{tls_algorithm}
    D -- TLS_SM4_GCM_SM3 --> E[SM4-GCM-SM3 国密]
    D -- TLS_AES_256_GCM_SHA384 --> F[AES 国际]
    E --> G[mTLS 证书校验]
    F --> G
    G -- 证书缺失/算法异常 --> H[fail-closed 阻断]
    G -- 正常 --> I[rpc/dmsbtex/libobk/fs-backup/oss 全链路 TLS]
    I --> J[reload 边界修复]
```
Source: `file: libs/rdb-config.h:allowed_values` `file: dmsbtex/network.c:tls_enable`

## 2. 签发加固回退图（`RAND_bytes` + `UAF` 时序）

```mermaid
sequenceDiagram
    participant K as tls_keygen
    participant R as RAND_bytes
    participant X as X509_set_pubkey
    participant E as EVP_PKEY

    K->>R: RAND_bytes 63 位随机 serial
    alt RAND 失败
        K->>K: clock_gettime回退
        K->>K: dump_openssl_errors
    end
    K->>X: X509_set_pubkey
    alt 成功
        K->>E: EVP_PKEY_free 延后
    else 失败
        K->>E: EVP_PKEY_free 补释放
        K->>K: dump_openssl_errors
    end
```
Source: `file: libs/tls_keygen.c:EVP_PKEY_free` `file: libs/tls_keygen.c:RAND_bytes`

## 3. 模板自解释通用图（`allowed_values` 3 类约束）

```mermaid
flowchart TD
    A[config_kv_def_t.allowed_values] --> B{类型}
    B -- 枚举 --> C[tls_algorithm]
    B -- BOOL --> D[0关闭/1开启 回退]
    B -- INT --> E[显示 min max 如 keepalive]
    B -- STR --> F[显示 最大长度4095]
    C --> G[cmd_gen 通用展示]
    D --> G
    E --> G
    F --> G
    G --> H[rdb.conf 注释 3 类约束行]
```
Source: `file: libs/rdb-config.h:allowed_values` `file: rdb-cfg/cli.c:cmd_gen`


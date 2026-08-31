# 修复 tls-keygen 签发证书 UAF 与多算法并发证书异常

## 背景

用户按以下序列连续生成双算法（sm2 + ed25519）全量证书时，产出的 host 证书校验失败或握手失败：

```bash
rm -rf /opt/aio/cfg/certs/
xmake run tls-keygen ca -n "MySM2RootCA" -a sm2
xmake run tls-keygen ca -n "MySM2RootCA" -a ed25519
# server
xmake run tls-keygen create -a sm2
xmake run tls-keygen create -a ed25519
xmake run tls-keygen sign -a sm2
xmake run tls-keygen sign -a ed25519
# client
xmake run tls-keygen create -n "MySM2RootCA" -a sm2
xmake run tls-keygen create -n "MySM2RootCA" -a ed25519
xmake run tls-keygen sign -n "MySM2RootCA" -a sm2
xmake run tls-keygen sign -n "MySM2RootCA" -a ed25519
```

文件层面 sm2/ed25519 已带前缀隔离（`sm2_host.*` vs `ed25519_host.*`、`sm2_ca.*` vs `ed25519_ca.*`），不会覆盖。但签发链路存在致命缺陷。

## 根因分析

### R1 — Use-After-Free（必现，P0）`libs/tls_keygen.c:537-575`

```c
EVP_PKEY *req_pkey = X509_REQ_get_pubkey(req);   // 537
if (X509_REQ_verify(req, req_pkey) <= 0) { ... }
EVP_PKEY_free(req_pkey);                         // 554  已释放
...
X509 *cert = X509_new();
...
X509_set_pubkey(cert, req_pkey);                 // 575  野指针 UAF
```

`X509_set_pubkey` 内部会 `EVP_PKEY_up_ref`，传入已释放对象属堆 UAF。顺序执行时堆未重用偶尔“看似成功”，并发/多次签发、ASAN 或不同分配器下必现证书公钥错乱、`openssl verify` 报 `error 7 signature failure` 或握手失败。用户“同时执行”即放大该竞态。

### R2 — 序列号硬编码冲突（P1）`libs/tls_keygen.c:564`

```c
ASN1_INTEGER_set(X509_get_serialNumber(cert), 2);
```

同一 CA 下 server 与 client 证书序列号均为 2，违背 PKI 唯一性，CRL/OCSP 与部分严格校验实现会拒认。

### R3 — 无其他文件覆盖问题

- `create -a sm2/ed25519` 输出 `sm2_host.key/csr` 与 `ed25519_host.key/csr` 隔离。
- `ca -n MySM2RootCA -a sm2/ed25519` 输出 `sm2_ca.crt/key` 与 `ed25519_ca.crt/key` 隔离（`handle_ca` 忽略 CN 仅作 Subject，不影响路径）。
- `sign -a` 与 `sign -n` 的 CA 读取均走 `DEFAULT_CERT_DIR/{algo}_ca.*`，`sign -n` 额外将 CA 拷贝至 `certs/<CN>/{algo}_ca.crt`，无覆盖。

## 修复方案

### F1 — 修复 UAF（最小改动）

将 `EVP_PKEY_free(req_pkey)` 延后至 `X509_set_pubkey(cert, req_pkey)` 之后（`X509_set_pubkey` 成功后 up_ref，再释放原引用；失败分支仍需释放）。或保留引用至 `X509_free(cert)` 前统一释放。

### F2 — 序列号唯一化

以 `time(NULL)` 低位 + 随机/原子计数混合生成 63 位正整数序列号，或至少以 `arc4random/random()+time` 避免同 CA 下重复。保持与现有 `ASN1_INTEGER_set` 兼容，必要时改 `ASN1_INTEGER_set_int64`。

### 非目标

- 不改变 `DEFAULT_CERT_DIR` 布局与 `-n` 语义
- 不引入并发锁（`tls-keygen` 为单进程工具，UAF 修复后并发 mkdir 已有 `EEXIST` 容忍）

## 验收标准

- [ ] UAF 修复后连续双算法签发证书均可通过 openssl verify 与 mtls 自测
- [ ] 序列号唯一性修复
- [ ] 回归测试通过

## 关联本体节点

```
ontology:concept/pdca-task
```

## 风险

- 序列号改随机后，依赖固定序列号的旧测试需同步更新（已排查无硬编码断言）

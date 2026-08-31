---
schema: pdca.asset/v1
id: ontology:pitfall/tls-keygen-sign-uaf-serial
type: pitfall
layer: Knowledge
status: active
summary: tls-keygen 签发链路 UAF 与序列号硬编码导致并发证书异常
source_task: T0454
relations:
  specializes: [ontology:pitfall]
  guides: [ontology:entity/x509-certificate]
attributes:
  - name: applicability
    desc: 使用 libs/tls_keygen.c 签发宿主机证书（tls_keygen_sign_with_algo）的 sm2/ed25519 双算法签发
    constraint: ""
    testable_signal: 单进程内连续签发多张 host 证书（sm2+ed25519×server/client）后，openssl verify 均 OK 且 serial 唯一、pubkey 与 CSR 一致
---

# tls-keygen 签发链路 UAF 与序列号硬编码陷阱

> 来源：T0454-0831-research-last-two-commits 调研 6195ba5d（B-T0451）与 740d55f0（F-139）引入-修复链；根因代码 `libs/tls_keygen.c:537-575`，修复提交 `6195ba5d`。

## 陷阱 1：Use-After-Free — 先 free 再 set_pubkey（P0，必现）

`tls_keygen_sign_with_algo` 原实现：

```c
EVP_PKEY *req_pkey = X509_REQ_get_pubkey(req);  // 537
X509_REQ_verify(req, req_pkey);
EVP_PKEY_free(req_pkey);                        // 554 已释放
...
X509 *cert = X509_new();
ASN1_INTEGER_set(...);
...
X509_set_pubkey(cert, req_pkey);                // 575 野指针 UAF
```

`X509_set_pubkey` 内部 `EVP_PKEY_up_ref`，传入已释放对象属堆 UAF。单次签发时堆未重用偶尔“看似成功”，连续签发（`sm2×2 + ed25519×2`）或 ASAN/不同分配器下必现 `pubkey 与 CSR 不一致`、`openssl verify` 报 `error 7 signature failure`、mTLS 握手失败。并发/连续执行放大堆扰动。

**修复**：将 `EVP_PKEY_free(req_pkey)` 延后至 `X509_set_pubkey` 成功之后；失败分支补 free。见 `6195ba5d` diff：

```c
X509 *cert = X509_new();
if (!cert) { EVP_PKEY_free(req_pkey); ... }
...
if (X509_set_pubkey(cert, req_pkey) != 1) { EVP_PKEY_free(req_pkey); ... }
EVP_PKEY_free(req_pkey);
```

**检测**：`rm -rf /opt/aio/cfg/certs/ && xmake run tls-keygen ca -n MySM2RootCA -a sm2/ed25519 && create/sign 循环 4 次 && openssl verify -CAfile <CA> <host.crt>`；或 `libs/tests/tls_keygen_test` 与 `test/tls_test.sh`。

## 陷阱 2：序列号硬编码 2 — 同 CA 下多证书冲突（P1）

```c
ASN1_INTEGER_set(X509_get_serialNumber(cert), 2);
```

同一 CA 下 server 与 client 证书序列号均为 2，违背 PKI 唯一性，CRL/OCSP 与严格校验实现拒认。

**修复**：`RAND_bytes` 生成 63 位随机正整数，失败回退 `time+pid+random` 混合，改 `ASN1_INTEGER_set_int64`：

```c
long long serial = 0; unsigned char rnd[8];
if (RAND_bytes(rnd, sizeof(rnd))==1) { for (...) serial=(serial<<8)|rnd[i]; serial&=0x7fffffffffffffffLL; }
if (serial==0) { serial=time(NULL)^getpid()^random(); if(serial<0) serial=-serial; if(serial==0) serial=1; }
ASN1_INTEGER_set_int64(X509_get_serialNumber(cert), serial);
```

**注意**：`random()` 未显式 `srandom` 时低熵，回退仅兜底；主路径依赖 `RAND_bytes`。

## 引入-修复链

- **引入**：`740d55f0`（F-139，2026-08-28）TLS/mTLS 全栈整合，`libs/tls_keygen.c` 重构引入上述两缺陷。
- **修复**：`6195ba5d`（B-T0451，2026-08-31）2 文件 33 行修复，`tls_keygen_version 1.0.0.1->1.0.0.2`。
- **重叠文件**：仅 `libs/tls_keygen.c` 与 `xmake.lua`；其余 4178 文件无交集，确认为引入-修复关系而非并行特性。

## 审查要点（适用于 tls_keygen 变更）

1. 凡 `X509_REQ_get_pubkey` / `EVP_PKEY_*` 必审 `free` 与后续 `up_ref` 时序；`X509_set_pubkey` 前对象必须有效。
2. `ASN1_INTEGER_set` 硬编码序列号一律视为缺陷；同 CA 场景必须随机或单调计数。
3. 连续双算法签发（`sm2/ed25519 × server/client`）为必跑回归；单算法单张证书无法暴露堆扰动。
4. squash 合并提交（如 F-139 含 0bf741f8..fef11220 区间 10+ 子提交）审查时需穿透到子提交 diff，不可仅看合并后统计。

## 关联

- 提交：`6195ba5d`（B-T0451）、`740d55f0`（F-139）
- 任务：T0451-0831-tls-keygen-uaf-fix（已归档）、T0454-0831-research-last-two-commits（本次）
- 测试：`libs/tests/tls_keygen_test`（10 passed）、`test/tls_test.sh`（4/4 passed）

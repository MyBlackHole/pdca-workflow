---
schema: pdca.asset/v1
id: T0392-0826-mtls-comprehensive-review
phase: do
type: review-report
source_ids: [T0391-0826-tls-cert-min-proto-version]
---

# mTLS 全面安全审查报告（T0392）

## 0. 范围与方法
- 覆盖模块：`rpc`（aio-speed 工具链）、`dmsbtex`、`libobk`（sbt）、`rdbcomm`、`libs/tls_cert.c`（TLS 库核心）、`libs/tls_keygen.c`（工具）。
- 审查维度：①配置 fail-closed ②握手强制 ③降级拒绝 ④算法白名单 ⑤证书/CA 绑定 ⑥最低 TLS 版本；并下沉 OpenSSL 层核心。
- 方法：解析路径 grep、握手强制逻辑走读、`SSL_CTX_new` 全仓覆盖性扫描、回归测试复验。
- 关联任务：T0388/T0389/T0390（rdb config fail-closed 系列，已归档）；**T0391（F1 修复，已归档）**。

## 1. 总体结论
**五道核心防线（非法配置、握手强制、降级拒绝、算法白名单、证书/CA 绑定）全部 fail-closed 一致，无高危缺陷。** 唯一中危项 F1（生产上下文未显式设最低 TLS 版本）已在 T0391 修复并验证；F2–F5 为低危加固/一致性项（见 §6）。

## 2. 六维度逐项审查

### ① 配置 fail-closed（达标）
- 5 处 `sec_get_bool(..._MTLS_ENABLED)` 解析失败硬失败：
  - `rpc/rpc-config.cpp:189`、`dmsbtex/dmsbtex/network.c:106`、`libobk/lib/sbt/libobk.c`（`sbt_server_tls_config_init`）、`rdbcomm/rdbcommd-main.c:296`、`rdbcomm/rdbcomm-main.c:609`。
- CLI 非法值拒绝（非零退出）：`rpc/main.cpp:240`、`rpc/rpc-client.cpp:1215`、`rdbcomm/rdbcomm-main.c:522`、`dmsbtex/main.c:685`、`libobk/main.c:256`（`--mtls-enable=2` 一律拒绝）。
- 测试：dmsbtex AC-3a、rpc tool_integration L152 覆盖。

### ② 握手强制（达标）
- **rpc**：mtls_enabled 时客户端未请求证书或 ctx 缺失 → `HS_ERR_MTLS_REQUIRED`（`rpc/rpc-server.cpp:284-303`）；未握手业务帧 → 拒绝（:400）。
- **dmsbtex**：`!sbt_server_ctx` → `DM_HS_ERR_MTLS_UNAVAILABLE`（`dmsbtex/network.c:211`）；明文业务帧 → 拒绝（`dmsbtex/main.c:271`）。
- **libobk**：`!sbt_server_ctx` → 拒绝（`oracleCmdTbl.c:119`）。
- **rdbcomm**：无 ctx 拒绝握手 + 未握手业务帧拒绝（`rdbcomm/server.c:498/562`）；**无 plain 回退分支**，严格 MTLS-when-configured。

### ③ 降级拒绝（达标，无静默降级）
- 客户端结果码一律要求 `*_OK_MTLS`：`rpc/rpc-io.cpp:110`、`libobk/lib/libobk.c:162`、`rdbcomm/rdbcomm-client.c:199`，非 MTLS 结果 → 失败。
- 服务端"按需降级"分支（`rpc/rpc-server.cpp:348` 回 `HS_OK_PLAIN`）不会静默降级：客户端侧一律要求 MTLS，结果不一致即失败。
- 测试：rpc_own_handshake_test L285（T0349 F1）、mixed_mtls_integration AC-6。

### ④ 算法白名单 fail-closed（达标）
- 未知算法一律拒 + 服务端显式 `tls_algorithm` 锁定唯一值：`rpc:248-280`、`dmsbtex/network.c:225/241`、`oracleCmdTbl.c:132/147`、`rdbcomm/server.c:506/518`。

### ⑤ 证书/CA 双向绑定（达标，强）
- `tls_cert_verify_peer_cn`（`libs/tls_cert.c:196`）：先 `!preverify_ok` 短路（OpenSSL 链校验/过期/吊销先过），再比对对端证书 **issuer CN == 协商 ca_cn**，不等即拒。
- 双算法 slot 均生效；每次握手写 `mtls_auth` AuditLog（`tls_cert.c:757`）。

### ⑥ 最低 TLS 版本（F1，已修复 via T0391）
- **修复**：`libs/tls_cert.c` `tls_cert_slot_create` 在 `SSL_CTX_new` 成功后新增 `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)`，失败 fail-closed（`SSL_CTX_free` + 返回 `TLS_CERT_ERR_SSL_CREATE`）。server/client 共用一处，覆盖全部生产上下文。
- 回归测试 `tls_cert_min_proto_version_enforced`（`libs/tests/tls_cert_test.c`）：经 `tls_cert_get_ssl_ctx` 取 AES/SM4 两 slot 的 `SSL_CTX`，断言 `SSL_CTX_get_min_proto_version == TLS1_3_VERSION`，**20/20 通过**。可判别性：无修复时 OpenSSL4 默认最低 TLS1.2，断言必失败。

## 3. TLS 库核心深度（libs/tls_cert.c）
- **套件白名单**：仅 `TLS_SM4_GCM_SM3` / `TLS_AES_256_GCM_SHA384`（AEAD + 前向安全）；`SSL_CTX_set_ciphersuites` 失败即 fail-closed（`tls_cert.c:93`）。
- **CRL 吊销**：`crl.pem` 存在时启用 `X509_V_FLAG_CRL_CHECK|CRL_CHECK_ALL`（`tls_cert.c:284`），被吊销证书 fail-closed（可选，见 F2）。
- **热加载安全**：`tls_cert_slot_reload`（`tls_cert.c:896`）重建后重定向 `SSL_CTX_set_app_data(slot->ca_cn)`，避免验证回调读悬空指针——正确规避已知陷阱。
- **审计**：每次握手记录成功/失败 + peer CN + IP。

## 4. 覆盖性审计（关键）
全仓生产 `.c/.cpp` 的 `SSL_CTX_new`（排除 third_party）仅出现在：
- `libs/tls_cert.c:236` ← 生产库**唯一**上下文创建点（F1 已修复）
- `libs/tls_keygen.c:1529/1534` ← 工具自身已设 `TLS1_3_VERSION`
- `libs/tests/tls_cert_test.c:627/842` ← 测试负向用例

=> rpc / dmsbtex / libobk / rdbcomm **无任何直接 `SSL_CTX_new`**，全部经 `tls_cert_init_*` / `*_handshake` / `*_ctx_acquire` 间接到达 `tls_cert_slot_create`。**F1 一处修复即覆盖全部生产上下文，无绕过路径。**

## 5. 边界与一致性
- `tls_cert_init_server` 不受 `mtls_enabled` 影响始终建 slot → 即便"可选 mTLS"模式，服务端 ctx 也锁 TLS1.3（合理）。
- `tls_cert_init_client` 在 `!mtls_enabled` 时直接返回不建 ctx（无影响）；启用时才走建 ctx 路径 → 受修复覆盖。
- 本系统只配置 TLS1.3 套件，无 TLS1.2 客户端，锁定最低版本不破坏互通。

## 6. 发现清单
| ID | 严重度 | 状态 | 说明 |
|----|--------|------|------|
| F1 | 中 | **已修复（T0391）** | 生产上下文未显式设最低 TLS 版本；已加 `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)` + 回归测试 |
| F2 | 低 | 建议 | CRL 仅当文件存在才启用，无 OCSP；高安全场景建议强制 |
| F3 | 低 | 建议 | `rpc/rpc-server.cpp:400` 对 `MT_GET_TIME` 做预握手豁免，mTLS 强制下仍可明文送达 |
| F4 | 低 | 建议 | `dmsbtex/dmsbtex/network.c:204` `dm_server_handshake` 不检查 `mtls_enabled`，强制外包给 `main.c:271`，与其余三者不一致 |
| F5 | 低 | 设计说明 | `tls_cert_verify_peer_cn` 仅校 issuer CN，未校 subject CN/SAN 白名单（标准 mTLS PKI 语义） |

## 7. 总体 verdict
**mTLS 安全基线总体达标**：五道防线 fail-closed 一致，无高危缺陷；F1 已闭环。建议将 F2–F5 作为独立后续任务按需收敛。

## 8. 后续建议
- F1 已闭环，代码提交待用户显式"提交"指令（沿用 T0388/T0389/T0390 惯例，PDCA 仓与代码仓均尚未提交）。
- 可选任务：F2（强制 CRL/OCSP）、F3（收紧 GET_TIME 豁免）、F4（收敛 dmsbtex 强制逻辑）、F5（subject 白名单，按需）。

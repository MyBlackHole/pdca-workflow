# rpc 混合模式：服务端未配置时客户端兼容明文与密文，配置后强制密文 — 规格文档

## 问题陈述

- **现状**: `rpc` 首阶段协商已区分 `HS_OK_PLAIN / HS_OK_MTLS / HS_ERR_MTLS_REQUIRED`，但服务端 `mtls=0` 时客户端是否可同时以明文与密文建连、服务端 `mtls=1` 时是否强制密文未在单测矩阵中显式覆盖；`rpc/rpc-io.cpp:133` 的 `cert_dir+algorithm+ca_cn` 仅在 `HS_OK_MTLS` 时触发，`PLAIN` 时 `ca_cn` 为空且不尝试 `tls_cert`，该分支与 `server mtls` 开关的组合未被回归。
- **目标**: 混合模式可测且确定：`server mtls=0` → 客户端 `plain` 通且 `mtls`（若具备 `cert_dir`）亦通（按协商结果自适应，不强制）；`server mtls=1` → 客户端必须 `mtls` 通，缺证书或协商失败即建连失败，不回退明文。
- **差距**: 首阶段混合/强制分支的显式矩阵与单测缺口，`ca_cn` 空值语义与回退策略的文档化缺口。

## 解决方案

保持 `rpc_hs_server_accept` / `rpc_hs_client_negotiate` 现有帧，仅固化按需语义：`server mtls=0` 时 `cert_dir` 有即建 `tls_ctx`，按 `want_mtls` 回 `HS_OK_PLAIN`（`ca_cn` 空）或 `HS_OK_MTLS`（`ca_cn` 非空），`client` 按结果分流（`PLAIN` 直通，`MTLS` 需 `cert_dir` 完备否则失败不回退）；`server mtls=1` 时强制 `HS_OK_MTLS`（`tls_ctx` 必非空），`client` 任何 `want_mtls` 均 `MTLS` 且缺证书即失败，不回退。

## Seam 分析

### 测试接缝

- 在 `libs/rpc-handshake.{c,h}` 与 `rpc/rpc-io.{c,h}` 边界：`rpc_hs_client_negotiate` / `rpc_hs_server_accept` / `rpc_handshake_client_negotiate` 的首阶段分支与 `tls_cert` 调用点。
- 已有 `libs/tests/rpc_handshake_test.c` 覆盖 `PLAIN`/`MTLS` 单路径，缺 4 象限矩阵；`libs/tests/tls_cert_test.c` 已覆盖 `cert_dir` 初始化。
- 外部依赖：`socketpair` 内存管道，不依赖外网；证书复用 `libs/tests/certs` 的 `host` 前缀新生成。

### 声明的测试接缝

- seam: libs/tests/rpc_handshake_test.c -> rpc-handshake.h
- seam: libs/tests/tls_cert_test.c -> tls_cert.h

### 验收可测性

- 每个 AC 为 `socketpair` 4 象限之一，`pass` 为建连后 `write/read` 成功或按 `HS_ERR` 失败，`fail` 为相反。
- 边界：`server 0/1 x client 0/1` 4 象限、`ca_cn` 空、`cert_dir` 空、缺证书均可独立构造。

## 用户故事

1. 作为客户端开发者，服务端未配置 `mtls` 时，我想按 `want_mtls` 分别以明文或密文建连成功（`want_mtls=0` 走 `PLAIN`，`1` 走 `MTLS`），不被强制单一。
2. 作为客户端开发者，服务端配置 `mtls` 时，我想仅以密文建连成功，缺证书时明确失败，不回退明文。
3. 作为服务端开发者，我想 `mtls=0` 时按 `want_mtls` 回 `PLAIN`/`MTLS`（`cert_dir` 有即 `MTLS` 可选），`mtls=1` 时强制 `MTLS` 并校验。

## 实现决策

- **新增/修改的模块**: `libs/rpc-handshake.{c,h}`（固化 `server mtls` 开关与 `HS_OK_*` 的映射，`ca_cn` 空值语义注释）；`rpc/rpc-io.cpp`（`HS_OK_PLAIN` 回退分支注释与 `cert_dir` 完备性校验），`libs/tests/rpc_handshake_test.c`（增量 4 象限矩阵用例）。
- **模块接口定义**:

```c
int rpc_hs_server_accept(rpc_hs_session_t *s, int fd, const rpc_hs_server_config_t *cfg, tls_cert_ctx_t *tls_ctx, rpc_hs_result_t *r);
int rpc_hs_client_negotiate(rpc_hs_session_t *s, int want_mtls, uint16_t alg, rpc_hs_result_t *r);
int rpc_handshake_client_negotiate(rpc_io_t *io); // 内部按 r->result 分流 plain/tls
```

- **技术澄清**:
  - `server mtls=0` → 若 `cert_dir` 有则建 `tls_ctx`，按 `want_mtls` 回 `PLAIN`（`ca_cn` 空）或 `MTLS`（`ca_cn` 非空）；`cert_dir` 空则固定 `PLAIN`。`client` 按结果分流，`PLAIN` 不触 `tls_cert`，`MTLS` 需 `cert_dir` 完备否则失败。
  - `server mtls=1` → `tls_ctx` 必非空且 `cert_dir` 必有，强制 `HS_OK_MTLS`，`ca_cn` 为 `tls_cert_get_ca_cn` 首个非空 CN；`client` 任何 `want_mtls` 均按 `MTLS` 且缺证书即失败，不回退。
- **架构决策**: 首阶段明文协商 + `tls_cert` 按需升级，不新增帧字段，沿用 T0342 的 `common.h` 唯一常量。
- **数据模型变更**: 无。
- **API 合约**: 上述 3 接口行为不变，仅分支语义固化。

## 测试决策

- 仅测外部行为：`socketpair` 4 象限，断言 `result` 与 `read/write` 成功/失败，不测内部 `SSL` 细节。
- 被测模块：`libs/rpc-handshake` 与 `rpc/rpc-io` 的首阶段分流。
- 新增用例：`test_mixed_plain_server_plain_client`、`test_mixed_plain_server_mtls_client`、`test_forced_mtls_success`、`test_forced_mtls_no_cert_fail`。

## 验收标准

- [ ] AC-1: `server mtls=0` + `client want_mtls=0`（`cert_dir` 空或有）→ `HS_OK_PLAIN` 且 `plain write/read` 成功。
- [ ] AC-2: `server mtls=0` + `client want_mtls=1`（`cert_dir` 完备）→ `HS_OK_MTLS` 且 `tls write/read` 成功（按需密文）。
- [ ] AC-3: `server mtls=1` + `client mtls=1`（`cert_dir` 完备）→ `HS_OK_MTLS` 且 `tls write/read` 成功（强制密文）。
- [ ] AC-4: `server mtls=1` + `client` 缺 `cert_dir`/`ca_cn` → 建连失败，不回退明文。
- [ ] AC-5: `server mtls=1` + `client want_mtls=0`（`mtls=0` 但服务端强制）→ 仍 `HS_OK_MTLS` 且缺证书即失败，不回退。

## 范围外

- 不改 `tls_cert` 双格式与 `common.h` 统一（T0342 已交付）。
- 不改 `sec_*` 签名与证书轮转。
- 不引入重连/重试策略。

## 备注

- 与 T0342 正交：T0342 交付 `cert_dir` 强制与双格式，本任务交付首阶段混合/强制矩阵。
- `ca_cn` 空值在 `PLAIN` 为正常，不触发 `tls_cert`。

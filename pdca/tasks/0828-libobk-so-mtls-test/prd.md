# libobk 共享库(.so) mTLS 功能验证程序（模仿 RMAN SBT 路径）— 规格文档

## 问题陈述

- **现状**: libobk 是 Oracle RMAN SBT 备份库（构建产物 libsbt.so）。现有 `libobk/test/session_test.c` 仅**直接调用 mTLS 会话 API**（`sbt_session_client_init` / `sbt_session_server_handshake`）做握手测试，未覆盖"RMAN 类客户端经 SBT API（`sbtinit2`→`sbtbackup`→`sbtclose2`→`sbtend`）真实调用路径触发 mTLS"的场景。现有 `libobk/simulator/main.c`（rman-mock）虽模拟 RMAN 调用 SBT 接口，但仅设置明文 env，未启用 mTLS。
- **目标**: 开发一个独立测试程序，模仿 RMAN 经 SBT API 调用 libobk.so，在真实 SBT 调用路径下验证 mTLS 是否正常（握手成功、备份闭环、fail-closed）。
- **差距**: 缺少"经 SBT API 路径触发 mTLS"的端到端验证，无法确认 libobk 作为 SBT 库被 RMAN 类客户端使用时 mTLS 是否真正常。

## 解决方案

新增 `libobk/test/rman_mtls_test.c`（xmake test 目标 `libobk_rman_mtls_test`）：

1. 测试程序 `fork` 子进程作为 mTLS 服务端（复用 `sbt_server_tls_config_init` + `sbt_session_server_prepare` + `sbt_session_server_handshake`，与 `session_test` 同范式），父进程作为"模仿 RMAN"的客户端，调用 libobk 的 SBT 接口（`sbtinit2`→`sbtbackup`→`sbtclose2`→`sbtend`）发起备份。
2. 客户端启用 mTLS（env：`LIBOBK_CLIENT_MTLS_ENABLE=1`、`LIBOBK_CLIENT_TLS_ALGORITHM`、`RPC_TLS_CA_CERT`/`RPC_TLS_CLIENT_CERT`/`RPC_TLS_CLIENT_KEY`/`RPC_TLS_CERT_DIR`），连接到 fork 服务端（loopback）。
3. 服务端完成 mTLS 握手后，进入最小 activeio 控制帧响应循环，响应客户端的 open/close backup slice 请求，使客户端备份 API 完成闭环。
4. fail-closed：服务端 mTLS 关闭或证书/算法错配时，客户端 `sbtinit2` 必须失败（不降级明文）。
5. 证书复用 `libs/tests/certs`（`TEST_CERT_DIR`）。

## Seam 分析

### 测试接缝
- 测试直接调用 libobk 公开 SBT 客户端 API（`sbtinit2`/`sbtbackup`/`sbtclose2`/`sbtend`）与公开 mTLS 服务端 API（`sbt_server_tls_config_init`/`sbt_session_server_prepare`/`sbt_session_server_handshake`），经真实 SBT 调用路径触发 mTLS。
- 与 `session_test` 的区别：`session_test` 直接调会话 API；本测试经 SBT API（`sbtinit2` 内部调 `sbt_session_client_init`）触发，验证端到端 SBT 路径。
- 服务端在 `fork` 子进程内承载，隔离全局状态；loopback TCP 或 socketpair 直连。
- 证书复用 `TEST_CERT_DIR`，零外部依赖。

### 声明的测试接缝
- seam: libobk/test/rman_mtls_test.c -> libobk/lib/sbt/libobk.c
- seam: libobk/test/rman_mtls_test.c -> libobk/lib/logic/oracleCmdTbl.c

### 验收可测性
- 每用例明确 pass/fail：`sbtinit2`/`sbtbackup`/`sbtclose2`/`sbtend` 返回值、服务端成功 mTLS 握手信号、fail-closed 时 `sbtinit2` 非 0。
- 边界：mTLS 开/关、证书/算法错配，可独立构造。
- 分层：集成级（SBT API 路径）+ 复用既有会话 API 单元。

## 用户故事

1. 作为维护者，我希望有程序模仿 RMAN 经 SBT API 调用 libobk.so 验证 mTLS，以便确认 libobk 作为 SBT 库被 RMAN 类客户端使用时 mTLS 真正常。
2. 作为维护者，我希望测试含 fail-closed 用例，以便 mTLS 异常时不会静默降级明文。
3. 作为 CI，我希望该测试是 xmake test 目标，以便每次构建自动回归。

## 实现决策

**不涉及生产代码修改**（纯测试补充）。若测试暴露缺陷，修 bug 并记录。

- 被测模块：libobk SBT 客户端（`lib/sbt/libobk.c`：`sbtinit2`→`sbt_session_client_init` mTLS 触发）、libobk mTLS 服务端（`lib/logic/oracleCmdTbl.c`：`sbt_session_server_prepare`/`handshake`）。
- 新增文件：`libobk/test/rman_mtls_test.c`；`libobk/xmake.lua` 新增 `libobk_rman_mtls_test` 目标（`set_kind("binary")`、`add_files("test/rman_mtls_test.c")`、`add_deps("sbt","logger","tls_cert")`、`add_defines("TEST_CERT_DIR=...")`、`add_tests("default")`）。
- 客户端调用约定：`sbtinit2` 读取 `AIO_SERV_HOST`/`AIO_SERV_PORT`/`AIO_SERV_BACKUP_DIR` env 连接并 mTLS 握手；`sbtbackup`/`sbtclose2`/`sbtend` 走 mTLS 通道完成备份控制帧。
- 服务端：`fork` 子进程调 `sbt_server_tls_config_init(mtls_enabled=1)`+`sbt_session_server_prepare`，`accept` 后 `sbt_session_server_handshake`；随后最小 activeio 控制帧响应循环（手工构造 open/close backup slice 响应），使客户端闭环。
- 证书：复用 `libs/tests/certs`，客户端经 env 注入，服务端经 `cert_dir` 注入。
- 架构决策：无（不改变生产架构）。

## 测试决策

- 好测试定义：仅测 SBT API 外部行为与 mTLS 握手结果（返回值/是否降级），不测内部实现细节。
- 被测模块：libobk SBT 客户端 + mTLS 服务端握手。
- 先例：`session_test`（链接级 socketpair fork 服务端范式）、`knowledge/tls/link-level-mtls-test-pattern.md`。

## 验收标准

- [x] AC-1: mTLS 启用下，客户端 `sbtinit2` 返回 0（mTLS 握手成功）、`sbtbackup` 返回 0、`sbtclose2` 返回 0、`sbtend` 返回 0；服务端记录到成功 mTLS 握手并完成备份控制帧闭环 → 经过 SBT API 路径的 mTLS 备份闭环成功。（实测：`[PASS] AC-1 mTLS backup closed-loop via SBT API succeeded`）
- [x] AC-2: fail-closed（服务端 mTLS 关闭）：客户端 `sbtinit2` 返回非 0 且未建立明文会话 → 证明不降级。（实测：`[PASS] AC-2 fail-closed: server mTLS off -> client sbtinit2 rejected`，日志 `handshake: short read on negotiate response`）
- [x] AC-3: fail-closed（证书/算法错配）：服务端用错配算法或缺失客户端证书时，客户端 `sbtinit2` 返回非 0 → 证明握手强制校验。（实测：`[PASS] AC-3 fail-closed: algorithm mismatch -> client sbtinit2 rejected`，日志 `handshake: algorithm 0x0002 rejected by server lock (locked=0x0001)`）
- [x] AC-4: `xmake build` 与 `xmake test` 全部通过，该测试纳入全量 CI 且无回归。`libobk/xmake.lua` 已注册 `libobk_rman_mtls_test` 目标（`add_tests("default", {realtime_output = true})`）。正确调用格式为测试标识符 `目标名/组名`：`xmake test --root -y "libobk_rman_mtls_test/default"`（参考同仓库 `oss/test/xmake_go_test.sh` 的 `aio-oss-go-test/default` 写法；裸 target 名或 `组/目标名` 均会 `nothing to test`）。实测：`xmake build libobk_rman_mtls_test` 通过；`xmake test --root -y "libobk_rman_mtls_test/default"` 输出 `libobk_rman_mtls_test/default passed`、`100% tests passed, 0 test(s) failed out of 1`，连续两次稳定（AC-1/2/3 三条 [PASS]）。

## 范围外

- 不修改 libobk 生产代码 mTLS 实现。
- 不改动证书加载/握手协议/算法 profile 模型。
- 不做性能/压测；不验证 restore（`sbtrestore`/`sbtread2`）路径（本期仅备份闭环）。
- 不引入独立服务端二进制（FileTransferAgent）作为测试服务端。

## 备注

- 与 `0820-tls-session-integration-test`（AC-2 覆盖 libobk 会话 mTLS）的区别：本任务经 SBT API 路径（`sbtinit2` 等）触发 mTLS，验证端到端 SBT 调用下的 mTLS，而非直接调会话 API。
- 复用知识库 `knowledge/tls/link-level-mtls-test-pattern.md`（链接级 fork 服务端范式，已否决 fork+execl 工具二进制 E2E）。
- 证书 CN 约束：测试证书 ca_cn 必须匹配白名单（ED25519_Test_CA/SM2_Test_CA 风格），见 `link-level-mtls-test-pattern.md`。

---
*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*

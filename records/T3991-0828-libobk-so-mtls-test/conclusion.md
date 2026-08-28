---
schema: pdca.asset/v1
id: T3991-0828-libobk-so-mtls-test
phase: check
source_ids: [do-evidence.md]
---

## 上下文

任务目标：开发独立测试程序，模仿 RMAN 经 SBT API（`sbtinit2`→`sbtbackup`→`sbtclose2`→`sbtend`）调用 libobk.so（libsbt.so），在**真实 SBT 调用路径**下验证 mTLS 是否正常（握手成功、备份闭环、fail-closed）。现有 `session_test` 仅直接调会话 API，`simulator/main.c` 仅走明文，二者均未覆盖"经 SBT API 触发 mTLS"的端到端场景。

## 假设与结果

- 假设 H1：libobk 作为 SBT 库被 RMAN 类客户端调用时，mTLS 握手能在其内部 `sbt_session_client_init` 路径正常完成 → **结果：成立**（AC-1）。
- 假设 H2：服务端 mTLS 关闭时，客户端 SBT 调用必须失败且不降级明文 → **结果：成立**（AC-2）。
- 假设 H3：服务端算法锁与客户端算法错配时，握手必须被拒、客户端失败 → **结果：成立**（AC-3）。
- 假设 H4：测试可经 `xmake test` 注册并运行，纳入 CI → **结果：成立**（AC-4，目标已注册、构建与运行均通过）。

## 分析

- **AC-1** ✅ mTLS 启用下 `sbtinit2`/`sbtbackup`/`sbtclose2`/`sbtend` 全部返回 0，服务端 mTLS 握手成功且完成 open/close backup slice 业务帧闭环（证据 `do-evidence.md`：运行日志 `recvOpenBackupSliceResponse ok, peer[/tmp/] has done`、`retCode: 0`）。
- **AC-2** ✅ fail-closed：服务端不启用 mTLS 时，客户端 `sbtinit2` 返回非 0，未建立明文会话（证据 `do-evidence.md`：`handshake: short read on negotiate response: fd=4 expect=234`，因服务端纯明文、不回应 mTLS 协商帧）。
- **AC-3** ✅ fail-closed：服务端锁定 SM4（`locked=0x0001`）、客户端用 AES（`0x0002`）时被拒，客户端 `sbtinit2` 返回非 0（证据 `do-evidence.md`：`handshake: algorithm 0x0002 rejected by server lock (locked=0x0001)`）。
- **AC-4** ✅ `libobk/xmake.lua` 注册 `libobk_rman_mtls_test` 目标（`add_tests("default")`），`xmake build` 通过；经正确标识符 `目标名/组名` 调用 `xmake test --root -y "libobk_rman_mtls_test/default"` 输出 `libobk_rman_mtls_test/default passed`、`100% tests passed, 0 test(s) failed out of 1`，连续两次稳定（证据 `do-evidence.md`）。注：早期 `xmake test libobk_rman_mtls_test`（裸名）/`xmake test default/libobk_rman_mtls_test`（组/目标）均报 `nothing to test`，属调用格式错误而非测试失效——标识符须为 `目标名/组名` 且需 `--root -y`（同仓库 `oss/test/xmake_go_test.sh` 范式）。

## 适用边界

- 仅覆盖备份闭环（`sbtbackup`/`sbtclose2`/`sbtend`），未覆盖 restore（`sbtrestore`/`sbtread2`）路径（PRD 范围外）。
- 测试中为简化手工服务端，关闭了压缩（`AIO_ENABLE_COMPRESS=0`）；生产链路由框架自动压缩，本测试不验证压缩与 mTLS 的交互。
- 证书复用 `libs/tests/certs`（`TEST_CERT_DIR`），覆盖 AES 与 SM4 两组；未引入独立 `FileTransferAgent` 服务端二进制（PRD 范围外）。
- 端口用 loopback 固定范围（28081-28083），依赖 `fork` 子进程承载服务端、`waitpid` 清理。

## 下一轮建议

- 如需更高保真，可补 restore 路径的 mTLS 闭环用例，或用真实 `FileTransferAgent` 作为服务端做 E2E。
- 若后续改动 mTLS 握手/证书加载逻辑，本测试作为回归闸门可捕获 SBT API 路径下的退化。

## Verdict（草案，待 Ch5 用户确认后固化）

- outcome: confirmed
- reason: 三项核心 AC 连续两次运行稳定通过，fail-closed 行为（mTLS 关闭、算法错配）均验证充分；测试已纳入 xmake test CI 目标（`add_tests("default")`），正确调用 `xmake test --root -y "libobk_rman_mtls_test/default"` 输出 100% passed；早期 `nothing to test` 系调用格式错误（标识符须为 `目标名/组名` 且需 `--root -y`），非测试失效。结论有 `do-evidence.md` 运行日志、构建与 xmake test 记录支撑。
- verdict_id: V-T3991-0828-001
- at: 2026-08-28T13:50:00+08:00

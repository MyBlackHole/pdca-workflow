---
schema: pdca.knowledge/v1
title: 服务端启动期 mTLS 准备应收敛为可测 boot prepare 并 fail-closed
source: records/T3987-0827-server-mtls-cert-boot-failclosed/conclusion.md
---

## 可复用规则
- 服务端在 `mtls_enabled=1` 时必须在启动期构建 mTLS 上下文；若证书目录缺失或证书/CA 加载失败，应**启动期非 0 退出（fail-closed）**，不得降级为明文监听。
- 将启动期 TLS 准备逻辑收敛为一个**可单测的 boot prepare 函数**（返回码 / 上下文指针 + 错误），而非内联在主流程；主流程仅在 `mtls_enabled` 为真时把"准备失败"解释为启动失败。
- 边界：仅当 `mtls_enabled=1` 强制 fail-closed；`mtls_enabled=0`（明文模式）证书缺失仍允许明文，保持既有按需/明文语义不回归。
- 已正确的同构实现（dm-ftp/sbt 的 `sbt_session_server_prepare`）应保留并以单测固化，不作为改造点。

## 反模式（本次 T3987 修复）
- rdbcommd：cert_dir 为空时跳过 `tls_cert_init_server` 仅 `WarningLog` → fail-open。
- aio-speedd：证书加载失败把 `tls_ctx` 置空继续明文（注释"证书加载失败不阻止启动"）→ fail-open。

## 实现要点
- 共享 `tls_cert_init_server(mtls_enabled)` 在 mtls 启用且 cert_dir 空 / 加载失败返回非 0，语义保持不变，由 boot prepare 直接转发其返回码。
- rdbcommd：`rdbcommd_tls_boot_prepare` 用 `(ret!=0 || !ctx)` 双条件判据；主流程 `return EXIT_FAILURE`。
- aio-speedd：`aio_speedd_tls_boot_prepare` 失败时返回 NULL 且置错误码，主流程 `exit(EXIT_FAILURE)`；`tls_cert_init_server` 成功必返回非 NULL ctx，故 `ctx==NULL` 仅在 mtls 未启用时触发（明文，符合边界）。

## 测试模式
- 单测构造不存在 / 空 `cert_dir` 且 `mtls_enabled=1`，断言 boot prepare 返回非 0（或进程非 0 退出）；`mtls_enabled=0` 分支断言不强制（明文允许）。
- 既有 mTLS 集成测试（handshake_session_test、mixed_mtls_integration、session_test）须保持通过，验证正常握手路径不回归。

## 来源
T3987 四服务端 mTLS fail-closed 改造，rdbcommd/aio-speedd 新增 boot prepare，dm-ftp/sbt 逻辑本已正确并单测固化，经单测与集成测试验证。

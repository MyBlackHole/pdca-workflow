---
schema: pdca.asset/v1
id: T3987-0827-server-mtls-cert-boot-failclosed
phase: check
source_ids: [rdbcomm-boot-test, aio-speedd-boot-test, dmsbtex-session-test, libobk-session-test, rdbcomm-handshake-test, mixed-mtls-integration, convergence-map]
---

## 上下文
四服务端（rdbcommd、aio-speedd、dm-ftp、sbt）在 `mtls_enabled=1` 时依赖启动期 `tls_cert_init_server` 构建 mTLS 上下文。诊断发现 rdbcommd、aio-speedd 存在 fail-open：mtls 启用但证书缺失时仍以明文监听。本任务将其收敛为"mTLS 启用即 fail-closed"。

## 假设与结果
- 假设：`tls_cert_init_server` 在 `mtls_enabled=1` 且 cert_dir 空/加载失败返回非 0，语义不变。✅ 已由 rdbcommd/aio-speedd boot 测试间接钉死（mtls=1+缺失路径返回非 0）。
- 假设：dm-ftp/sbt 的 `sbt_session_server_prepare` 已正确 fail-closed。✅ 既有 session_test 含 `bad cert_dir prepare fail`/`no-downgrade reject` 且 ALL PASS。
- 结果：rdbcommd、aio-speedd 抽取可测的 boot prepare，mtls 启用+证书缺失 → 主流程非 0 退出；全部单测与既有 mTLS 集成测试通过。

## 分析
- **AC-1** ✅ rdbcommd `mtls_enabled=1` 且 cert_dir 缺失/证书加载失败时启动期返回非 0（`rdbcommd_tls_boot_prepare` 返回非 0，主流程 `return EXIT_FAILURE`，日志含 cert_dir 路径）（rdbcomm-boot-test）
- **AC-2** ✅ aio-speedd `mtls_enabled=1` 且证书加载失败时启动期 `exit(EXIT_FAILURE)`，日志含证书不可用错误（aio-speedd-boot-test）
- **AC-3** ✅ dm-ftp `mtls_enabled=1` 且证书缺失时 `sbt_session_server_prepare` 返回非 0，主流程退出（既有语义保持，session_test ALL PASS）（dmsbtex-session-test）
- **AC-4** ✅ sbt `mtls_enabled=1` 且证书缺失时 `sbt_session_server_prepare` 返回非 0，主流程退出（既有语义保持，session_test 退出码 0 PASS）（libobk-session-test）
- **AC-5** ✅ 四服务端 `mtls_enabled=0`（明文模式）且证书缺失仍允许明文启动：rdbcommd/aio-speedd boot 测试含 mtls=0 分支（`ctx==NULL` 不强制）；dmsbtex/libobk `no-downgrade reject` 验证明文允许且不误触发 fail-closed（rdbcomm-boot-test, aio-speedd-boot-test, dmsbtex-session-test）
- **AC-6** ✅ 单测覆盖 libs（经 rdbcommd/aio-speedd 间接调用 `tls_cert_init_server` 钉死）/dm-ftp/sbt/rdbcommd/aio-speedd 启动期 fail-closed 分支，全部 PASS（rdbcomm-boot-test, aio-speedd-boot-test, dmsbtex-session-test, libobk-session-test）
- **AC-7** ✅ `xmake build` 成功（warnings-as-errors 全绿，rdbcommd/aio-speedd 主程序与测试均链接通过）；既有集成测试 `rdbcomm_handshake_session_test: ALL PASS`、`mixed_mtls_integration: PASS` 无回归（rdbcomm-handshake-test, mixed-mtls-integration）

## 双轴审查（B4，含 secure-coding）
- **标准轴**：`-Werror` 全绿；无 `strcpy`/`sprintf`、无格式字符串注入（日志均为固定格式串+参数）；无空指针解引用/释放后使用；`ret` 仍被使用无未初始化告警。
- **安全轴（fail-closed）**：rdbcommd 用 `(ret!=0 || !server_ctx)` 双条件防御；aio-speedd 依赖 `tls_cert_init_server` 成功必返回非 NULL ctx，故 `boot_ctx==NULL` 仅在 mtls 未启用时触发（明文，符合边界，无 fail-open）。CWE-636（配置启用却 fail-open）已收口。日志仅含 cert_dir 路径，无密钥泄露，符合 `structured-mtls-failure-diagnostics`。
- **非阻塞建议**：aio-speedd 可加 `boot_ctx==NULL` 冗余判据与 rdbcommd 对称，当前逻辑安全，不阻塞。
- **Blocking = 0**。

## 适用边界
仅当 `mtls_enabled=1` 时强制 fail-closed；明文模式（mtls=0）证书缺失仍允许明文，保持既有按需/明文语义不回归。未改动客户端握手、算法白名单、国密后端。

## 下一轮建议
- 可选加固：aio-speedd 增加 `boot_ctx==NULL` 冗余判据。
- 后续可补 `libs/tests/tls_cert_test.c` 独立断言 `mtls_enabled=1 + 空/不存在 cert_dir → 返回非 0`（当前由 rdbcommd/aio-speedd 间接覆盖）。
- 关联 0823-oss-https-cert 的 oss Go 工具 mTLS 不属本次范围。

## Verdict
{
  "outcome": "confirmed",
  "reason": "四服务端启动期 fail-closed 已实现并经单测与集成测试验证，AC-1..AC-7 全部满足，双轴审查 Blocking=0。",
  "verdict_id": "T3987-verdict-20260827",
  "at": "2026-08-27T18:32:00+08:00"
}

# Triage Brief — T0335 补充 dmsbtex/libobk 会话路径独立集成测试

## 分类
- category: enhancement
- scenario_type: development（含测试产物，可回归验证）

## 查重
- 搜索 pdca/tasks 与 archive：历史任务（0814-dmsbtex-sbt-encryption、0818-mtls-rpc-session-followup、0819-dmsbtex-libobk-mtls、0819-sbt-rpc-session、0819-sbt-mtls-simplify）均为"接入/复用/简化"，无"会话路径独立集成测试补强"任务。
- out-of-scope 知识库未命中概念 "tls session integration test"。
- 结论：无重复。

## Claim 验证
- `dmsbtex/test/session_test.c`：仅 socketpair 明文 echo，未覆盖 TLS 配置。
- `libobk/test/session_test.c`：仅 socketpair 明文 echo，未覆盖 TLS 配置。
- `xmake` 已注册 `dmsbtex_session_test` 与 `libobk_session_test` 目标（可增量扩展）。
- T0333 已交付 `dmsbtex_tls_config_t`/`libobk_tls_config_t`/`struct sbtctx` TLS 字段及 `sbt_session_server_prepare/accept`/`sbt_session_client_init` 带 cfg 入参。
- 结论：claim 成立（缺独立测试覆盖 cfg 显式入参生效路径）。

## 方案
- 扩展 `dmsbtex/test/session_test.c` 与 `libobk/test/session_test.c`：mTLS 启用握手成功 / 明文通道 / 证书缺失失败 三类用例。
- 测试证书复用仓库既有 TLS 工具链/材料，不引入外部依赖。
- 不改生产代码；暴露缺陷则修 bug 并记录。

## 验收标准
- 见 prd.md：AC-1（dmsbtex mTLS 握手）、AC-2（libobk mTLS 握手）、AC-3（明文）、AC-4（证书缺失失败）、AC-5（build+test 全通过）。

## 建议
- 规模小、单目标，无需拆解子任务；无需 design.md（不改架构）。
- 是否进入 Do 需用户 P6 终审确认。
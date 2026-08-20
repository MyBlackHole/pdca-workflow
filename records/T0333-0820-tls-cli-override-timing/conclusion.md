---
schema: pdca.asset/v1
id: T0333-0820-tls-cli-override-timing
phase: check
source_ids:
  - ac1-rdb-config-diff-v4
  - ac1-rdb-config-test
  - ac2-tool-help-v2
  - ac2-invalid-alg-v2
  - ac3-rdbcomm-diff-v2
  - ac3-rpc-diff-v2
  - ac3-integration
  - ac4-sbt-diff-v2
  - ac4-session-test
  - ac5-build-v2
  - ac5-full-test-v3
---

## 上下文

工具 mTLS 开关/算法此前通过全局 CLI 覆盖状态（`sec_tool_tls_set_cli_overrides` + `cli_mtls_set` 等模块级 static）在 rdb-config 内实现，存在时序耦合与线程隐患；无 CLI 库（dmsbtex/libobk/timed_net_key）无宿主可承载配置。本次修正将 TLS 配置归属迁移至各工具/库自己的结构体，rdb-config 仅保留纯参数化通用解析 API。

## 假设与结果

- 假设 1：rdb-config 剥离 CLI 覆盖与工具专属字符串后，工具 mTLS 开关/算法查询行为不变（env/config/master 优先级正确）。
  **成立** — `sec_resolve_int`/`sec_resolve_str` 通用解析（env > 工具 section/key > 全局 section/key > 默认值），`rdb_config_test` 12 项断言通过（含新增 sec_resolve_str 五层：tool/global/env/fallback/默认）。
- 假设 2：CLI 覆盖语义保持"启动即加载默认值，参数解析后存在则覆盖"。
  **成立** — 四工具 main 在解析 CLI 后将覆盖值填入各自结构体（`client_options`/`server_options`/`rpc_config`），消费点从字段读取；`tool-help.log` 明确记载 `priority: CLI > environment > section > [security] > default`。
- 假设 3：非法算法值错误信息不变。
  **成立** — 四工具非法值仍报 `invalid --tls-algorithm: BAD_ALG`（ac2-invalid-alg-v2）。
- 假设 4：无 CLI 库经显式入参/字段生效 TLS 配置。
  **成立** — dmsbtex/libobk 服务端经 `dmsbtex_tls_config_t`/`libobk_tls_config_t` 显式传参，libsbt 客户端 TLS 配置移入 `struct sbtctx`，timed_net_key 用 `timed_net_key_tls_config_t` 局部 cfg。

## 分析

逐条 AC 判定：

- **AC-1（rdb-config 纯查询 + cli overrides 移除）**：通过。`sec_tool_tls_set_cli_overrides` 及相关全局 static 已删除；`sec_resolve_int/str` 不硬编码字符串，section/key/env 全部调用方传入；`ac1-rdb-config-diff-v4` 展示 diff，`ac1-rdb-config-test` 单元测试通过。
- **AC-2（help + 参数解析 + 非法值不变）**：通过。`ac2-tool-help-v2`/`ac2-invalid-alg-v2` 实测四工具 help 与非法值行为不变。
- **AC-3（工具集成、结构体传参、证书路径不再隐式查询）**：通过。`client_options`/`server_options`/`rpc_config` 字段承载；`ac3-rdbcomm-diff-v2`/`ac3-rpc-diff-v2` 展示变更；`ac3-integration` 集成测试通过。
- **AC-4（sbt-session/timed_net_key/dmsbtex/libobk 显式入参/字段生效）**：通过。`sbt-session.c/h` 已删除并并入 `dmsbtex/network`（`sbt_session_client_init/server_prepare/accept` 带 cfg 入参），grill 确认无需专项证据；`ac4-sbt-diff-v2` diff + `ac4-session-test` 覆盖。
- **AC-5（build + test 全通过，不修改证书加载/握手协议/profile 模型）**：通过。`ac5-build-v2`/`ac5-full-test-v3`：`xmake build` 通过，`xmake test` 38/38 通过；改动仅限配置读取与结构体承载层。

关键决策回顾：TLS 配置归属 = 各工具/库结构体持有（dmsbtex_tls_config_t / struct sbtctx 字段 / timed_net_key_tls_config_t / rpc_config·client_options·server_options），无模块级 static 全局 TLS 配置对象；rdb-config 仅提供通用解析 API。

## 失败原因

无（全部 AC 通过）。

## 适用边界

- 结论仅适用于 TLS 配置**读取与归属**；证书加载、握手协议、profile 模型未改动（AC-5 边界）。
- `sec_resolve_*` 返回的字符串指针由 env/store 持有，调用方不得 free 或修改；生命周期随进程/store。
- CLI 覆盖仅在四工具（rdbcomm/rdbcommd/aio-speed/aio-speedd）存在；无 CLI 库以显式入参承载。
- rdb-config 不硬编码任何工具 section/key/env 字符串，调用方需自行传入（配置 schema 常量集中在 rdb-config.h 宏）。

## 下一轮建议

- 若后续引入新工具，需按相同模式定义 TLS 配置结构体并调用 `sec_resolve_*`，勿在 rdb-config 内新增工具专属逻辑。
- 可考虑为 dmsbtex/libobk 会话路径补充独立集成测试（本次 grill 判定非必需）。
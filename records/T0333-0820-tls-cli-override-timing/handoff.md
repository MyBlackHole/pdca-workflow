## 当前状态

T0333 已完成 Check→Act（verdict: confirmed，disposition: not_reusable，无知识沉淀）。Do 阶段已完成：TLS 配置归属从 rdb-config 全局 static 迁移至各工具/库结构体，rdb-config 仅保留通用解析 API。

## 未完成事项

无。5 项 AC 全部通过（`xmake build` + `xmake test` 38/38）。

## 已知约束

- rdb-config 不硬编码任何 section/key/env 字符串，调用方须经 `SEC_GLOBAL_*`/`SEC_MASTER_*`/`*_ENV`/`RDBCOMM_*` 宏传入 `sec_resolve_int`/`sec_resolve_str`。
- `sec_resolve_*` 返回的字符串指针由 env/store 持有，调用方不得 free。
- `sbt-session.c/h` 已删除，功能并入 `dmsbtex/network`（`sbt_session_client_init/server_prepare/accept` 带 cfg 入参）。
- CLI 覆盖仅存在于 rdbcomm/rdbcommd/aio-speed/aio-speedd 四工具 main。

## 推荐的下一步

- 若引入新工具：定义 TLS 配置结构体 → main 解析 CLI/env 后填入 → 消费点从字段读取，勿新增 rdb-config 工具专属逻辑。
- 版本已升：rpc 3.6.4.20、rdbcomm 1.0.1.9（xmake.lua）。

## 关键上下文文件列表

- `libs/rdb-config.h` / `libs/rdb-config.c`：`sec_resolve_int/str` 通用解析 + `SEC_*` 宏
- `dmsbtex/network.h`：`dmsbtex_tls_config_t` + `sbt_tls_config_init`
- `libobk/include/libobk.h`：`struct sbtctx` TLS 字段 + `sbt_client_tls_config_init`
- `libobk/include/oracleCmdTbl.h`：`libobk_tls_config_t`
- `libs/timed_net_key.h`：`timed_net_key_tls_config_t`
- `rdbcomm/client.h` / `server.h`、`rpc/rpc-config.h`：工具侧 TLS 字段
- `records/T0333-0820-tls-cli-override-timing/conclusion.md`：结论文档

## suggested skills

- 下次处理工具 TLS/配置归属类任务：`verify-convergence`、`advance-phase`
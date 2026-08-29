---
schema: pdca.asset/v1
id: T0388-0826-rdb-config-failclosed-unify
phase: check
source_ids: [build-all, param_registry_test, rdb_config_test, rpc_config_test, libobk_session_test, impl-diff, convergence-map]
---

## 上下文
T0388 跟进 T0386：统一 rdb config 的 fail-closed 一致性。原始假设"4 处 mtls 消费点无 `<0` 校验"经自我审查更正为：4 处（rdbcomm:569 / dmsbtex:106 / libobk:71 / oracleCmdTbl:39）赋值后已紧跟 `<0` 硬失败，真实缺口仅 `rdbcommd-main.c:263` 一处。同时 `rdb_auto_init` constructor 是唯一 `init_config` 生产调用点，存在"无法返回错误"与"静态库可能丢弃 .o"两处硬伤，本次一并重构为显式入口加载。

## 假设与结果
- H1（T0386 误判）：自我审查确认 4 处 mtls 点已硬失败，仅 rdbcommd 一处缺口 → **证实**。
- H2（constructor 缺陷）：移除 `rdb_auto_init` 并改为显式 `init_config` → **证实并落地**。
- H3（聚合点策略）：原计划在 `rpc_init_config` / `*_tls_config_init` 内部调 `init_config` 一处覆盖下游 → Do 验证**被推翻**：与 `rpc_config_test` 的"先 `parse_config` 再调聚合函数"契约冲突（重加载默认路径覆盖测试配置，致 `init_fills_sec_switches_from_store` 断言失败）。改为**入口策略**（仅最外层入口调 `init_config`），`init_config` 保持"每次强制重加载"语义。

## 分析
- **AC-1** ✅ rdbcommd-main.c 补上 mtls `<0` 硬失败（与同文件 audit/auth 一致）；其余 4 处经自我审查确认已有 `<0>` 硬失败，全局一致（impl-diff）。
- **AC-2** ✅ 已移除 `libs/rdb-config.c` 的 `rdb_auto_init` constructor；`init_config` 不再有生产自动调用（impl-diff）。
- **AC-3** ✅ 入口策略：rpc main、`rpc-client`、`fs-backup` fsdeamon/fsclient 在 `rpc_init_config` 之前显式 `init_config`；`rpc_config_test` 4/4 通过且其 `init_fills` 用例在入口策略下恢复正常（impl-diff, rpc_config_test, build-all）。
- **AC-4** ✅ 入口策略：`dmsbtex/main.c`、`libobk`（`sbtinit`/`sbtinit2` 库入口、`FileTransferAgent` CLI）在进入各自 TLS config init 之前显式 `init_config`；`libobk_session_test` 通过（impl-diff, libobk_session_test）。
- **AC-5** ✅ `rdbcomm/rdbcommd-main.c`、`rdbcomm/rdbcomm-main.c` main 开头显式 `init_config`，失败 `return EXIT_FAILURE`（impl-diff, build-all）。
- **AC-6** ✅ `param_registry_test.c` main 开头补 `init_config`，9/9 通过，移除 constructor 后不再读空配置（param_registry_test, impl-diff）。
- **AC-7** ✅ 合法 `0/1` 与 ENOENT 行为不变（`rdb_config_test` 15/15 回归、语义未变）；非法 mTLS 开关/非法 rdb.conf（非 ENOENT）改为 fail-closed：`rdbcommd-main.c` mtls `<0` 即 `return EXIT_FAILURE`，且 `rpc_config_test` 的 `init_invalid_audit_env_fails` 验证 env 非法布尔触发失败（rdb_config_test, rpc_config_test, impl-diff）。注：rdbcommd 非法 mtls 的"进程级退出"未做独立活体运行（守护进程启动复杂），但由 `sec_get_bool` 返回 `-1`→`return EXIT_FAILURE` 的代码路径与 `param_registry_test` 的 `sec_get_bool_fail_closed` 组合验证。
- **AC-8** ✅ 构建验证：rpc / rpc_config_test / fsbackup_tools / makeFsbackup / libobk_session_test / FileTransferAgent / rdbcommd / rdbcomm / dmsbtex 编译链接通过（exit 0）；`param_registry_test` 9/9、`rdb_config_test` 15/15 全过。既有 `libobk_protocol_test` 的 `-Werror=unused-variable` 编译失败为本任务范围外（与本次改动无关），不计入（build-all, param_registry_test, rdb_config_test）。

## 失败原因（仅 rejected/partial）
无（全部 AC 满足）。

## 适用边界
- 本次仅 C 侧 rdb config；Go(oss) 侧不在范围。
- 合法 `0/1` 与 ENOENT（无配置文件）行为完全不变；仅"非法开关 / 错误 rdb.conf（非 ENOENT）"从严（fail-closed 启动/初始化失败）。
- `init_config` 须保持"每次强制重加载"语义，不可下沉到聚合函数内部（会与"先 parse 再调"的测试契约冲突）。

## 下一轮建议
- F7（dmsbtex 仍读 `sbt-config.conf` 与 `rdb.conf` 并存）仍列为后续优化，未本次处理。
- `libobk_protocol_test` 的 `-Werror=unused-variable` 属独立阻断，建议单独立项修复。

## 结论判定（verdict）
<!-- 待用户确认后填充：outcome / reason / verdict_id / at -->

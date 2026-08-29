# 对话日志：T0388（0826-rdb-config-failclosed-unify）

## Plan 阶段
- 自我审查更正 T0386 误判：4 处 mtls 消费点（rdbcomm:569 / dmsbtex:106 / libobk:71 / oracleCmdTbl:39）赋值后已紧跟 `<0` 硬失败，仅 `rdbcommd-main.c:263` 一处缺硬失败。
- 用户指出 `rdb_auto_init` 解析失败未处理 + 遗漏 fs-backup；决策方案 B（硬失败 + 显式 init_config 重构），先按"聚合点策略"规划。

## Do 阶段
- 移除 `rdb_auto_init` constructor（`libs/rdb-config.c`）。
- 先按聚合点策略在 `rpc_init_config` 与 3 个 TLS config init 内加 `init_config`，并补各 main/测试 init。
- 验证发现 `rpc_config_test` 的 `init_fills_sec_switches_from_store` 先 `parse_config` 再调 `rpc_init_config`，聚合函数内 `init_config` 重加载默认路径覆盖测试配置致断言失败 → **撤销聚合点内部 init**，改为**入口策略**：仅最外层入口（rdbcomm/rdbcommd/dmsbtex/fs-backup/rpc/libobk×3/FileTransferAgent/param_registry_test）显式 `init_config`，`init_config` 保持"每次强制重加载"语义。
- rdbcommd-main.c 补 mtls `<0` 硬失败。
- 构建与测试全部通过：`param_registry_test` 9/9、`rdb_config_test` 15/15、`rpc_config_test` 4/4、`libobk_session_test` exit 0；rdbcomm/rdbcommd/dmsbtex/libobk/rpc/fs-backup 编译链接通过。
- 更新知识库 `audit-findings.md`、`optim-roadmap.md`。

## Check 阶段
- 登记证据：build-all / param_registry_test / rdb_config_test / rpc_config_test / libobk_session_test / impl-diff / convergence-map。
- 收敛校验 `validate-convergence` → valid:true。
- 写 `conclusion.md`，逐条 AC 判定全部 ✅。
- 用户 verdict=**confirmed**。

## Act 阶段
- 写 `task.json` 的 `meta.verdict`（confirmed）与 `meta.disposition`（projected）。
- 知识沉淀至 `knowledge/rdb-config/audit-findings.md`、`optim-roadmap.md`（manifest 已记录）。
- 归档（phase→archive，任务目录移入 archive/）。

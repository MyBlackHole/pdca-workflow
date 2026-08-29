# T0389 对话日志

## Plan 阶段
- 用户报告：libobk rdb config 存在重复初始化问题（`sbtinit`/`sbtinit2`/`main.c` 三处各自 `init_config`）。
- 决策：开新 PDCA 任务 T0389（父 T0388，已归档）修复，development 场景。
- 用户要求：守卫必须考虑多线程安全。

## Do 阶段
- 初版用互斥锁+标志实现一次性守卫；用户指出应使用 `pthread_once`。
- 改用 `pthread_once`（线程安全一次性初始化惯用法），三态记录结果（`0`=未初始化/`1`=成功/`-1`=失败），失败后所有调用返回 `-1`（fail-closed，不可重试）。
- 守卫定义于 `oracleCmdTbl.c`（该 TU 同时被 `sbt` 库与 `FileTransferAgent` 编译，两目标共用）；`oracleCmdTbl.h` 加 `extern` 声明。
- 三处 `init_config` 调用替换为 `libobk_ensure_rdb_config()`。
- `init_config` 内部实现未改，"每次强制重加载"语义保留。
- 构建通过；回归全过：`param_registry_test` 9/9、`rdb_config_test` 15/15、`rpc_config_test` 4/4、`libobk_session_test` exit 0。

## Check 阶段
- 登记证据：impl-diff / build-all / param_registry_test / rdb_config_test / rpc_config_test / libobk_session_test / convergence-map。
- 收敛校验通过（do→check 门禁 valid）。
- 写 `conclusion.md`，5 条 AC 全部 ✅。
- 用户 verdict=**confirmed**。

## Act 阶段
- 写 `meta.verdict`（confirmed）与 `meta.disposition`（projected）。
- 知识沉淀至 `knowledge/rdb-config/audit-findings.md`（新增"入口重复初始化收敛（T0389 已修复）"小节）。
- 归档（phase→archive，任务目录移入 archive/）。

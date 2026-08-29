# 结论 — T0389：修复 libobk rdb config 重复初始化

## 背景

父任务 T0388 已统一 rdb config 为"fail-closed + 外层入口显式 `init_config`"。但 libobk 有
三个独立入口都调用 `init_config(NULL, ...)`：`sbtinit`（`libobk/lib/sbt/libobk.c`）、
`sbtinit2`（同文件）、`main.c` 的 FileTransferAgent。Oracle SBT 调用序为
`sbtinit` 一次 + `sbtinit2` 多次（每会话一次，可能并发），导致 `init_config` 被重复执行
（重复解析 rdb config 文件，且效率与可观测性差）。

## 修复方案

新增进程内一次性守卫 `libobk_ensure_rdb_config()`，采用 `pthread_once`（线程安全的一次性
初始化惯用法），定义于 `oracleCmdTbl.c`（该 TU 同时被 `sbt` 库与 `FileTransferAgent` 编译，
故两目标共用同一份实现与标志）。守卫三态：`0`=未初始化、`1`=成功、`-1`=失败（失败后所有
调用均返回 `-1`，fail-closed，且不可重试——符合"配置加载失败即拒绝"语义）。

- `sbtinit` / `sbtinit2` / `main.c` 三处 `init_config(NULL, ...)` 调用替换为
  `libobk_ensure_rdb_config()`。
- `oracleCmdTbl.h` 增加 `extern int libobk_ensure_rdb_config(void);` 声明。
- **未改动** `init_config` 内部实现，其"每次强制重加载"语义保持不变（T0388 为
  `rdb_config_test` 刻意保留），守卫只在 libobk 入口层生效。

## 验收判定

- **AC-1** ✅ `libobk_ensure_rdb_config()` 一次性守卫落地，`sbtinit`/`sbtinit2`/`main.c`
  三处改调，`pthread_once` 保证进程内 `init_config` 仅真正执行一次（重复入口/多会话不再
  重复重解析）。证据：`impl-diff`
- **AC-2** ✅ `init_config` 自身"强制重加载"语义不变；`rdb_config_test`(15/15)、
  `param_registry_test`(9/9)、`rpc_config_test`(4/4) 全部通过，rpc/dmsbtex/fs-backup
  入口不受影响。证据：`param_registry_test`、`rdb_config_test`、`rpc_config_test`
- **AC-3** ✅ `libobk_session_test` 通过（exit 0）；守卫仅加载一次，会话测试无重复加载
  副作用。证据：`libobk_session_test`
- **AC-4** ✅ 构建通过——`sbt` 库、`FileTransferAgent` 及依赖 rdb-config 的
  rpc/dmsbtex/fs-backup/rdbcomm 等目标编译链接正常。证据：`build-all`、`impl-diff`
- **AC-5** ✅ 合法 `0/1` 与 ENOENT（无配置文件按合法处理）行为不变；非法配置（非 ENOENT）
  仍 fail-closed（`init_config` 失败 → 守卫返回 `-1` → 入口拒绝）。证据：`rdb_config_test`、
  `impl-diff`

## 收敛

见 `evidence/t0389-convergence-map.json`：收敛点 1（一次性守卫落地、三入口改调）由
`impl-diff`+`build-all` 支撑；收敛点 2（语义不变、四测试全过、构建不受影响）由
`param_registry_test`+`rdb_config_test`+`rpc_config_test`+`libobk_session_test` 支撑。

## 结论

修复达成：libobk 三入口的 rdb config 重复初始化问题消除，且线程安全地一次性加载；
fail-closed 与 `init_config` 现有语义完全保留，全量回归测试通过。建议 verdict=**confirmed**。

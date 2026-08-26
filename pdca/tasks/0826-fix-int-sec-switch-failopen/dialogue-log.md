# T3981 对话日志

## Plan
- 方案 A+纵深（用户确认）：审计/鉴权 param 改 `CFG_TYPE_BOOL` 走 `sec_get_bool`；
  `sec_walk_int` env/def 层改 `parse_strict_int` 返回 -1；消费者改用 `sec_get_bool` + `<0` fail-closed；
  新增 `param_registry_test` 用例。prd.md AC-1~AC-7 定稿，final_confirmation=confirmed。

## Do
- `libs/rdb-config.c`：两参数升 BOOL；`sec_walk_int` env/def 层改 `parse_strict_int`；
  `sec_walk_bool` def 层一并硬化为 `sec_parse_strict_bool`（消除安全布尔开关路径上的宽松 `atoi`）。
- 消费者 6 处改 `sec_get_bool` 并 fail-closed：解析/初始化路径（`rpc-config.cpp`、
  `rdbcommd-main.c`）`<0` 时响亮 `return -1`/`EXIT_FAILURE`；谓词路径（`libs/logger.c`、
  `libs/timed_key.c`）用 `-1 != 0` 天然 fail-closed。
- 补抓 PRD 漏列：`libs/logger.c`、`libs/timed_key.c` 及第四个测试
  `rpc/tests/rpc_config_test.cpp`（旧用例对 "2" 用宽松 int 语义断言，用户 xmake 跑出
  `init_env_overrides_store` 失败即源于此，已修并新增 `init_invalid_audit_env_fails`）。
- 按用户反馈移除 `key_is_enabled`/`logger.c` 的 `if(<0)x=1` 掩错兜底（保留错误语义不掩盖）。
- 验证：`param_registry_test` 9/9、`rdb_config_test` 17/17、`logger_test` 11/11、
  `rpc_config_test` 4/4（xmake）全绿。

## Check
- 收敛校验 `valid: true`；逐条 AC 判定全部 ✅。
- 用户 verdict：confirmed（成立）。

## Act
- 知识沉淀 `knowledge/rdb-config/security-bool-failclosed.md`（正确范式 + 三类反模式）。
- disposition：task_only（T3980 HIGH-1 由此闭环，无后续跟随任务；其余 MEDIUM/LOW/F 类
  由 `0826-cleanup-rdb-config-deadcode` 承接）。

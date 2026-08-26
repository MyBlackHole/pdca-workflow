---
schema: pdca.asset/v1
id: T3981-0826-fix-int-sec-switch-failopen
phase: check
source_ids: [T3981-FIX-VERIFY-ALL, convergence-map2]
---

## 上下文
T3980 审查判定 rdb-config 不满足生产级别（HIGH-1）：`sec_walk_int` 的 env 层用
`atoi` 宽松解析，导致 `PARAM_AUDIT_ENABLED` / `PARAM_AUTH_KEYCHECK_ENABLED` 两类
INT 安全开关在 env 脏值下静默 fail-open（审计/鉴权被关），而同文件内 BOOL 开关
（如 mTLS）已 fail-closed，存在内部不一致。本任务（T3981）落实该整改。

## 假设与结果
- 假设 A：`PARAM_AUDIT_ENABLED` / `PARAM_AUTH_KEYCHECK_ENABLED` 实际只取 0/1 语义，
  可直接升为 `CFG_TYPE_BOOL`。
- 假设 B：消费者应统一走 `sec_get_bool` 并 fail-closed，与既有 `mtls_enabled`
  范式一致。
- 结果：两参数升 BOOL；`sec_walk_int` env/def 层改用 `parse_strict_int`（非法值
  返回 -1）；`sec_walk_bool` def 层一并硬化为 `sec_parse_strict_bool`；6 处消费者
  改 `sec_get_bool` 并 fail-closed；新增/修正测试覆盖脏值响亮失败。

## 分析
- **AC-1** ✅ `PARAM_AUDIT_ENABLED`/`PARAM_AUTH_KEYCHECK_ENABLED` 改 `CFG_TYPE_BOOL`，`g_param_table` 与 `config_dump_params` 类型显示一致（T3981-FIX-VERIFY-ALL）
- **AC-2** ✅ `sec_walk_int` env/def 层改 `parse_strict_int`，非法值返回 -1；`sec_walk_int` 内无 `atoi` 残留（`sec_walk_bool` def 层一并硬化）（T3981-FIX-VERIFY-ALL）
- **AC-3** ✅ 6 处消费者改 `sec_get_bool` 并 fail-closed：解析/初始化路径（`rpc-config.cpp`、`rdbcommd-main.c`）`<0` 时 `return -1`/退出并写错误；谓词路径（`logger.c`、`timed_key.c`）利用 `-1 != 0` 天然 fail-closed，不做 `if(<0)x=1` 改写掩盖（T3981-FIX-VERIFY-ALL）
- **AC-4** ✅ `param_registry_test` 新增 `audit_auth_fail_closed_env`：脏值 → `sec_get_bool` 返回 -1（T3981-FIX-VERIFY-ALL）
- **AC-5** ✅ 回归 `param_registry_test`(9/9)、`rdb_config_test`(17/17)、`logger_test`(11/11)、`rpc_config_test`(4/4) 全通过（T3981-FIX-VERIFY-ALL）
- **AC-6** ✅ 受影响模块经 gcc/xmake 编译验证通过；既有 `libs/tls_cert.c` `-Werror=stringop-truncation` 为独立既有问题（T3981-FIX-VERIFY-ALL）
- **AC-7** ✅ 无 `sec_get_int(PARAM_AUDIT_ENABLED)` / `sec_get_int(PARAM_AUTH_KEYCHECK_ENABLED)` 残留（T3981-FIX-VERIFY-ALL）

## 适用边界
- 仅覆盖 T3980 判定的 HIGH-1；T3980 中 MEDIUM/LOW 及 F-类清理项由 `0826-cleanup-rdb-config-deadcode` 承接。
- `sec_get_int` 仍保留给其它真正的 INT 参数使用，本次未改动其通用语义。

## 下一轮建议
- 将本整改提交后，关联关闭 T3980 的 HIGH-1；后续在 CI 中加入"安全开关 env 脏值必须 fail-closed"的回归基线。
- 关注 `rpc-config.cpp` 中 `g_rpc_config->audit_enabled` 等字段为 `int`，运行时值恒为 0/1（`-1` 仅在 `rpc_init_config`/`rpc_parse_config` 内部提前返回前短暂出现），消费者按布尔判读安全。

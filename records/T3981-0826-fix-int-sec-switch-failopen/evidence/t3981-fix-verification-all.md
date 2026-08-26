# T3981 整改验证证据

## 变更范围
- `libs/rdb-config.c`：`PARAM_AUDIT_ENABLED` / `PARAM_AUTH_KEYCHECK_ENABLED`
  由 `CFG_TYPE_INT` 改为 `CFG_TYPE_BOOL`；`sec_walk_int` 的 env/def 层改用
  `parse_strict_int`（非法值返回 -1）；`sec_walk_bool` 的 def 层一并硬化为
  `sec_parse_strict_bool`（消除安全布尔开关路径上的宽松 `atoi`）。
- 消费者（6 处）改用 `sec_get_bool` 并 fail-closed（不掩盖错误）：
  - `rpc/rpc-config.cpp`（rpc_parse_config / rpc_init_config 共 4 处）：
    `<0` 时直接 `return -1` 并写 `err_msg`（与 `mtls_enabled` 范式一致）。
  - `rdbcomm/rdbcommd-main.c`（server_opts 2 处）：`<0` 时 `fprintf(stderr)`
    后 `return EXIT_FAILURE`。
  - `libs/logger.c`、`libs/timed_key.c`（谓词路径）：利用 `sec_get_bool` 的
    `-1 != 0` 天然 fail-closed，不做 `if(<0)x=1` 改写掩盖错误。

## 测试验证
- `libs/tests/param_registry_test.c`（手动 gcc）：9/9 通过，含新增
  `audit_auth_fail_closed_env`（脏值 → `sec_get_bool` 返回 -1）。
- `libs/tests/rdb_config_test.c`（手动 gcc）：17/17 通过。
- `libs/tests/logger_test.c`（手动 gcc）：11/11 通过。
- `rpc/tests/rpc_config_test.cpp`（xmake run rpc_config_test）：4/4 通过，
  含新增 `init_invalid_audit_env_fails`（非法 env → `rpc_init_config`
  返回 -1，响亮失败）；修复了原 `init_env_overrides_store` 对 "2" 的
  宽松 int 旧断言。

## 范围补充发现
- Do 阶段发现 PRD 漏列两处库内消费者（`libs/logger.c`、`libs/timed_key.c`）
  及第四个测试文件 `rpc/tests/rpc_config_test.cpp`（经公共 API 调用，
  不直连 `sec_get_int`，故 AC-7 grep 未捕获）。均已纳入整改与测试。

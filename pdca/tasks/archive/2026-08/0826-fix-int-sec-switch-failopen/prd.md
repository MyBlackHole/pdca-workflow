# PRD — T3981：rdb-config INT 安全开关 env 脏值 fail-open 整改

- 任务 ID：T3981 / 0826-fix-int-sec-switch-failopen
- 父任务：T3980（审查结论：不满足生产级别，HIGH-1）
- 场景：development（bugfix）
- 关联知识：`knowledge/rdb-config/int-security-switch-failopen.md`

## 问题陈述
`libs/rdb-config.c` 的 `sec_walk_int` 在 env 层（及 def 层）使用 `atoi`，导致 `PARAM_AUDIT_ENABLED`（`AUDIT_ENABLE_ENV`）、`PARAM_AUTH_KEYCHECK_ENABLED`（`AUTH_ENABLE_ENV`）这类以 INT 承载布尔语义的安全开关，在 env 被设为脏值（如 `AUDIT_ENABLE=garbage`）时 `atoi→0`，审计/鉴权被静默关闭（fail-open）。同文件 BOOL 开关已通过 `sec_parse_strict_bool` + 消费者 `<0` 校验实现 fail-closed，INT 安全开关被遗漏，构成 T3980 HIGH-1。

## 方案
采用 A+纵深：
1. 将 `PARAM_AUDIT_ENABLED`、`PARAM_AUTH_KEYCHECK_ENABLED` 的 `type` 由 `CFG_TYPE_INT` 改为 `CFG_TYPE_BOOL`，走已具备 fail-closed 的 `sec_get_bool`。
2. `sec_walk_int` 的 env 层与 def 层改为 `parse_strict_int`，非法值返回 `-1`（fail-closed），彻底移除宽松 `atoi` 路径（纵深防御；当前无其余 INT 参数，改动零副作用）。
3. 消费者 `rpc/rpc-config.cpp`（2 处）、`rdbcomm/rdbcommd-main.c`（2 处）改用 `sec_get_bool`，并对返回值 `<0` 做 fail-closed 校验（报错/退出），与既有 `mtls_enabled` 处理一致。

## 用户故事
- 运维误配 `AUDIT_ENABLE=garbage` 时，依赖该开关的服务启动失败并报错，而非静默以无审计状态运行。
- 合法 `AUDIT_ENABLE=0/1`、`AUTH_ENABLE=0/1`、未设置（取默认）行为完全不变。

## 实现/测试决策
- 改动文件：`libs/rdb-config.c`（g_param_table 类型 + sec_walk_int 严格化）、`rpc/rpc-config.cpp`（2 处）、`rdbcomm/rdbcommd-main.c`（2 处）、`libs/tests/param_registry_test.c`（新增测试）。
- `sec_walk_int` 改造后语义：env 层 `parse_strict_int` 失败 → 返回 -1；layer2/layer3 维持 `config_get_int(...,-1)`；def 层 `parse_strict_int` 失败 → 返回 -1。
- 消费者校验模板：
  `if (x->audit_enabled < 0) { 报错; return -1 / EXIT_FAILURE; }`
- 不改动 Go `oss` 侧（其解析独立于 C 注册表，且本 HIGH 为 C 侧问题）。

## 范围外
- 不修复 T0369 F9（证书路径校验，属 MEDIUM，归 0826-cleanup-rdb-config-deadcode）。
- 不修复 MEDIUM-2/3、LOW-1/2/3（归 0826-cleanup-rdb-config-deadcode）。
- 不改动其他参数类型（其余均为 STR/BOOL，无 INT 残留）。

## 备注
- `atoi` 在 `sec_walk_int` 移除后，整个安全开关解析链不再有宽松 atoi 路径。
- `sec_get_int` 仍保留导出，但当前无 INT 参数消费者；回归测试保证其严格语义。

## Seam 分析

### 声明的测试接缝
- seam: libs/tests/param_registry_test.c -> libs/rdb-config.c

## 验收标准
- [x] AC-1: `PARAM_AUDIT_ENABLED` / `PARAM_AUTH_KEYCHECK_ENABLED` 的 `type` 改为 `CFG_TYPE_BOOL`，`g_param_table` 声明与 `config_dump_params` 类型显示一致。
- [x] AC-2: `sec_walk_int` 的 env 层与 def 层改用 `parse_strict_int`，非法值返回 -1；`grep` 确认 `sec_walk_int` 内无 `atoi` 残留（`sec_walk_bool` 的 def 层一并硬化为严格解析，消除安全布尔开关路径上的宽松 `atoi`）。
- [x] AC-3: 全部消费者改用 `sec_get_bool` 并 fail-closed（与 `mtls_enabled` 处理一致、**不掩盖错误**）：解析/初始化路径（`rpc/rpc-config.cpp`、`rdbcomm/rdbcommd-main.c` 共 4 处）`<0` 时直接 `return -1`/退出并写错误；谓词路径（`libs/logger.c`、`libs/timed_key.c` 共 2 处）利用 `sec_get_bool` 的 `-1 != 0` 天然 fail-closed，不做 `if(<0)x=1` 改写掩盖；测试 `libs/tests/rdb_config_test.c`、`libs/tests/logger_test.c`、`rpc/tests/rpc_config_test.cpp` 同步改用 `sec_get_bool`/合法布尔 env，并修正非法值断言（rpc_config_test 新增 `init_invalid_audit_env_fails` 验证响亮失败）。
- [x] AC-4: `libs/tests/param_registry_test.c` 新增用例 `audit_auth_fail_closed_env`：`AUDIT_ENABLE`/`AUTH_ENABLE` 设为脏值 → `sec_get_bool` 返回 -1；合法 `0`/`1`、未设置行为不变（同套 `shared_chain_consistency` 已改用 `sec_get_bool`）。
- [x] AC-5: 回归 `param_registry_test`(9/9)、`rdb_config_test`(17/17)、`logger_test`(11/11)、`rpc_config_test`(4/4，经 xmake 运行) 全部通过；T0369 F2/F4/F5 行为不变。
- [x] AC-6: 受影响模块（`rpc`/`rdbcomm`/`libs`）源文件经手动 `gcc` 编译验证通过（与现有 xmake 同源）；既有 `libs/tls_cert.c` `-Werror=stringop-truncation` 为独立既有问题，非本任务引入。
- [x] AC-7: `grep` 确认无 `sec_get_int(PARAM_AUDIT_ENABLED)` / `sec_get_int(PARAM_AUTH_KEYCHECK_ENABLED)` 残留；新增符号仅为 fail-closed 谓词用法，无遗留。

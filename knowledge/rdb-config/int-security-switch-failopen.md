# INT 型安全开关须 fail-closed（rdb-config 审查 T3980）

## 原则
安全关键开关（审计 / 鉴权 / mTLS）的参数解析**必须 fail-closed**：环境变量或配置文件中的脏值（非预期值）应回退默认值或显式报错，而**不能静默当作 0 / 关闭**。否则攻击者或运维误配可导致安全控制被悄悄关掉，且无任何告警。

## 案例（T3980 HIGH-1）
- 位置：`libs/rdb-config.c` `sec_walk_int`（env 层 `rdb-config.c:382-385` 用 `atoi` 直接返回）。
- 现象：`PARAM_AUDIT_ENABLED`（`AUDIT_ENABLE_ENV`）、`PARAM_AUTH_KEYCHECK_ENABLED`（`AUTH_ENABLE_ENV`）定义为 `CFG_TYPE_INT`；当 env 被设为脏值（如 `AUDIT_ENABLE=garbage`）时 `atoi→0`，**审计 / 鉴权被静默关闭**，无告警、无报错。
- 不一致：同文件 `BOOL` 开关已通过 `sec_parse_strict_bool` + 消费者 `<0` 校验实现 fail-closed（如 `rpc-config.cpp:180`、`rdbcommd-main.c:332`），INT 型安全开关被遗漏。
- 根因：T3979 为 `INT` 保留"宽松 atoi 历史语义"（注释 `rdb-config.c:378`），但审计 / 鉴权以 INT 类型承载布尔语义，使宽松语义落在了安全开关上。

## 整改方向（任一）
1. 将 `AUDIT_ENABLED` / `AUTH_KEYCHECK_ENABLED` 改为 `CFG_TYPE_BOOL`，走 `sec_get_bool`（已 fail-closed 且校验 `-1`）；或
2. `sec_walk_int` 的 env 层改用 `parse_strict_int`，失败返回 `-1`，并要求消费者对 `-1` 显式处理（fail-closed）。

## 适用边界
- env 通常由运维受信；但在容器 / 12-factor / CI 环境下 env 可被间接注入，此时 fail-open 可被利用使审计 / 鉴权静默失效。
- 判定口径：以"安全控制 fail-closed"为生产级别硬标准；若组织明确接受 env 受信假设，可将该类发现降级为 MEDIUM，但需在文档中显式声明该假设。

## 复用指引
审查任何安全相关配置解析链时，统一核对：**所有安全开关（含 INT 型承载布尔语义者）是否 fail-closed**，不要只检查显式的 BOOL 参数。同时核对跨语言（C/Go）对非法值的处理策略是否一致（C 侧报错 vs Go 侧告警+关闭的分歧亦属待统一项）。

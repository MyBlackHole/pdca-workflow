# sec_resolve 运行期调用收敛为各模块进程上下文字段

## 问题

`sec_resolve_*` 在运行期被反复调用，每次都执行 getenv + 配置锁 + store 线性查找。运行期热点：

- rdbcomm/server.c ×3：AUDIT 开关检查位于连接/消息处理路径（每消息执行）
- rpc/rpc-server.cpp ×2：同上（worker 处理路径）
- libs/timed_key.c key_is_enabled()：被 rdbcomm/server.c process_init 每连接调用（AUTH 解析）

其余调用点（四模块 config init、logger init_audit_logger、客户端一次性路径）已是初始化时一次，符合模式。

## 设计原则（用户裁定）

- **每个程序有自己的进程上下文结构**（如 `rpc_config`、`server_options`），运行初期初始化时就通过 `sec_resolve_*` 把安全开关值取好存入上下文。
- **运行期处理业务时读自己上下文的字段**；连接级业务由连接对象持有的上下文副本承接（connection 已有 `conn->options = server->options` 拷贝链）。
- **不新建全局策略单例**（否决初版 sec_policy_t/pthread_once 方案——通用缓存机制已被裁定不做，全局单例同样引入失效复杂度且违背模块自持上下文原则）。
- 不提供运行期刷新：进程生命周期内策略固定（"初始化时获取好"语义）。

## 方案

各模块既有进程上下文结构增加安全开关字段，初始化时解析填充：

```c
/* rpc_config（rpc/rpc-config.h）与 server_options（rdbcomm/server.h）均新增： */
int audit_enabled;  /* AUDIT_ENABLE_ENV > [security]audit_enable > [auth]enable > 0 */
int auth_enabled;   /* AUTH_ENABLE_ENV  > [security]auth_enable  > [auth]enable > 0 */
```

解析沿用 `sec_resolve_int` 宽松 int 语义（非 sec_resolve_bool 严格布尔），保持行为不变。填充位置与既有 `mtls_enabled` 字段同模式（init/main 中一次解析）。

### 迁移点

| 文件 | 改动 |
|------|------|
| rpc/rpc-config.h | `rpc_config` 增加 `audit_enabled`/`auth_enabled` 字段 |
| rpc/rpc-config.cpp `rpc_init_config` | 初始化时解析两开关存入 `g_rpc_config` |
| rpc/rpc-config.cpp `rpc_parse_config` | 配置重载切换后重新解析两开关（Grill 裁定：reload 刷新，不沿用旧快照） |
| rpc/rpc-server.cpp ×2 | `sec_resolve_int(AUDIT...)` → `g_rpc_config->audit_enabled` |
| rdbcomm/server.h | `server_options` 增加 `audit_enabled`/`auth_enabled` 字段 |
| rdbcomm/rdbcommd-main.c | main 初始化段解析填入 `server_opts` |
| rdbcomm/server.c ×3 | AUDIT 检查 → `conn->options.audit_enabled`（经既有 conn->options 拷贝链） |
| rdbcomm/server.c:694 | `key_is_enabled()` → `conn->options.auth_enabled != 0` |

### Grill 追加裁定（Check 阶段回滚 Do 补齐）

- **reload 刷新语义**：aio-speedd 的 process_reload_cmd→rpc_parse_config 重载配置时，安全开关随重载重新解析（env/store 当前值生效），不沿用旧快照。
- **补充单测**：rpc/tests/rpc_config_test.cpp 新 target，覆盖 init 填充、env 优先、reload 重解析三场景（含 section 名对齐生产用法的回归锚）。

### 明确不动

- 四模块 config init、dmsbtex/libobk 的 mtls/cert 解析：已是正确模式
- libs/logger.c init_audit_logger：本身即初始化时一次调用，已符合模式
- key_is_enabled 余下消费方（rdbcomm-main.c、rpc-client.cpp、timed_net_key.c）：客户端一次性/低频路径，非热点，保持不动
- timed_net_key_create：仓内无调用方（仅导出符号），不触碰

## 用户故事

1. 作为维护者，运行期安全策略开关应零解析开销（读上下文字段），配置来源在启动时一次性确定，且每个模块的策略状态由自己的上下文持有，无跨模块全局单例。

## Seam 分析

### 声明的测试接缝

- seam: libs/tests/rdb_config_test.c -> ../rdb-config.c（锁定 audit/auth 开关四层解析语义）
- seam: e2e test/e2e_tool_scenarios.sh S1/S7/S8（aio-speed 与 rdbcomm 端到端 audit/auth 路径）

## 测试决策

- rdb_config_test 新增用例：AUDIT/AUTH 开关的 env > [security] > [auth] > default 四层解析断言（迁移所依赖语义的回归锚；sec_resolve 本体不变，此为防漂移锚点）。
- rpc_config_test（Grill 追加）：rpc_init_config 填充、env 优先、reload 重解析三场景单测。
- 回归：logger_test、session_test、e2e 场景矩阵（S1 覆盖 aio-speed 命令执行路径、S7/S8 覆盖 rdbcomm 路径）。
- server_opts 填充位于 rdbcommd main 流程，无独立单测 target，由 e2e 全路径覆盖（限制已在 evidence 说明）。

## 验收标准

- [ ] AC-1: grep 确认运行期路径不再直接调用 sec_resolve_int(AUDIT/AUTH)：server.c 三处读 conn->options.audit_enabled、process_init 读 conn->options.auth_enabled、rpc-server.cpp 两处读 g_rpc_config->audit_enabled。
- [ ] AC-2: rdb_config_test 新增 audit/auth 四层解析用例通过。
- [ ] AC-3: 全量构建通过；logger_test 与 e2e 场景矩阵（S1/S7/S8 及全量）回归通过。
- [ ] AC-4: 既有初始化模式未被破坏（session_test 回归过；key_is_enabled 客户端消费方行为不变）。
- [ ] AC-5: 配置重载（rpc_parse_config）后安全开关重新解析刷新，rpc_config_test reload 用例通过。
- [ ] AC-6: rpc/tests/rpc_config_test.cpp 单测 target 建立，init 填充/env 优先/reload 刷新三场景全部通过。

## 范围外

- 四模块 config init 重构（已是正确模式）
- 通用缓存机制 / 全局策略单例（用户已裁定不做）
- timed_net_key 导出 API 变更

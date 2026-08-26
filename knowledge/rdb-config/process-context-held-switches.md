# 进程上下文持有模式（安全/策略开关的运行期收敛）

## 模式定义

每个程序在自己的**进程上下文结构**中持有安全/策略开关字段：初始化时经 `sec_resolve_*` 一次性解析取值保存，运行期业务路径只读结构体字段（O(1)），不再逐次执行 getenv + 配置锁 + store 线性查找。

## 裁定原则（T3968 用户确立）

1. **模块自持上下文**：不建全局策略单例、不做通用缓存机制。每个模块用自己的上下文结构（如 `rpc_config`、`server_options`）承载自己的策略状态。
2. **运行初期初始化好**：开关值在 init/main 时解析填充，与既有配置字段（mtls_enabled 等）同位置同模式。
3. **连接对象承接连接级业务**：连接级处理从连接对象持有的上下文副本读取（rdbcomm 既有 `conn->options = server->options` 拷贝链），不为连接额外复制独立快照成员。
4. **reload 刷新语义**：配置重载入口（如 aio-speedd 的 process_reload_cmd→rpc_parse_config）须重新解析策略开关——管理员的运行期变更应可经 reload 生效；解析源（env + 全局 config store）与被重载的结构体 ini 相互独立。

## 实施锚点（T3968 参考）

| 要素 | 位置 |
|------|------|
| rpc 侧上下文字段 | `rpc_config.audit_enabled/auth_enabled`（rpc/rpc-config.h） |
| rpc 填充点 | `rpc_init_config`（init 兜底）+ `rpc_parse_config` 切换后刷新（reload） |
| rdbcomm 侧上下文 | `server_options.audit_enabled/auth_enabled` → `conn->options` |
| 单测范式 | rpc/tests/rpc_config_test.cpp：init 填充 / env 优先 / reload 刷新三场景；测试需显式 `rpc_set_section_name` 对齐生产 |

## 语义边界

- 解析沿用 `sec_resolve_int` 宽松 int 语义（env "2" 为真）；严格布尔 fail-closed 属 `sec_resolve_bool` 域（见 T0361），勿混淆。
- 无重载机制的程序（如 rdbcommd）快照为进程生命周期固定——这是"初始化时获取好"的正确语义而非缺陷。
- 新增安全开关时优先挂到既有进程上下文结构，禁止新建全局单例。

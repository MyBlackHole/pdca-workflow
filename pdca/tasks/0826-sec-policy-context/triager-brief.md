# Triage Brief — 0826-sec-policy-context

- **category**: enhancement
- **scenario_type**: development
- **summary**: sec_resolve 的 AUDIT/AUTH 开关在运行期路径反复解析，收敛为初始化时一次性获取的进程级策略上下文（sec_policy_t 单例）。
- **current behavior**: rdbcomm/server.c×3、rpc-server.cpp×2 每请求执行 getenv+锁+查找；timed_key key_is_enabled 同样每次全链解析。
- **desired behavior**: 启动时 sec_policy_init() 解析保存；运行期读字段零开销。
- **key interfaces**: rdb-config.h sec_policy_t/sec_policy_init/sec_policy。
- **acceptance criteria**: 运行期路径无 sec_resolve 直接调用；rdb_config_test 新用例过；logger_test/e2e 回归过；四模块 init 不受影响。
- **out of scope**: 四模块 config init 重构；通用缓存机制。
- **information gaps**: 无。
- **dedup results**: T3967 曾做通用 cached 变体被用户撤销；本任务为显式上下文模式，符合用户"初始化时获取好+参数保存"指示。无重复。
- **recommended next steps**: 小改动直接实施。

---
schema: pdca.asset/v1
id: T3968-0826-sec-policy-context
phase: check
source_ids: [ac1-grep-zero-residual, ac2-rdb-config-test, ac3-build-logger-e2e, ac4-session-tests, ac5-reload-reresolve, ac6-rpc-config-test]
---

## 上下文

`sec_resolve_int(AUDIT/AUTH)` 在运行期热点（rdbcomm/server.c ×3、rpc/rpc-server.cpp ×2、key_is_enabled 每连接）被逐次调用，每次执行 getenv + 配置锁 + store 线性查找。任务目标：按"每个程序有自己的进程上下文"原则，将安全开关解析收敛进各模块既有进程上下文结构，初始化时取好值，运行期只读字段。执行中经历一次方案重设计（否决全局 sec_policy 单例）与一次 Grill 驱动的回滚补齐（reload 刷新语义 + 补单测）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 热点迁移到上下文字段后行为不变（宽松 int 语义保持） | ✅ 成立——四层解析回归锚用例锁定语义，e2e 19/19 通过 |
| conn->options = server->options 既有拷贝链可直接承载新字段 | ✅ 成立——server.c 五处读取点零额外传递代码 |
| reload 沿用旧快照可接受（与 mtls_enabled 一致） | ❌ 被 Grill 否决——已修复：rpc_parse_config 切换后重解析 |
| 填充逻辑无单测、由 e2e 覆盖足够 | ❌ 被 Grill 否决——已补 rpc_config_test 三场景单测 |

## 分析

- **AC-1** ✅ 运行期路径零 sec_resolve_int/key_is_enabled 直接调用，五处读取点全部改为上下文字段（conn->options.audit_enabled/auth_enabled ×4、g_rpc_config->audit_enabled ×2 处文件）（ac1-grep-zero-residual）
- **AC-2** ✅ rdb_config_test 新增 sec_switch_audit_auth_layers 四层解析回归锚通过，17/17（ac2-rdb-config-test）
- **AC-3** ✅ 受影响目标构建通过；logger_test 11/11；e2e 场景矩阵 19/19（含 S1/S7/S8 audit/auth 路径）（ac3-build-logger-e2e）
- **AC-4** ✅ dmsbtex/libobk session_test rc=0；key_is_enabled 客户端消费方（rdbcomm-main/rpc-client/timed_net_key）git diff 零改动（ac4-session-tests）
- **AC-5** ✅ Grill Q1 裁定修复落地：rpc_parse_config 切换后重新解析两开关（rpc-config.cpp:104），reload 用例先红后绿锁定语义（ac5-reload-reresolve）
- **AC-6** ✅ rpc/tests/rpc_config_test.cpp 新 target 三场景全绿：init 从 [security] 段填充、env 优先+宽松 int 语义、reload 刷新（ac6-rpc-config-test）

提交链：1318f591（主体迁移，经并行 amend 含无关格式化调整）→ 69da290b（Grill 修复 + 单测）。

## 适用边界

- 方案适用于"进程级安全策略开关"类配置的运行期收敛；不适用于需逐请求变化的动态配置。
- rdbcommd 侧快照为进程生命周期固定（无重载机制）；aio-speedd 侧 reload 触发重解析，两层语义并存但各自自洽。
- 解析沿用宽松 int 语义（env "2" 为真）；严格布尔 fail-closed 属 sec_resolve_bool 域，未在本任务范围。

## 下一轮建议

- 性能定量基准可并入后续 perf 任务（参照 0815-perf-baseline 先例）：热路径每消息最多省 3 次 getenv+锁+线性查找。
- 全量 `xmake build -a` 中 fs_meta_key_test.cpp 编译错误为既有问题（stash 验证与本改动无关），建议另开任务处理。
- 若未来 rdbcommd 引入配置重载机制，需对称补充 server_options 快照刷新逻辑。

## verdict

- outcome: confirmed
- reason: 六条 AC 均有登记证据支撑；Grill 两项否决（reload 刷新语义、补单测）已修复闭环并先红后绿锁定
- verdict_id: T3968-check-verdict-001
- at: 2026-08-26T10:30:41+08:00

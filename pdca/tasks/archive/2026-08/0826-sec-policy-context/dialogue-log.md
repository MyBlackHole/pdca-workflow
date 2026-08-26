# dialogue-log — T3968 0826-sec-policy-context

## 2026-08-26 Plan→Do→(回滚 Plan)→Do 摘要

### 本阶段讨论要点
1. 初版方案（全局 sec_policy_t 单例 + pthread_once）完成自我审查：热点计数与代码事实一致，但识别出宽松 int/严格 bool 语义、pthread_once×fork、once 后不可复测三项约束。
2. 用户否决初版并给出架构原则：每个程序有自己的进程上下文结构（如 rpc_config），运行初期初始化时取好 sec_resolve_* 值；连接级业务由连接对象持有的上下文承接。
3. 修正方案：rpc_config 与 server_options 增加 audit_enabled/auth_enabled 字段，init/main 时填充；经既有 conn->options = server->options 拷贝链下发；五处热点改读字段。
4. TDD 以特征化测试先行：sec_switch_audit_auth_layers 四层解析回归锚锁定迁移依赖语义，再实施行为保持迁移。
5. 全部验证通过后提交 e58fd9b4 并登记 4 条 AC 证据 + convergence-map（validate 通过）。

### 被否决的备选及否决理由
- ❌ 全局 sec_policy_t 单例（初版 PRD）：用户裁定不做通用缓存机制，全局单例同样引入失效复杂度且违背"模块自持上下文"原则。后续 session 勿再提议。
- ❌ key_is_enabled 改带参签名/timed_net_key API 变更：仓内 timed_net_key_create 无调用方，客户端消费方均为一次性低频路径，不值得破坏导出 API。
- ❌ 连接对象复制策略快照为独立成员：audit/auth 为纯进程级开关，conn->options 已是上下文副本，无需再加一层。

### 用户关键反应原话
- "不要直接执行回滚到计划阶段，每个程序应该有自己的上下文，运行初期就应该初始化好，如果运行过程出现例如连接对象应该是连接对象持有上下文处理"
- "例如 rpc_config 就是 rpc 服务端的进程上下文结构，那么他就应该初始化时就获取好 sec_resolve_* 的值，而不是运行态处理业务时再获取"
- "可以"（确认修正方案进入 Do；对应 clarifications final_confirmation 条目）

### 未解决即跳过的疑点
- 无阻塞疑点。备注：全量 xmake build -a 中 fs_meta_key_test.cpp 编译错误为既有问题（stash 验证与本改动无关），未在本任务处理。

## 2026-08-26 Check→(Grill)→回滚 Do→Check 摘要

### 本阶段讨论要点
1. Grill 三问：Q1 reload 后开关沿用旧快照是否接受、Q2 填充逻辑无单测是否接受、Q3 性能未量化是否接受。
2. 用户裁定 Q1 不一致需修复、Q2 补单测、Q3 接受定性（仅 Q3 采纳推荐）。
3. 回滚 do 执行修复切片：rpc_parse_config 切换后重解析两开关；新增 rpc/tests/rpc_config_test.cpp（TDD 先红后绿，红锁定 reload 未刷新缺陷；调试中发现默认 section 为 aio-speed 非服务端段，测试显式 set 对齐生产）。
4. PRD 增补 AC-5/AC-6，全量回归通过（rdb_config 17、rpc_config 3、logger 11、session rc=0×2、e2e 19/19），提交 69da290b。
5. 发现并行 amend：e58fd9b4→1318f591，差异为 libs/tls_cert.c 纯格式化（非本会话操作，语义无害，留痕备查）。

### 被否决的备选及否决理由
- ❌ "reload 沿用旧快照与 mtls_enabled 一致即可"（我的推荐）：用户裁定安全策略开关应随 reload 刷新，管理员变更需可生效。
- ❌ "填充无单测由 e2e 覆盖足够"（我的推荐）：用户要求专项单测。

### 用户关键反应原话
- Q1 答"不一致，需修复"；Q2 答"不接受，补单测"；Q3 答"不补，接受定性"（grilling round 1，captured:true 已落盘）

### 未解决即跳过的疑点
- rdbcommd 无配置重载机制，server_options 快照天然进程固定，无对称修改需求。

## Check 阶段收尾
- verdict=confirmed（T3968-check-verdict-001）：六条 AC 证据链完整，Grill 否决项闭环。进入 Act。

# 分析 rpc 配置重载链路失效问题（三层断裂与发布竞态）

## 问题陈述

T3968 引入"配置重载时安全开关重新解析刷新"的裁定，T3975 审查发现该目标实际落空：重载链路存在三层断裂 + 一个发布竞态。需完整厘清 rpc 配置生命周期，量化 reload 对各安全消费点的真实影响，产出修正设计。

## 已验证事实（triage）

1. **store 层不刷新**：`libs/rdb-config.c:380` `__attribute__((constructor)) rdb_auto_init` 启动时 `init_config` → `parse_config` 填充 `_kv_stores[2]`；全仓库无第二处 `parse_config` 调用。
2. **rpc_parse_config 覆盖不全**：`rpc/rpc-config.cpp:86-121` ini 重解析 + audit/auth 两字段 sec_resolve 重算（:110-119）；`mtls_enabled`/`tls_algorithm`/`cert_dir` 仅存在于 `rpc_init_config`（:170-186），reload 路径完全不触及。
3. **发布顺序竞态**：`rpc-config.cpp:104-105` 先 `config_index=tmp; g_rpc_config=p_config;` 发布新缓冲，:110 之后才回写 audit/auth 字段——工作线程可读到"新指针+未回写字段"。
4. **reload 触发点**：`rpc/main.cpp:453` 注册 `RELOAD_CONFIG_CMD` → `process_reload_cmd`（:308）→ 仅调 `rpc_parse_config`。

## 分析维度（方案）

1. **数据流全景**：ini 文件/env → {_kv_stores, g_rpc_config} → 消费点 的层级图，标注每条边的写入时机（constructor/init/reload/runtime）。
2. **影响矩阵**：安全相关消费点（握手 mtls_enabled、算法锁定 tls_algorithm、cert_dir、key 验证 auth_enabled、审计 audit_enabled、sec_resolve 其他调用方）× reload 后行为（生效/不生效/竞态窗口）逐格判定。
3. **竞态语义分析**：C++ 数据竞争标准层面 vs x86 TSO 实际表现 vs 业务危害（审计判定瞬间不一致）分级论证。
4. **修正方案对比**（至少两案）：
   - A. 完整热重载：reload 同步刷新 store（复用 libs 双缓冲）+ 补齐 TLS 三字段重解析 + 写完再发布（RCU 式）
   - B. 安全键冻结：文档化"安全开关仅启动期生效"，reload 时检测安全键差异即告警或拒绝
   - 权衡维度：fail-closed 一致性、运维灵活性、并发复杂度、与 T3968 裁定意图的相容性
5. **设计模式深度审查**（用户终审补充要求，逐模式评价其与热重载目标的相容性）：
   - 双缓冲快照发布模式（`_kv_stores[2]` 与 `_config[2]` 两处同型实现）：槽位数、读者宽限、发布/回写顺序
   - constructor 隐式初始化模式（`rdb_auto_init`）：加载时机不可控、无刷新入口的结构性后果
   - sec_resolve 四层解析链模式（ini-global/master-enable/env/default）：层间短路语义、fail-open/fail-closed 分裂
   - 进程上下文字段缓存模式（T3968"解析一次存字段"）：上下文化优化与可重载性的内在张力——本缺陷的根性矛盾
   - 全局指针切换单例模式（`g_rpc_config` 裸指针发布）：原子性缺失与替代（atomic/shared_ptr/世代计数）
6. **配置参数可发现性与可维护性审计**（用户终审反馈：rdb config"根本不知道到底有什么参数"，不具备可维护性）：
   - 全量盘点被消费的配置键：键名宏/字符串定义位置、消费点、来源层级、默认值——形成参数清单表
   - show 命令展示覆盖度 vs 实际键集的差距；文档现状（无参数文档）
   - 根因分析：无单一参数注册表/schema，键定义散落多文件多层级
   - 改进方向：集中式参数注册表（键名/层级/类型/默认值/说明五元组）驱动解析、show 全量输出与文档生成
7. **推荐设计**：给出推荐方案的落地要点（函数级改动清单，供后续修复任务直接引用）。

## Seam 分析

research 场景无代码测试产物；验证方式为报告内容断言。

### 声明的测试接缝

（无——纯调研分析）

## 范围外

不修改任何代码；修复实施另行立项；不分析非安全字段的 reload 语义（debug/retry 等业务字段当前工作正常）。

## 验收标准

- [ ] AC-1: `records/T3977-0826-analyze-rpc-reload-chain/analysis-report.md` 存在，含数据流全景图与每层刷新时机标注
- [ ] AC-2: 报告含安全消费点 × reload 行为的影响矩阵，每格附 file:line 依据
- [ ] AC-3: 报告含 ≥2 个修正方案的 fail-closed 权衡论证与明确推荐
- [ ] AC-4: 报告含设计模式深度审查章节：五个模式逐一评价（含与热重载目标的相容性判定）
- [ ] AC-5: 报告含配置键全量盘点表（键/定义位置/消费点/层级/默认值）与参数不可发现问题的根因结论
- [ ] AC-6: 推荐方案附函数级落地要点清单；每条关键结论有可复核验证途径

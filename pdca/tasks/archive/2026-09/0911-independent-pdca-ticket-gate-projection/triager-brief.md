# Triage Brief — independent-pdca-ticket-gate-projection

- **category**: bug
- **ontology_role**: `ontology_projection`
- **execution_contract**: 将独立 PDCA 不变量投射到阶段门禁；删除 children 强制条件并更新回归测试；保持其他 Plan 门禁不变；以无 children 任务不再出现 TICKETS_MISSING 为完成信号。
- **summary**: 修复旧 ticket 门禁阻止独立 PDCA 进入 Do 的本体实现偏差。
- **current behavior**: 无 parent、无 children 的任务即使完成 Plan 也被拒绝执行。
- **desired behavior**: 每个任务独立完成生命周期，任务关系只用于拆分与调度。
- **key interfaces**: Plan→Do 语义门禁、任务关系字段、阶段转换器和门禁回归测试。
- **acceptance criteria**: 运行三个专业职责的独立任务门禁测试均不产生 TICKETS_MISSING，其他 Plan 门禁回归保持通过。
- **out of scope**: 场景本体清理、Agent runtime 全量投射和任务关系数据迁移。
- **information gaps**: 无；拒绝 receipt 已精确定位冲突分支。
- **dedup results**: 现有 leaf exemption 只豁免有 parent 叶任务，不能满足独立 PDCA；需替换而非扩展该旧规则。
- **recommended next steps**: 用户确认后由全新子 Agent 实现最小投射、登记证据并停留在 Do 等待符合性验证。

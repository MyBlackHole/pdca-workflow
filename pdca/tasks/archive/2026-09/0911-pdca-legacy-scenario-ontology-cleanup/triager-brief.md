# Triage Brief — pdca-legacy-scenario-ontology-cleanup

- **category**: enhancement
- **ontology_role**: `ontology_modeling`
- **execution_contract**: 产出无旧场景控制语义的 PDCA 核心权威模型；盘点入口、分类命中、修订节点、删除旧规则并验证；不修改 runtime 或历史记录；以全入口零控制命中和本体校验通过为完成信号。
- **summary**: 清除仍与已确认 PDCA 根本体冲突的六场景、A/B/C 和 `scenario_type` 控制语义。
- **current behavior**: 根本体采用三个专业职责，但部分流程、阶段和分诊入口仍按旧场景分类或路由。
- **desired behavior**: 三个专业职责与四字段执行契约成为唯一工作控制来源，具体 skill 仅作为工具被选择。
- **key interfaces**: 全局代理入口、阶段流程本体、阶段概念、分诊协议、技能索引和本体关系图。
- **acceptance criteria**: 运行核心权威入口残留扫描得到零个旧控制语义命中；运行本体契约、孤岛、技能索引和收敛校验全部通过。
- **out of scope**: runtime 字段迁移、历史事实改写、工具 skill 删除和 Agent 隔离实现投射。
- **information gaps**: 无；控制语义与允许语义的分类边界已在 PRD 明确。
- **dedup results**: T2175 Act 回顾确认这是根本体任务范围外的仓库级残留，需由新的独立 PDCA 承担。
- **recommended next steps**: 完成一轮 Plan 确认后，由全新子 Agent 自主执行本体建模与证据登记。

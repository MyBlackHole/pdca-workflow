# Triage Brief — 0910-process-complexity-review

- **category**: enhancement
- **scenario_type**: research
- **summary**: 调研PDCA流程是否太复杂、能否简化，为何本体承载下仍有75个py脚本
- **current behavior**: 门禁与脚本持续叠加，用户体感复杂；T2104/05已做简化必要性/方案方向初探
- **desired behavior**: 量化复杂度来源，判定简化空间，给出本体与脚本的职责边界结论
- **key interfaces**: ontology元本体节点、scripts投射层、门禁调用链
- **acceptance criteria**: 脚本数与职责有统计；每结论有file:line或命令复核途径；报告过图/网络门禁
- **out of scope**: 不实际删脚本改门禁，仅调研结论
- **information gaps**: 简化判据（删什么、留什么）需对齐
- **dedup results**: T2104/05为子问题初探，本任务为全景判定，无重复
- **recommended next steps**: 按skill-research产报告并登记

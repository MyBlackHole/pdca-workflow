# Triage Brief — 0910-research-first-compliance-audit

- **category**: enhancement
- **scenario_type**: review
- **summary**: 审查六场景现行机制是否满足任务必须先调研产出本体的要求
- **current behavior**: T2092先调研门禁已上线，T0513起Act强制回写；但research自指局限待升级，部分存量plan任务未补调研
- **desired behavior**: 双轴并行审查，给出每场景满足/不满足判定与缺口定位
- **key interfaces**: RESEARCH_FIRST门禁、ontology-ready、Act回写门禁、settlement校验
- **acceptance criteria**: 运行门禁测试判满足；逐场景结论可回链到file:line；证据已登记
- **out of scope**: 不改门禁代码，仅审查判定
- **information gaps**: 满足标准（先调研+产本体双条件）与自指局限是否计为不满足需对齐
- **dedup results**: T2072为旧口径判定，T2073为回写审查，本任务为新门禁上线后的合规复审，无重复
- **recommended next steps**: 双轴子票产review.md并登记

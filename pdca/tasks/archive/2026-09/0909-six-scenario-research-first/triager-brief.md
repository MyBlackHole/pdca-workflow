# Triage Brief — 0909-six-scenario-research-first

- **category**: enhancement
- **scenario_type**: research
- **summary**: 分析六场景是否使用严格先调研后操作，产出带可复核途径的结论报告
- **current behavior**: 六场景Do路径文档分散，未有统一是否先调研矩阵
- **desired behavior**: 逐场景核验Do准入ontology-ready、执行是否消费本体、Act是否回写本体，给出是否严格结论
- **key interfaces**: pdca-gate-do准入、ontology-ready判定、scenario-boundary-rule裁决、research本体沉淀
- **acceptance criteria**: 运行验证命令得到门禁通过；每场景结论可回链到file:line；research-report已登记为证据
- **out of scope**: 不改门禁代码，仅做调研判定；不产出可执行功能代码
- **information gaps**: 无，已Grill对齐口径为A（fragment合法即算先调研）
- **dedup results**: 检索pdca/tasks含0903-review-research-dev-mismatch相关但无相同六场景矩阵，属新调研
- **recommended next steps**: 按skill-research产research-report.md并登记证据

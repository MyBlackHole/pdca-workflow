# Triage Brief — 0910-research-first-gate

- **category**: enhancement
- **scenario_type**: development
- **summary**: 落实任务必须先调研：Do前须有已完成的调研依据，不止于复用fragment
- **current behavior**: ontology-ready仅要求fragment存在合法即可放行，复用旧本体无须任何本次调研动作；T2072口径A确认此现状
- **desired behavior**: 全场景development/bugfix/research/documentation/design/review进入Do前须出示本次调研证据二选一（链内research子票已归档，或本次research-report通过mermaid≥3/Source≥3/http≥1/URL≥2）；仅ontology_exempt自举豁免，无父链继承
- **key interfaces**: pdca-gate-do准入、task_identity亲子链、research-report门禁、convergence回链
- **acceptance criteria**: 运行门禁测试先调研缺失判失败、齐备通过；全量门禁测试通过
- **out of scope**: 不改research本身图门禁；不动Act回写链
- **information gaps**: 何为有效调研、适用场景范围、自举豁免外是否还有豁免需对齐
- **dedup results**: T2072为判定口径现状，T2081为URL门禁，T2084为叶豁免，均无先调研动作门禁，属新需求无重复
- **recommended next steps**: Grill定口径后TDD实现门禁与测试

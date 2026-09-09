# Triage Brief — 0910-scope-coverage-impl

- **category**: enhancement
- **scenario_type**: development
- **summary**: 实现覆盖判定器：do→check硬门禁验diff ⊆ triage声明集
- **current behavior**: T2112只产出设计，scope-declare判定无代码实现
- **desired behavior**: 新增判定脚本与测试，triage产声明，do→check硬门禁，pre-commit仅告警
- **key interfaces**: git diff名集、scope-declare.json、gate_issues do分支、convergence回链
- **acceptance criteria**: 缺声明判失败覆盖通过；全量门禁测试通过；文档同步
- **out of scope**: 不改先调研与TICKETS门禁；不碰他人任务
- **information gaps**: 无，口径已定do-check硬门禁+triage产声明
- **dedup results**: T2112为设计，本任务为实施，无重复
- **recommended next steps**: TDD判定器与测试，文档同步

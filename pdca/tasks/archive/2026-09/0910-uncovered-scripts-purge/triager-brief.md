# Triage Brief — 0910-uncovered-scripts-purge

- **category**: enhancement
- **scenario_type**: development
- **summary**: 删除PDCA流程本体未覆盖的逻辑脚本，逐项确认后删，全绿回归
- **current behavior**: 76脚本中35无PDCA流程引用，其中部分为匹配器误判（改进环概念节点），部分被测试引用，部分疑似并发在用
- **desired behavior**: 覆盖判据对齐后出dry-run分级清单，用户逐项确认，删后pytest全绿，可revert提交
- **key interfaces**: ontology映射扫描、tests引用、跨脚本import、.github/skill调用、git近期使用
- **acceptance criteria**: 判据落盘；清单逐项有去留结论；删后全绿且validate通过
- **out of scope**: 不动门禁语义；不碰他人未提交文件归属判定只读
- **information gaps**: 覆盖范围、测试引用与并发在用三条红线需对齐
- **dedup results**: T2111为归因，本任务为执行清理，无重复
- **recommended next steps**: Grill定判据后dry-run分级

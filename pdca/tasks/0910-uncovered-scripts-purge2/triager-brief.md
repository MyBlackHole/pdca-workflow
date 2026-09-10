# Triage Brief — 0910-uncovered-scripts-purge2

- **category**: enhancement
- **scenario_type**: development
- **summary**: T2127后第二轮purge：对当前scripts/全量重审残留脚本本体覆盖，逐项裁决后删，全绿回归
- **current behavior**: T2127已删25留10并归档，结论冻结于当时点；当前scripts/约50项，含T2127后新增（如resolve-ai-*第三件、scenario-boundary-check、run-ai-friendliness-fixtures等），覆盖状态未知
- **desired behavior**: 沿用T2127判据（运行时导入/kept调用/CI链/他人在途四类保留）出dry-run分级清单，用户逐项确认，删后pytest全绿且validate通过，可revert提交
- **key interfaces**: ontology映射扫描、tests引用、跨脚本import、.github/skill调用、git近期使用
- **acceptance criteria**: dry-run清单逐项有去留结论；删除后全绿已提交可revert；收敛valid:true且证据已登记
- **out of scope**: 不改门禁语义；不碰他人未提交文件归属判定只读；T2127已删不重审
- **information gaps**: 无，范围/判据/强度三题已确认（全量重审＋沿用判据＋dry-run先行）
- **dedup results**: T2127为第一轮已归档，本任务为第二轮，无重复
- **recommended next steps**: 复核判据适用性后出dry-run分级清单，用户逐项确认后删除回归

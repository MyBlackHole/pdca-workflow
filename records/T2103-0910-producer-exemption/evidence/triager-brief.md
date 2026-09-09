# Triage Brief — 0910-producer-exemption

- **category**: enhancement
- **scenario_type**: development
- **summary**: research票豁免自身先调研门禁（生产者豁免），他人引用仍须证据
- **current behavior**: 新鲜research叶票无子票无报告即RESEARCH_FIRST_MISSING阻断，自指无收敛；测试用例锁定该行为
- **desired behavior**: scenario==research豁免自身门禁；非research判定不变；测试更新为豁免断言
- **key interfaces**: pdca_core先调研门禁段、test_research_first_gate自指用例、本体节点testable_signal
- **acceptance criteria**: 运行门禁测试research叶放行；非research无证据仍阻断；全绿
- **out of scope**: 不动二选一证据定义；不动豁免外场景
- **information gaps**: 无，口径已拍板生产者豁免
- **dedup results**: T2092锁定自指局限，本任务为其升级项，无重复
- **recommended next steps**: TDD改断言→改门禁→回归

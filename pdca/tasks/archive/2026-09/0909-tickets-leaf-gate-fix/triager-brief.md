# Triage Brief — 0909-tickets-leaf-gate-fix

- **category**: enhancement
- **scenario_type**: development
- **summary**: 修复TICKETS_MISSING对非research叶票的无限递归，叶票应可单票执行
- **current behavior**: plan态非research无children即阻plan→do，叶票再拆孙票无收敛；T2074/T2075/T2082/T2083四次命中后绕行转research
- **desired behavior**: 叶票豁免或仅父票卡，回归测试锁定，occurrence FE-fcc29闭环
- **key interfaces**: pdca_core gate_issues TICKETS段、transition-phase、task_identity
- **acceptance criteria**: 运行复现测试叶票放行；全量门禁测试通过；T2074类场景不再阻断
- **out of scope**: 不动其它门禁码，仅TICKETS段
- **information gaps**: 豁免口径（叶票定义）需对齐
- **dedup results**: 无相同修复任务，来源occurrence FE-fcc29
- **recommended next steps**: TDD复现→修复→回归，登记证据

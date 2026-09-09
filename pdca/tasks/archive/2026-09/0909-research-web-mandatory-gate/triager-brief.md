# Triage Brief — 0909-research-web-mandatory-gate

- **category**: enhancement
- **scenario_type**: development
- **summary**: research强制网络查询门禁：至少1 websearch+1 webfetch/context7并列URL，缺失阻断
- **current behavior**: skill-research只卡mermaid/Source，web-research为manual可选，T2072/T2073靠自觉补查
- **desired behavior**: 新增可回归校验脚本+测试，更新skill-research门禁，内部纯代码审查可豁免需论证
- **key interfaces**: skill-research图门禁、skill-web-research策略、register-evidence kind、settlement校验
- **acceptance criteria**: 运行校验脚本对缺URL报告失败；有URL通过；测试全绿
- **out of scope**: 不改flow-act改进授权链，仅加Do门禁
- **information gaps**: 豁免口径与URL计数规则需对齐
- **dedup results**: 无相同门禁任务，T2073记改进候选来源
- **recommended next steps**: TDD实现校验脚本与测试，更新skill，登记证据

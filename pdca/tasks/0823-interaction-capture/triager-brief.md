# Triage Brief — interaction-capture

- **category**: enhancement
- **scenario_type**: development
- **summary**: 真实用户交互捕获机制：provenance 标记 + 元反馈类型 + HITL 红线
- **current behavior**: 用户输入未落盘；AI 代填 Q&A 污染数据源且与真实输入不可区分
- **desired behavior**: captured 双态标记、user_meta_feedback 类型、三条既有元反馈补录
- **key interfaces**: clarifications.jsonl 格式、skills/grilling、flows/flow-{plan,check}
- **acceptance criteria**: 运行 grep -c user_meta_feedback pdca/tasks/*/clarifications.jsonl 得到>=3；运行门禁冒烟证明新字段不被拒
- **out of scope**: question 平台工具改造、历史存量清洗
- **information gaps**: task.schema.json 是否管控 clarifications.jsonl（Do 首步核实）
- **dedup results**: improvement_source=T0374 用户反馈，无重复
- **recommended next steps**: 终审后实施

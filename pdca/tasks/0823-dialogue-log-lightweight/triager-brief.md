# Triage Brief — dialogue-log-lightweight

- **category**: enhancement
- **scenario_type**: documentation
- **summary**: 阶段边界对话摘要轻量存档机制
- **current behavior**: 对话推理路径与被否备选随会话消失
- **desired behavior**: 每次阶段转换前追加 <=2KB 四要素摘要到 dialogue-log.md
- **key interfaces**: skills/handoff-work、flows 四转换步骤
- **acceptance criteria**: 运行 cat pdca/tasks/0823-dialogue-log-lightweight/dialogue-log.md 得到首份合规摘要
- **out of scope**: 全量逐句、平台导出、历史回填
- **information gaps**: 无
- **dedup results**: 与 T0375 互补（彼为决策点捕获，此为过程轨迹），无重复
- **recommended next steps**: 终审后实施并自反产出首份摘要

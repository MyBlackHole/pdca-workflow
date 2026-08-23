# Triage Brief — history-review-self-improve

- **category**: enhancement
- **scenario_type**: review
- **summary**: 历史任务流程质量全量审查 + AI 执行者失误复盘
- **current behavior**: 从未系统审查历史任务执行质量；AI 操作失误散落在 transition 拒绝记录中未被结构化
- **desired behavior**: 量化扫描+抽样审读+失误清单+三层处置
- **key interfaces**: task.schema.json、transition-phase.py 门禁、pdca-doctor、records 证据链
- **acceptance criteria**: 运行 cat records/T0374-0823-history-review-self-improve/review-report.md 得到含5项AC覆盖的审查报告
- **out of scope**: 不改历史任务文件；不实施防再发措施
- **information gaps**: 无
- **dedup results**: R0142-clean-invalid-active-history 为数据清理非质量审查；无重复
- **recommended next steps**: 终审后 F1 扫描

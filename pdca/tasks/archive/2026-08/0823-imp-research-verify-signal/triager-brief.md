# Triage Brief — imp-research-verify-signal

- **category**: enhancement
- **scenario_type**: documentation
- **summary**: research 结论强制附可复核验证途径
- **current behavior**: 4/4 抽查样本 conclusion 无系统验证途径章节
- **desired behavior**: research SKILL 规则 + C2 审查项 + baseline 豁免
- **key interfaces**: skills/research/SKILL.md、flow-do C2、skill-content-baseline.json
- **acceptance criteria**: 运行 grep -A3 "验证途径" skills/research/SKILL.md 得到规则条目；运行 python3 scripts/audit-skill-content.py 零 budget issue
- **out of scope**: 脚本逻辑、历史 conclusion 追溯
- **information gaps**: 无
- **dedup results**: improvement_source=T0371 E-1，无重复
- **recommended next steps**: 终审后实施

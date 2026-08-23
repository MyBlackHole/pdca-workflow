# Triage Brief — imp-completion-criterion-phase-boundary

- **category**: enhancement
- **scenario_type**: documentation
- **summary**: 合入 completion-criterion 杠杆与 phase-boundary 决策树两处文档增补
- **current behavior**: 完成标准节仅好坏例；handoff-work 无清窗时机指引
- **desired behavior**: 第五杠杆完整理论入 writing-great-skills；五选项树入 handoff-work；baseline 豁免同步
- **key interfaces**: writing-great-skills 完成标准节、handoff-work 模板节、skill-content-baseline.json
- **acceptance criteria**: 运行 cat skills/writing-great-skills/SKILL.md 得到含 clarity/demand 双性质的杠杆节；运行 python3 scripts/audit-skill-content.py 得到零 budget issue
- **out of scope**: flow-do 主文件、门禁脚本、六路径 Done when 全量化
- **information gaps**: 无
- **dedup results**: improvement_source=T0371，无重复立项
- **recommended next steps**: 终审后 Do 实施

# Triage Brief — T0233

## 分类
- category: enhancement
- scenario_type: development
- 触发：穷尽审查 mattpocock/skills 全部 37 技能，确认 to-spec 的"seam 先确认"是唯一剩余实质可证明候选。

## 查重结果
- T0230-T0232 已落地 grilling 批量问法 / source 契约 / DAG ready-set / 词汇契约，均不涉及 seam 确认。
- knowledge/ 无 seam 契约既有实现。
- flow-plan 无 seam 用户确认门禁；SPEC.md 有 Seam 章节但流程不强制确认。

## 验证结果
- mattpocock `to-spec/SKILL.md:6-9` 明确"Check with the user that these seams match their expectations"（已读原文）。
- PDCA `flows/flow-plan/SKILL.md` P1-P3 无 seam 确认步骤。
- PDCA `skills/tdd/SKILL.md:24` 在 Do 阶段兜底 seam 确认——返工成本高。
- 契约测试先例：T0231 source 契约、T0232 词汇契约，同构可复用。

## 信息缺口
- seam 确认放 flow-plan 位置。
- 契约测试的 seam 解析方式。
- 覆盖范围与追溯策略。

## 建议下一步
按 flow-plan P2 Grill 逐轮对齐，再 PRD、P6 终审。

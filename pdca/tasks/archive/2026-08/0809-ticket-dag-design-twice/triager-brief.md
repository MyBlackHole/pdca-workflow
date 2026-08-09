# Triage Brief — T0232

## 分类
- category: enhancement
- scenario_type: development
- 触发：审查 mattpocock/skills 剩余可借鉴可证明机制，用户确认落地 #3 + #2。

## 查重结果
- T0230（grilling frontier 批量问法）、T0231（source 术语一致性）：已归档，frontier 语义为"可答问题集合"，与本次"可并行任务集合"不同，不冲突但需消歧。
- knowledge/ 无 blocking edges / design-it-twice 既有实现。
- skills/to-tickets/SKILL.md 无显式依赖边。

## 验证结果
- mattpocock `to-tickets/SKILL.md:29-40` 含 blocking edges 显式声明机制（已读原文）。
- mattpocock `codebase-design/DESIGN-IT-TWICE.md` 含 design-it-twice 并行 sub-agent 接口双方案流程（已读原文）。
- mattpocock `codebase-design/SKILL.md` 提供强制词汇表（module/interface/seam/adapter/depth）+ deletion test（已读原文）。
- PDCA `skills/to-tickets/SKILL.md` 现无依赖边、无 DAG/frontier 校验。
- PDCA 无 design-it-twice 机制，无词汇契约测试。

## 信息缺口
- 落地形态：to-tickets 扩展 vs 新技能。
- frontier 测试 fixture 设计。
- design-it-twice 独立技能 vs 并入。
- 词汇契约测试范围。

## 建议下一步
按 flow-plan P2 走 Grill 逐轮对齐，再出 PRD、P6 终审。

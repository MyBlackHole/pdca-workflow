# P2 改进项实施（Negative Space/cache/to-questionnaire/wait-wait/HITL-AFK）

## 背景

T0450 审查识别的 P2 改进项。本任务实施剩余 5 项 P2 改进。

## 验收标准

- [ ] AC-1：补充 Negative Space 失败模式到 skill-writing-great-skills.md
- [ ] AC-2：补充 cache 概念到 skill-writing-great-skills.md
- [ ] AC-3：新增 to-questionnaire 技能节点
- [ ] AC-4：新增 wait-wait 技能节点
- [ ] AC-5：引入 HITL/AFK 分类到 wayfinder
- [ ] AC-6：所有改进后 ontology-validate 通过且 islands: 0

## 收敛条件

- convergence-map 逐条回链 PRD AC 到 evidence ID
- 所有改进项关联本体节点
- 改进后 ontology-validate 通过且 islands: 0

## 改进清单

| 编号 | 改进项 | 关联本体节点 | 验证方式 |
|------|--------|-------------|----------|
| P2-1 | Negative Space 失败模式 | `ontology:domain/skill-writing-great-skills.md` | 内容对照 |
| P2-2 | cache 概念 | `ontology:domain/skill-writing-great-skills.md` | 内容对照 |
| P2-3 | to-questionnaire 技能 | `ontology:domain/skill-to-questionnaire.md` | 节点创建 + 校验 |
| P2-4 | wait-wait 技能 | `ontology:domain/skill-wait-wait.md` | 节点创建 + 校验 |
| P2-5 | HITL/AFK 分类到 wayfinder | `ontology:domain/skill-wayfinder.md` | 内容对照 |
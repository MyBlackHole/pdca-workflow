# 实施本体论改进计划（P0/P1/P2）

## 背景

T0450 审查识别出本体论在闭环融入和 mattpocock/skills 对照中的改进空间。本任务按 P0→P1→P2 优先级实施改进计划，每项改进关联本体节点或任务。

## 验收标准

- [ ] AC-1：完成 P0 改进（writing-for-agents 重构、skill-mechanics 节点、skill-invocation-contract 节点），ontology-validate 通过
- [ ] AC-2：完成 P1 改进（ask-matt/prototype/tdd/research/triage 更新），ontology-validate 通过
- [ ] AC-3：完成 P2 改进（Negative Space/cache/to-questionnaire/wait-what/HITL-AFK），ontology-validate 通过
- [ ] AC-4：所有改进后 `ontology_graph` 无新增孤岛
- [ ] AC-5：更新 journal 并记录 disposition

## 收敛条件

- convergence-map 逐条回链 PRD AC 到 evidence ID
- 所有改进项关联本体节点
- 改进后 `ontology-validate.py` 通过且 `islands: 0`

## 范围边界

- 本任务为 development 类型，按 scenario_type 路由执行
- 每个优先级建议创建子任务独立推进
- 改进需通过 `ontology-check` 门禁

## 改进清单

### P0（立即实施）

| 编号 | 改进项 | 关联本体节点 | 验证方式 |
|------|--------|-------------|----------|
| P0-1 | 重构 writing-for-agents：拆分 SKILL.md + SKILL-MECHANICS.md | `ontology:domain/skill-writing-great-skills` | 内容对照 + 校验 |
| P0-2 | 新增 skill-mechanics 概念节点 | `ontology:concept/skill-mechanics` | 节点创建 + 校验 |
| P0-3 | 新增 skill-invocation-contract 概念节点 | `ontology:concept/skill-invocation-contract` | 节点创建 + 校验 |

### P1（近期实施）

| 编号 | 改进项 | 关联本体节点 | 验证方式 |
|------|--------|-------------|----------|
| P1-1 | 更新 ask-matt 扩展 phase boundaries 决策树 | `ontology:domain/skill-ask-matt.md` | 内容对照 |
| P1-2 | 更新 prototype 增加 HTML 分支和 throwaway branch | `ontology:domain/skill-prototype.md` | 内容对照 |
| P1-3 | tdd 改为 reference-only，增加 tautological-test | `ontology:domain/skill-tdd.md` | 内容对照 |
| P1-4 | research 增加 subagent 并行 burn-down | `ontology:domain/skill-research.md` | 内容对照 |
| P1-5 | triage 增加外部 PR 处理 | `ontology:domain/skill-triage.md` | 内容对照 |

### P2（概念补充）

| 编号 | 改进项 | 关联本体节点 | 验证方式 |
|------|--------|-------------|----------|
| P2-1 | 补充 Negative Space 失败模式 | `ontology:domain/skill-writing-great-skills.md` | 内容对照 |
| P2-2 | 补充 cache 概念 | `ontology:domain/skill-writing-great-skills.md` | 内容对照 |
| P2-3 | 新增 to-questionnaire 技能 | `ontology:domain/skill-to-questionnaire.md` | 节点创建 + 校验 |
| P2-4 | 新增 wait-what 技能 | `ontology:domain/skill-wait-what.md` | 节点创建 + 校验 |
| P2-5 | 引入 HITL/AFK 分类到 wayfinder | `ontology:domain/skill-wayfinder.md` | 内容对照 |

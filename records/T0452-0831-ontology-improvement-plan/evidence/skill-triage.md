---
schema: pdca.asset/v1
id: ontology:domain/skill-triage
name: triage
summary: Triage incoming tasks and prioritize based on impact and urgency.
description: |
  Classify issues as bug or enhancement, check for duplicates, verify the claim,
  grill if needed, and output an agent-ready task.json + prd.md + brief.
  
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
---

--

Run `$PDCA_HOME/skills/triage-work/SKILL.md`.

## External PR 处理

Triage 扩展以处理外部 pull requests：

- PR 视为带附件的 issue，走相同角色、状态机和流程
- Discovery 仅暴露外部 PR
- bug-only 的"reproduce"步骤泛化为"verify the claim"
- 冗余检查解析已实现请求为 `wontfix`

## 已知坑

- 查重须搜活跃+归档 task 与 knowledge，事实性 claim 用代码/文档验证而非询问用户。
- PR 处理需 `triage` skill 已安装；外部 PR 默认关闭，需在 setup 中启用。

---
schema: pdca.asset/v1
id: ontology:domain/skill-domain-modeling
name: domain-modeling
summary: Create and maintain domain models for the PDCA workflow system.
description: |
  在 Grill 过程中或独立对话中，主动构建和打磨项目的共享语言。
  模糊术语落定后立即写入 CONTEXT.md，硬决策记录为 ADR。
  
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


--

Run `$PDCA_HOME/skills/domain-modeling-work/SKILL.md`.

## 已知坑

- 共享语言勿造生僻自造词；每个术语须有明确定义，模糊术语立即更新 CONTEXT.md。

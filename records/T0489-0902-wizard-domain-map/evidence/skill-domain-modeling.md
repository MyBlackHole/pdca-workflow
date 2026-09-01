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

## 文件结构（单/多上下文）

- 单上下文：`CONTEXT.md` 于根 + `docs/adr/`
- 多上下文：`CONTEXT-MAP.md` 于根路由，每 bounded context 独立 `CONTEXT.md`（如 `src/ordering/CONTEXT.md`）+ 分层 `docs/adr/`
- 惰性创建：仅当有可写术语/决策时才建文件；无 MAP 即单上下文

## 多上下文路由

1. 读 `CONTEXT-MAP.md` 定位所属上下文
2. 术语更新写入对应 `CONTEXT.md`，跨上下文冲突在 MAP 层决策
3. ADR 按 system-wide vs context-specific 分层

## 已知坑

- 共享语言勿造生僻自造词；每个术语须有明确定义，模糊术语立即更新 CONTEXT.md。
- 多上下文下勿将 system-wide 决策写入单 context ADR。

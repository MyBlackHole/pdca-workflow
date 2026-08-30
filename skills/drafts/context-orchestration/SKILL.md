---
name: context-orchestration
description: |
  知识资产分层、溯源、检索评估与 AI 提效方法调研
status: draft
source_record: records/T0075--07-26-调研知识资产管理与-ai-提效方法/conclusion.md
---

# context-orchestration

## 来源经验

`records/T0075--07-26-调研知识资产管理与-ai-提效方法/conclusion.md`

## 适用边界

- 发布前必须由用户或审查流程确认。
- 该草稿来自经验记录，不代表已验证为全局规则。

## 经验摘要

---
schema: pdca.asset/v1
id: conclusion:T0075--07-26-调研知识资产管理与-ai-提效方法
layer: experience
summary: 知识资产分层、溯源、检索评估与 AI 提效方法调研
tags: [knowledge-management, ai-efficiency, rag, provenance, pdca]
scenarios: [research, default, software-development, code-review]
phases: [do, check, act]
applies_when: [设计集中式知识资产管理、AI 上下文检索或任意场景的 PDCA 知识闭环]
excludes_when: [需要未经验证的自动知识发布]
source_ids: [evidence:T0075--07-26-调研知识资产管理与-ai-提效方法:sha256:7cfbe39c1fa5c7d06c8688b48cbb972800381d3609fde176152279e46dfcd720]
confidence: high
status: active
---

# 结论

## 假设验证

成立。分层、来源链、最小上下文、检索/生成评估和 PDCA 闭环共同构成比无结构文档堆积更可靠的 AI 提效基础；但语义正确性仍必须由 validator 和人工边界控制。

## 结果

- 完成 8 个来源的调研，覆盖知识管理、溯源、RAG、评估、Agent 指令和可信度风险。
- 明确 Evidence、Experience、Knowledge、Skill 四层边界和单向来源链。
- 形成任务指纹 → 候选资产 → 证据核验 → 最小上下文 → 执行 → 经验/知识/技能投影闭环。
- 给出软件开发、资料调研、代码/文档审查和日常工作的应用方式。
- 输出 `knowledge/research/knowledge-assets-ai-efficiency.md`，满足 PRD 的来源、范围和落地建议验收标准。

## 边界与下一轮

- 本调研没有建立真实生产数据集，因此没有给出检索 Recall、Groundedness 或延迟的实测值。
- 下一步应建立小型评估集，记录 retrieval、groundedness、relevance、completeness 和误报反馈。
- Knowledge/Skill 的自动投影只能生成草稿，必须经过 evidence、Check 和 disposition。

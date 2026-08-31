---
schema: pdca.asset/v1
id: ontology:domain/ai-efficiency-knowledge-assets-and-ai-workflow
type: domain
layer: Knowledge
status: active
summary: 知识资产与 AI 工作流
domain:
- ontology:domain/ai-efficiency
relations:
  specializes:
  - ontology:domain/ai-efficiency
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 检查资产 source_ids 非空且可追溯至 Evidence/Experience，并对抽样查询执行 retrieval/groundedness/relevance/completeness 四维评估达标，缺失来源链或任一维度未通过时报告具体资产与维度
---

---
schema: pdca.asset/v1
id: knowledge:ai-efficiency.knowledge-assets-and-ai-workflow
layer: knowledge
summary: 以分层、来源链、最小上下文和验证闭环管理知识资产并提升 AI 效率
tags: [knowledge-management, ai-efficiency, rag, provenance, pdca]
scenarios: [research, default, software-development, code-review]
phases: [plan, do, check, act]
applies_when: [需要为任意场景建立可检索、可追溯和可复用的 AI 知识上下文]
excludes_when: [需要未经验证的自动知识发布]
source_ids: [experience:T0075--07-26-调研知识资产管理与-ai-提效方法]
confidence: high
status: active
---

# 知识资产与 AI 工作流

## 核心结论

知识资产应分为 Evidence、Experience、Knowledge、Skill 四层：Evidence 保存不可变事实，Experience 保存单次任务结论，Knowledge 保存跨任务稳定规律，Skill 保存可执行步骤。来源链必须保持 `Skill → Knowledge/Experience → Evidence`，不能把模型摘要直接当作事实。

AI 提效的可靠闭环是：

```text
任务指纹 → 候选资产 → 来源核验 → 最小上下文 → 执行 → Check → Experience → Knowledge/Skill 草稿
```

检索应同时考虑场景、阶段、标签、可信度、时效和适用边界；默认只注入最小可信上下文。RAG 输出必须分别评估 retrieval、groundedness、relevance 和 completeness。未通过 evidence、validator 和 Check 的结论不得自动投影为 Knowledge 或 Skill。

## 落地规则

- 每项资产记录 `source_ids`、`scenarios`、`phases`、`confidence`、`status` 和版本关系。
- 任务开始先检索 Knowledge，只有需要核验时才展开 Experience/Evidence。
- 软件开发用历史架构、失败经验和测试策略减少上下文准备；调研用来源分级和冲突保留避免把搜索摘要当事实；审查用 Skill 固化清单并要求 finding 绑定证据；日常 journal 先作为 Experience 候选。
- 资产生命周期至少包含 draft、active、superseded、retired；冲突和 misleading 反馈不能静默覆盖。

## 边界

本知识来自一次调研，尚未建立生产检索评估集；后续需测量召回、groundedness、完整性、延迟和误报率。

---
schema: pdca.asset/v1
id: ontology:domain/workflow-code-review-dual-axis
type: domain
layer: Knowledge
status: active
summary: 双轴代码审查模式
domain:
- ontology:domain/workflow
relations:
  specializes:
  - ontology:domain/workflow
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


---
schema: pdca.asset/v1
id: knowledge:workflow.code-review-dual-axis
layer: knowledge
summary: 将代码审查拆分为标准轴和规范轴并行运行，防止单一维度掩盖问题
tags: [code-review, quality]
scenarios: [code-review, software-development]
phases: [do, check]
applies_when: [进行正式代码审查]
excludes_when: []
source_ids: []
confidence: high
status: active
---

# 双轴代码审查模式

## 概念
将代码审查拆分为两个独立维度并行运行，防止单一维度掩盖另一维度的问题。

## 双轴定义

| 轴 | 审查内容 | 评判标准 |
|----|----------|----------|
| **标准轴** | 编码规范、代码坏味 | 项目文档标准 + Fowler 坏味基线 |
| **规范轴** | 功能实现正确性 | 原始 PRD / spec / issue |

## 适用场景
- 任何需要正式代码审查的变更
- 特别适用于：大变更、跨团队 PR、安全敏感代码

## 关键规则
- 两个轴由独立子代理并行执行，互不污染上下文
- 不合并、不排序报告，各自独立呈现
- 结尾只做每轴发现计数，不做跨轴排名

## 为什么需要两个轴
同一变更可能通过一轴而失败另一轴：
- **标准通过、规范失败**：代码合规但实现错误功能
- **规范通过、标准失败**：功能正确但破坏编码规范

## 参考实现
- `skills/code-review/SKILL.md`

## 坏味基线（Fowler 《Refactoring》 ch.3）
参见 `skills/code-review/SKILL.md` 中的完整 12 种坏味列表。始终是判断（judgement call）而非硬性违规，项目文档标准优先。
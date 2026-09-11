---
schema: pdca.asset/v2
id: ontology:domain/skill-bug-commit-format
name: bug-commit-format
summary: Commit bug fixes with structured format including description, root cause, solution, impact scope, and
  performance impact.
description: Use when fixing bugs and committing changes — commit messages must include bug description, root cause,
  solution, impact scope, and performance impact
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/skill-bug-commit-format/3.1.0
relations:
  relates_to:
  - ontology:pattern
  - ontology:concept/writing-for-agents
  - ontology:concept/pdca-task
  instance_of:
  - ontology:concept/knowledge-artifact
revision: 3.1.0
authority: reference
validation:
  structural_checks:
  - 递归解析本节点身份及关系列表；目标 ID 必须可定位。引用数量不作为行为验证。
  claim_status: unverified
  adoption: claim_review_required
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

---
name: bug-commit-format
description: Use when fixing bugs and committing changes — commit messages must include bug description, root cause, solution, impact scope, and performance impact
---

# Bug Commit Format

## 模板
```
【B-xxxx】: {简短标题}

## 问题描述
<现象+复现步骤>

## 根因
<为什么会发生>

## 解决方案
<怎么修复的>

## 影响范围
<影响的模块/用户/版本>

## 测试验证
- [ ] 复现步骤已验证通过
- [ ] 回归测试通过
```

## 铁律
- 每个 commit 只修复一个 bug
- 标题 ≤72 字符，动词开头（fix/修复）
- 根因 ≠ 现象，必须追到代码/配置/流程层面且与诊断假设的双向预测一致；区分三类：假设/设计错误、实现/环境错误、流程/证据遗漏
- 影响范围必须有具体模块名
- 未获 `fix_confirmation:confirmed` 不得提交修复（Do 内修复前确认门禁）

## 已知坑

- commit 信息必须含 bug 描述、根因、解决方案、影响范围与性能影响；缺根因说明的提交会被驳回。
- 根因≠现象：未区分三类或与上游诊断假设不一致的“根因”是猜测，需经 `fix_confirmation` 验证。

---
schema: pdca.asset/v2
id: ontology:domain/skill-feature-commit-format
name: feature-commit-format
summary: Commit new features with structured format including requirement description, background, implementation,
  impact scope, and testing verification.
description: Use when implementing new features and committing changes — commit messages must include requirement
  description, background, implementation, impact scope, and testing verification
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/skill-feature-commit-format/3.1.0
relations:
  relates_to:
  - ontology:concept/writing-for-agents
  - ontology:concept/triage
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
name: feature-commit-format
description: Use when implementing new features and committing changes — commit messages must include requirement description, background, implementation, impact scope, and testing verification
---

# Feature Commit Format

## 模板
```
【F-xxxx】: {简短标题}

## 需求背景
<为什么要做>

## 实现方案
<怎么实现的，关键决策点>

## 影响范围
<新增/修改的文件模块>

## 测试验证
- [ ] 单元测试覆盖核心逻辑
- [ ] 集成测试覆盖边界
- [ ] 手动验证通过
```

## 铁律
- 每个 commit 一个 feature（可拆多个 commit）
- 标题 ≤72 字符，动词开头（feat/添加/实现）
- 实现方案需说明关键设计决策及替代方案
- 影响范围列出新增和修改的主要模块

## 已知坑

- commit 信息须含需求描述、背景、实现、影响范围与测试验证；缺验证说明的新功能提交会被驳回。

---
schema: pdca.asset/v1
id: ontology:domain/skill-feature-commit-format
name: feature-commit-format
summary: Commit new features with structured format including requirement description, background, implementation, impact scope, and testing verification.
description: Use when implementing new features and committing changes — commit messages must include requirement description, background, implementation, impact scope, and testing verification
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/writing-for-agents
    - ontology:concept/triage
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

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

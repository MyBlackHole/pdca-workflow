# PRD（转向修订版 r2） — 覆盖门禁设计

## 背景
r1行级hunk映射已作废（round2决议）。本质要求：实现内容/逻辑须在本体记录中事先具备。

## 验收标准

- [ ] AC-1: 覆盖口径已对齐（具名声明制）
- [ ] AC-2: 双方案对比已产出，推荐有接口契约与测试seam
- [ ] AC-3: design已登记，收敛valid:true

## 关联本体节点

```
ontology:domain/skill-codebase-design
ontology:domain/design-it-twice
ontology:concept/pdca-evidence
```

## 拆分映射

- 覆盖判定设计 -> ontology:domain/design-it-twice
- 接口契约 -> ontology:domain/skill-codebase-design
- 证据锚定 -> ontology:concept/pdca-evidence

## 具备定义
改动触及的模块/逻辑须在任务`ontology_fragment`子树节点或`PRD`中有具名声明，否则阻断；事后回链不能替代事前具备。

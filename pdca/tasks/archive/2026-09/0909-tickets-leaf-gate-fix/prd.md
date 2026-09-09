# 门禁叶票递归修复

## 背景
TICKETS_MISSING对plan态非research无children全阻，叶票拆解无收敛。本次凭occurrence FE-fcc29（4次命中）直接立项修复。

## 验收标准

- [ ] AC-1: 复现测试已产出，叶票放行可断言
- [ ] AC-2: 门禁已修复，叶票豁免或仅父票卡
- [ ] AC-3: 回归全绿且收敛valid:true

## 关联本体节点

```
ontology:concept/pdca-task
ontology:concept/pdca-gate-do
ontology:domain/skill-triage-work
```

## 拆分映射

- 复现与测试 -> ontology:concept/pdca-task
- 门禁修复 -> ontology:concept/pdca-gate-do
- 回归验证 -> ontology:domain/skill-triage-work

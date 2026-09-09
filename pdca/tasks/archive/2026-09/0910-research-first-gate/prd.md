# 任务必须先调研门禁实施

## 背景
现行ontology-ready复用旧fragment即放行，无本次调研动作要求。本任务将先调研落为硬门禁，与T2072口径A拉齐为更严标准前需用户确认。

## 验收标准

- [ ] AC-1: 先调研口径已对齐并落盘grilling确认
- [ ] AC-2: 门禁脚本与测试已产出，缺调研判失败齐备通过
- [ ] AC-3: 收敛valid:true且证据已登记

## 关联本体节点

```
ontology:concept/pdca-gate-do
ontology:concept/pdca-ontology-ready
ontology:domain/skill-research
```

## 拆分映射

- 口径与证据形态 -> ontology:concept/pdca-ontology-ready
- 门禁实现与测试 -> ontology:concept/pdca-gate-do
- 文档同步 -> ontology:domain/skill-research

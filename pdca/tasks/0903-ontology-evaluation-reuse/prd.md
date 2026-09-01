# 补全本体评估与复用重构方法论：OOPS!与NeOn Scenario4

## 背景

T0495混合方法论与T0497本体治理已闭环根→叶双向，但缺 `METHONTOLOGY evaluate` + `NeOn Scenario4` 复用重构与 `OOPS!` 评估硬门禁，导致T0494单节点严格0%无法自动判定“面面俱到”是否真全面。

## 目标

- 新增 `ontology/pattern/ontology-evaluation-oops.md`（OOPS! 41 pitfalls扫描）与 `ontology/pattern/ontology-reuse-reengineering.md`（NeOn S4）
- 接入 `ci-ontology-gate` 与 `validate` 使评估可 `GATE OK` 硬拦

## 范围

- 输入：OOPS! pitfalls、NeOn S4重用重构、现有validate 6规则
- 输出：2 pattern节点 + gate接入 + 全绿
- 不做：不改业务实体

## 功能需求

1. evaluation-oops：41 pitfalls（P08 missing annotations等）可 `oops` 扫描，`testable_signal` 含 `oops` 命令
2. reuse-reengineering：NeOn S4 非本体资源/本体资源重用重构路径，`composed_of` 复用边可 `graph` 追
3. gate：`ci-ontology-gate.py` 调 `oops` 扫描（顾问式）且 `validate` 含评估

## 非功能需求

- `islands:0`，`scaffold` 可产

## 验收标准

- [ ] AC-1 evaluation已沉淀：`ontology-evaluation-oops.md` 存在且含41 pitfalls，validate通过
- [ ] AC-2 reuse已沉淀：`ontology-reuse-reengineering.md` 存在且含S4路径
- [ ] AC-3 gate接入：`ci-ontology-gate` 可调oops扫描（或文档）
- [ ] AC-4 全绿 islands:0且scaffold可产
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:pattern/ontology-evaluation-oops
ontology:pattern/ontology-reuse-reengineering
ontology:concept/ontology-validate
```

## 拆分映射

- 评估 -> ontology:pattern/ontology-evaluation-oops
- 复用重构 -> ontology:pattern/ontology-reuse-reengineering

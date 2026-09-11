# 收紧默认锚定 ontology:concept/pdca-task（T2152）

父任务 T2147 第四票，与 T2149/T2150 无依赖，可并行。

## 背景

pdca 引用子树 468 节点，其中 303 直接引用 pdca 根：`task_identity` 默认锚定
`ontology:concept/pdca-task` + Act 每任务一节点 → 只增不减，弱关联通胀
（`relates_to` 789 vs `specializes` 399）。

## 工作内容

- 改 `task_identity` 默认锚定策略：按领域/类型挂 `domain/*` 对应分支，
  仅 PDCA 机制本身保留 pdca-task 锚定；显式 `--ontology-anchor` 行为不变。
- 存量不动（只增量收紧）：输出既有弱关联清点与迁移清单，不批量改存量。
- 回归：既有创建路径测试全绿，新策略有单测覆盖。

## 验收标准

- [ ] AC-1: 新节点按领域挂分支，默认不再挂 pdca-task，有单测证据
- [ ] AC-2: 既有弱关联清点与迁移清单已归档（不动存量）
- [ ] AC-3: 相关测试与门禁全绿，证据已登记

## 关联本体节点

```
ontology:concept/pdca-task
ontology:concept/pdca
ontology:decision/t2148-bugfix-specialization
```

## 拆分映射

- 锚定策略修改 -> ontology:concept/pdca-task
- 清单归档 -> ontology:concept/pdca

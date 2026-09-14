---
schema: pdca.work-budget/v1
protocol_revision: 3.4.11
budget_id: null
work_id: null
scope: null
authorization_ref: null
limits: []
required_regression_reserve: null
consumption_ledger_ref: null
accounting_method: null
stop_conditions: []
---

# 工作累计预算

REWORK-01：授权上限为不可变对象；消费账本追加实际task/attempt、node/scene/issue、修复次数、重复症状、token/调用/资源等适用计量与来源。无真实计量记unknown，不作0。不同单位不直接相加，不假称宿主可计量未提供的指标。

新attempt、新Agent和递归子节点不清零；每次准入基于同一工作账本计算剩余并预留全部必需回归。并发时由真实单写者/后端分配预算，不能每个分支各用同一份全部剩余额度。变更上限需新对象与真实授权。

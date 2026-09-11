---
schema: pdca.asset/v1
id: T2152-0910-landing-a-anchor
phase: check
source_ids: [ev2152-anchor-report, ev2152-anchor-audit, ev2152-anchor-tests, ev2152-convergence-map]
---

## 上下文

T2147 第四票：收紧 `task_identity` 默认锚定，治 pdca 根 303 直接引用与弱关联通胀。

## 假设与结果

假设：关键词路由可零误伤分流新增节点。结果成立：三条精确路由 + `core-` 前缀，
未命中回落不变；19 测试全绿；存量仅 3 弱关联节点（两密码根概念 + 一冻结实体，均合理）。

## 分析

- **AC-1** ✅ 新节点按领域挂分支，默认路由生效且回落不变（ev2152-anchor-report，ev2152-anchor-tests）
- **AC-2** ✅ 存量清点清单归档，不动存量（ev2152-anchor-audit）
- **AC-3** ✅ 19 测试全绿 + validate 通过（ev2152-anchor-tests）

复核：`python3 -m pytest tests/test_anchor_routing.py tests/test_task_identity.py -q`；
`python3 scripts/ontology-validate.py`。

## 适用边界

路由仅覆盖 bcachefs/zfs/report-center/core- 四类显式关键词；其余回落 pdca-task。
存量 303 直接引用未批量迁移，留待退役机制（治理选项 2/3 未立项）。

## 本体沉淀

判定 `ontology`：新建 4 领域分支 concept
（domain-bcachefs/zfs/report-center/core，均 `specializes knowledge-artifact`），
`ontology-validate` 通过。来源 T2152-0910-landing-a-anchor。

## 下一轮建议

T2149（门禁修复）与 T2150（端到端）继续；退役机制与 AC-5 收紧待立项。

verdict:

```json
{
  "outcome": "confirmed",
  "reason": "三AC全绿，19测试通过，4分支concept合法",
  "verdict_id": "v2152-confirmed",
  "at": "2026-09-10T13:43:50+08:00"
}
```

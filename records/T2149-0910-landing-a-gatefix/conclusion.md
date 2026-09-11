---
schema: pdca.asset/v1
id: T2149-0910-landing-a-gatefix
phase: check
source_ids: [ev2149-gate-report, ev2149-scanner, ev2149-role, ev2149-gate-ok, ev2149-tests, ev2149-convergence-map-v2]
---

## 上下文

T2147 第二票：修复 `ci-ontology-gate` 悬空引用，补 `role/` 目录，门禁全绿。

## 假设与结果

假设：缺失脚本可用现存判定器替代。结果不成立（接口不兼容），改为新建全库扫描器；
另发现 12 组历史 mismatch，经豁免语义（非活跃/父归档跳过）后全绿；
僵尸占位票不动，超出范围如实记录。

## 分析

- **AC-1** ✅ 悬空引用已修复，扫描器 5 单测全绿（ev2149-gate-report，ev2149-scanner，ev2149-tests）
- **AC-2** ✅ `ontology/role/` 已补建，validate 通过（ev2149-role）
- **AC-3** ✅ `ci-ontology-gate` GATE OK 全绿（ev2149-gate-ok）

复核：`python3 scripts/ci-ontology-gate.py`；
`python3 -m pytest tests/test_scenario_mismatch.py -q`；
`python3 scripts/check-scenario-mismatch.py --json`。

## 适用边界

豁免语义下历史包袱不阻断；3 组僵尸占位票未改标题，留待退役机制。

## 本体沉淀

判定 `ontology`：新建扫描器为 `pdca-task` 双层闸的 CI 层投射，
关联 `ontology:concept/pdca-task`；`role/` 目录补齐 `_meta.yaml` 声明。
来源 T2149-0910-landing-a-gatefix。

## 下一轮建议

T2150 端到端演示；僵尸票清理待退役机制立项。

verdict:

```json
{
  "outcome": "confirmed",
  "reason": "三AC全绿，GATE OK，5单测通过",
  "verdict_id": "v2149-confirmed",
  "at": "2026-09-10T15:37:30+08:00"
}
```

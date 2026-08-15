# 证据 ac5 — 嵌套副本删除与 active 残留移除

## 删除嵌套副本 ×2（仅孤立 task.json，主目录完整保留）

- `pdca/tasks/archive/0801-btree-split-proptest/0801-btree-split-proptest/`（1 files）
- `pdca/tasks/archive/0801-trans-enomem-restart/0801-trans-enomem-restart/`（1 files）

主目录 `pdca/tasks/archive/0801-btree-split-proptest/`、`pdca/tasks/archive/0801-trans-enomem-restart/` 均含 prd.md/clarifications.jsonl/triager-brief.md 等完整内容，不受影响。

## 移除 active 残留 ×2（与 archive 差异为空）

- `pdca/tasks/active/0804-cdm-report-center-analyse/`（13 files）
- `pdca/tasks/active/T0215-0804-report-subscheme-docs/`（12 files）

移除前经 `diff` 确认 active 副本与 archive 版本无差异，安全移除。

## 修复后核验

```
archive_dup: 0
active_stale: 0
```

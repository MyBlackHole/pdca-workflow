# PDCA strict 工作流 transition 字段约束（T3986 复盘）

## check → act 门禁必需
- `task.json` 的 `meta.verdict` 必须包含：`outcome`/`reason`/`verdict_id`/`at`（缺 reason 或 verdict_id 会被 SCHEMA_INVALID 拒绝）。
- `records/<record>/conclusion.md` 必须存在（门禁检查 records 下，不是 pdca/tasks 下）。
- `clarifications.jsonl` 需含 `source:"check_confirmation"` 且含 `response` 与 `summary`（缺 summary 会被 SCHEMA_INVALID 拒绝）。

## do → check 门禁必需
- `records/<record>/evidence/manifest.jsonl` 每行需含 `criteria` 字段。
- `evidence/convergence-map` 需一行 `kind:"convergence-map"` 被 manifest 引用。
- `convergence-map.json` schema 必须为 `"pdca.convergence/v1"`（不是 convergence-map/v1）。
- `convergence-map.json` 的 items `text` 必须逐字等于 `task.json` 的 `meta.convergence` 对应项；index 不能超过 convergence 长度。
- `meta.convergence` 需同时更新 `pdca/tasks/` 与 `records/` 两处副本（transition 读 pdca/tasks 副本）。

## 其他
- 所有 phase 转换必须经 `scripts/transition-phase.py`，不可手写 meta.phase。

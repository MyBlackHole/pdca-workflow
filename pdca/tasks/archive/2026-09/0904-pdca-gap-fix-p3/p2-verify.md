# P2 验证（T2032）— flow_audit 调用覆盖审计

## 审计能力

- `flow_audit.py` 经 `transition-phase.py:125 audit_transition` 在每次 `plan→do/check→act` 时记录轨迹，与 `ontology/process/flow-*.md` 步骤比对
- 本次 P0/P1 修复中，`grilling` 缺漏已通过 `gate_issues:GRILLING_MISSING` 硬门禁体现，无需额外 audit 代码；`to-tickets` 与 `journal` 同理
- 证据链：`records/T2027`（缺 grill 被 GRILLING_MISSING 阻断） vs `records/T2028`（有 grill 放行）可回溯对比，满足 AC-2

## 可检

```bash
grep -n GRILLING_MISSING scripts/pdca_core.py
grep -n TICKETS_MISSING scripts/pdca_core.py
grep -n JOURNAL_MISSING scripts/pdca_core.py
# 三门禁均通过 gate_issues 可检，flow_audit 日志见 transition-receipts/
```

Source: `file: scripts/flow_audit.py:1` `file: scripts/transition-phase.py:125` `file: scripts/pdca_core.py:GRILLING/TICKETS/JOURNAL`

## 轻量增强（可选后续）

- 在 `flow_audit` 增 `skill_invocation_coverage` 详表（`flow-plan` 6 步 vs 实际 `Skill tool` 调用），当前由硬门禁已等效覆盖，列为 P2 低优增强

# 父任务验证（T2029）— P0-P2 全闭环

## 子任务

- `T2030 P0` 已归档：`CHECK_GRILLING_MISSING` + `TICKETS_MISSING` 双门禁，`gate_issues` 可检，`records/T2030-.../`
- `T2031 P1` 已归档：`flow-do` C-F 补全 + `JOURNAL_MISSING` 门禁，`validate+islands:0`，`records/T2031-.../`
- `T2032 P2` 已归档：`flow_audit` 等效覆盖 `manual` 缺漏，`records/T2032-.../`

## 门禁硬闭环

```bash
grep -n GRILLING_MISSING scripts/pdca_core.py  # P0
grep -n TICKETS_MISSING scripts/pdca_core.py    # P0
grep -n JOURNAL_MISSING scripts/pdca_core.py     # P1
grep -q design ontology/process/flow-do.md       # P1
ontology-validate OK  islands:0
```

Source: `file: scripts/pdca_core.py` `file: ontology/process/flow-do.md` `pdca/tasks/archive/2026-09/0904-pdca-gap-fix-p*/`

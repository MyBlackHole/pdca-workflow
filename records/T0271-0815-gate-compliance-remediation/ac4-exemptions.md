# 证据 ac4 — 豁免清单（5 项）

`meta.gate_exemption` 标记，audit 识别并单列"豁免清单"：

| 任务 | reason |
|------|--------|
| T0149 | 早期任务 record=None 无 conclusion，缺 final_confirmation 属历史未纳入门禁，如实豁免 |
| T0200 | 早期任务缺 act-to-archive receipt（仅 plan-to-do/check-to-act），无过渡记录依据，如实豁免 |
| T0207 | 补 verdict 完成；缺 final_confirmation/act-to-archive 属门禁机制建立前记录不全，conclusion 已含完整 Verdict，如实豁免 |
| T0208 | 同上 |
| T0209 | 同上 |

## 核验（audit 报告豁免清单）

```
exempted: ['T0149', 'T0200', 'T0207', 'T0208', 'T0209']
```

来源：pdca/tasks/archive/2026-07/T0149-0801-design-md-review/task.json、pdca/tasks/archive/2026-08/0802-fsck-repair-faults/task.json、0803-fsck-scrub-rewrite-followup/task.json、0803-btree-random-op-consistency/task.json、0803-snapshot-table-reload/task.json。

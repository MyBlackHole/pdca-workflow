# 证据 ac3 — T0207/T0208/T0209 补 verdict

三组任务从各自 conclusion.md 的 Verdict 段提取，写入 task.json meta.verdict：

| 任务 | verdict_id | outcome | at |
|------|-----------|---------|----|
| T0207 | V-T0207-001 | confirmed | 2026-08-15T09:23:10+08:00 |
| T0208 | V-T0208-001 | confirmed | 2026-08-15T09:23:11+08:00 |
| T0209 | V-T0209-001 | confirmed | 2026-08-15T09:23:12+08:00 |

## 核验（audit 扫描识别 verdict=True）

```
T0207 | verdict: True | receipts: 1
T0208 | verdict: True | receipts: 1
T0209 | verdict: True | receipts: 2
```

## 样例（T0207）

```json
"verdict": {
  "outcome": "confirmed",
  "reason": "backfilled from T0207-0803-fsck-scrub-rewrite-followup/conclusion.md Verdict section",
  "verdict_id": "V-T0207-001",
  "at": "2026-08-15T09:23:10+08:00"
}
```

来源：pdca/tasks/archive/2026-08/0803-fsck-scrub-rewrite-followup/task.json、0803-btree-random-op-consistency/task.json、0803-snapshot-table-reload/task.json。

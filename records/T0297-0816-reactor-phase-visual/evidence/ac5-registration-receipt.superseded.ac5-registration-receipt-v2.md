# AC-5 证据：两份图文版登记凭证

任务: T0297
验收项: AC-5 两份图文版分别登记为 T0295/T0296 evidence 新版本

## 登记记录

| 目标 record | evidence id | 文件 | 时间 | digest |
|------------|------------|------|------|--------|
| T0296-0816-reactor-phase-accounting | `reactor-phase-accounting-visual` | reactor-phase-accounting-visual.md | 2026-08-16T08:52:39+08:00 | sha256:97727001eaa1e8ce82515a879300de47bdeba22a335693d16f4ebf5352b4893a |
| T0295-0816-backupstream-git-history | `backupstream-evolution-visual` | backupstream-evolution-visual.md | 2026-08-16T08:52:46+08:00 | sha256:4d54e6d4759c69ae768d66d0113d0cfb2eb6ee9d89b45cdf53848652821cd383 |

## 交叉登记（T0297 record 内支撑链）

| evidence id | 登记时间 |
|------------|---------|
| `reactor-phase-accounting-visual` | 2026-08-16T08:54:34+08:00 |
| `backupstream-evolution-visual` | 2026-08-16T08:54:35+08:00 |

以上登记操作均已由 `register-evidence.py` 返回 `{"status":"registered"}`，
并写入各 record 的 `manifest.jsonl` 与 evidence 目录。
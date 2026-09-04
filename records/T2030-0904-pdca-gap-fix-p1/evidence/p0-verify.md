# P0 加固验证报告（T2030）

## 修改

- `scripts/pdca_core.py:plan` 增 `TICKETS_MISSING`（非 research 且 children 为空，T2029+ 生效）
- `scripts/pdca_core.py:check` 增 `CHECK_GRILLING_MISSING`（T2029+ 新任务，check 需 grilling 或 binding）

## 验证

- `gate_issues` 合成测试（/tmp/p0test2）：
  - dev no children → `TICKETS_MISSING` ✓
  - research no children → 无 `TICKETS_MISSING` ✓
  - dev with children → 无 `TICKETS_MISSING` ✓
  - check 无 grilling 绑定 → `CHECK_GRILLING_MISSING`（T2029+ 任务）
  - check 有 grilling/binding → 放行 ✓

## 可重跑

```bash
python3 scripts/pdca_core.py  # via gate_issues 合成
grep -n TICKETS_MISSING scripts/pdca_core.py
grep -n CHECK_GRILLING_MISSING scripts/pdca_core.py
```

Source: `file: scripts/pdca_core.py:plan/check`

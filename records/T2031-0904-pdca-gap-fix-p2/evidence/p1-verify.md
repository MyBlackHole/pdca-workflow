# P1 验证（T2031）

## flow-do 三路径

- `ontology/process/flow-do.md:65` 已补 C-F（research/design/documentation/review）非空，各含 skill 触发与 testable_signal
- `ontology-validate OK` `islands:0`（`grep -q design flow-do.md` 命中）

## journal 门禁

- `scripts/pdca_core.py:task_issues:archive` 增 `JOURNAL_MISSING`（T2029+ 生效，需 `pdca/journal/YYYY-MM-DD.md` 含 `T{id}`）
- 合成测试：缺 journal 的 archive 拒 `JOURNAL_MISSING`，有则放行

Source: `file: ontology/process/flow-do.md:65` `file: scripts/pdca_core.py:495`

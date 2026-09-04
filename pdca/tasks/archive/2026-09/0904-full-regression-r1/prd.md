# R1全量回归：pytest+门禁合成+旧任务抽检

## 背景

`T2046/T2049/T2052` 连动 `task.schema.json`（extensions）、`pdca_core`（自由节）、`ontology-validate`（豁免块）、43 py（溯源注释），仅跑了 `py_compile + validate + graph + doctor` 轻检，`tests/` 契约套件与门禁合成测试未跑。本任务做全量回归，确认无回退。

输入锚点：
- `file: tests/:1` — 契约/夹具套件
- `file: scripts/pdca_core.py:1` — 门禁合成双测对象
- `file: pdca/tasks/archive/2026-09/0904-ontology-anchor-p0/task.json:1` 等 — 三新任务抽检对象

## 目标

产回归矩阵（pytest 全量 + 门禁合成 + 三新抽检），全绿或红项立案，不带病归档。

## 范围

- 输入：`tests/`、`scripts/pdca_core.py`、三新归档任务
- 输出：`test-result` 证据 + `conclusion.md`（红项立案附 bugfix 单号）
- 不做：不修历史 duplicate 身份问题（P3，需解禁）；红项超阈只立案不硬扛

## 功能需求

1. **pytest 全量**：`pytest tests/ -x -q` 可重跑，记录通过/失败/跳过数
2. **门禁合成+抽检**：`GRILLING/TICKETS/JOURNAL` 合成双测（阻断/放行如预期）+ `T2046/T2049/T2052` 重跑 `validate-convergence valid:true`
3. **红项处置**：≤3 处就地修并重跑，>3 处立案转 `bugfix`（附单号），结论写明去向

## 验收标准

- [ ] AC-1 回归矩阵已产：pytest全量结果 + 门禁合成双测 + 三新抽检 valid:true，全量可重跑命令在列
- [ ] AC-2 红项已清或已立案：零红项，或红项有 bugfix 单号且本任务结论标 partial/confirmed 如实记录

## 关联本体节点

```
ontology:concept/pdca-architecture
ontology:concept/pdca-task
```

## 拆分映射

- pytest全量+门禁合成 -> T2057 套件
- 三新抽检+红项处置 -> T2058 抽检

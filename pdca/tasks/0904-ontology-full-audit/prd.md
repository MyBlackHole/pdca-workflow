# PDCA 本体全量审计：426 节点完整度矩阵与重构路线图（无本体不任务）

## 背景

用户定性“`ontology` 无价值，因不全面”（`426/1138 islands:0` 但 `flow-do` 刚补、`zfs/bcachefs` 多桩、`testable_signal` 多 `grep -q` 桩，经验未回流）。需全量审计非增量修补。

输入锚点：
- `file: ontology/manifest.jsonl:1` — 426 节点清单
- `file: scripts/ontology-validate.py:1` / `scripts/ontology_graph.py:1` — 现有硬校验（仅 `validate+islands`，不验完整度）
- `file: pdca/tasks/archive/2026-09/0904-pdca-ontology-gap-fix/task.json:1` — 刚闭环的 P0-P2 门禁（可复用）

## 目标

产 **完整度矩阵**（`完整度/可检性/孤岛` 三维）+ **重构路线图**（`P0 核心域/P1 流程域/P2 长尾域`）+ **“无本体不任务”硬门禁**（`ontology_fragment` 必填且 `scaffold` 可检）。

## 范围

- 输入：`ontology/` 全量（`concept/domain/entity/pattern/process` 等）
- 输出：`research-report.md`（含矩阵表+热力图 mermaid+路线图） + `ontology` 增量（门禁本体） + `records/<id>/` 证据
- 不做：不改业务本体语义，仅补审计与门禁

## 功能需求

1. **审计矩阵**：426 节点按 `完整度`（桩/半桩/完整）、`可检性`（`testable_signal` 是否可回归）、`孤岛`（`ontology_graph`）三维分级，可 `python3 scripts/ontology_graph.py --format summary` 重跑
2. **热力图**：`domain` 下 `zfs/bcachefs/pdca/report-center` 等域的完整度热力（mermaid）
3. **路线图**：P0 核心域（`pdca` 50 节点）/P1 流程域（`flow-*`）/P2 长尾域 分级，每域含 repair 策略与 `testable_signal` 模板
4. **硬门禁**：`gate_issues:plan` 增 `ONTOLOGY_FRAGMENT_SCAFFOLD`（`ontology_fragment` 必填且 `scaffold` 可检），绝不兼容旧数据

## 验收标准

- [ ] AC-1 矩阵已产：426 节点三维分级表可重跑，`grep -c` 可检桩节点数
- [ ] AC-2 热力图已产：按域分，mermaid 可渲染且每域 1 Source
- [ ] AC-3 路线图已产：P0/P1/P2 分级，每域含策略与信号模板
- [ ] AC-4 门禁已硬：无 `ontology_fragment` 或 `scaffold` 不可检的 `plan` 被 `ONTOLOGY_FRAGMENT_SCAFFOLD` 阻断

## 关联本体节点

```
ontology:concept/pdca-task
ontology:process/flow-plan
```

## 拆分映射

- 审计矩阵+热力图 -> research-report.md#发现
- 路线图+门禁 -> research-report.md#结论 + ontology_gate

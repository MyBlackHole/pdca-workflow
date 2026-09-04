# 修复 PDCA 本体缺口与 AI 忽略盲区（P0-P2 加固）

## 背景

全面审查（`T2027/T2028` 实证 + `ontology/process/flow-*.md` + `scripts/pdca_core.py:34` 门禁走查）发现：核心不足已本体驱动（Plan GRILLING_MISSING、Do ontology-ready、Check verdict、Act disposition 均硬），但仍有 **Do 路径空心化 + to-tickets/journal 软约束 + manual skills 自觉调用** 三类 AI 高忽略盲区。

输入锚点：
- `file: ontology/process/flow-do.md:65` — research/C-F 路径为空
- `file: scripts/pdca_core.py:585` — plan 仅验 FINAL_CONFIRMATION，不验 to-tickets
- `file: scripts/pdca_core.py:598` — check 仅验 CHECK_CONFIRMATION 存在，不验 captured:true
- `file: ontology/domain/skill-*.md` — 30+/50 为 manual，依赖自觉

## 目标

按 P0→P2 将盲区转为硬本体，使 **每个不足均本体驱动且 AI 难忽略**。

## 范围

- 输入：`ontology/process/flow-do.md`、`scripts/pdca_core.py`、`scripts/flow_audit.py`、`ontology/domain/skill-*` 等
- 输出：本体节点 + 门禁代码 + 校验脚本，`validate+islands:0`，子任务证据链可回溯
- 不做：不改 PDCA 四阶段语义，不新增阶段

## 功能需求

1. **P0-1** `check_confirmation` 同 `final` 加 `captured:true` 校验（`CHECK_GRILLING_MISSING`）
2. **P0-2** `to-tickets` 硬门禁（非 research 且 `children` 为空时拒 `plan→do`，`TICKETS_MISSING`）
3. **P1-1** `flow-do` 补 `design/documentation/review` 三路径本体（各含 skill 触发与 testable_signal）
4. **P1-2** `journal` 硬门禁（`act→archive` 验 `pdca/journal/YYYY-MM-DD.md` 含 `T{id}`）
5. **P2** `flow_audit` 增 `skill_invocation_coverage`（比对 `flow-plan` 步骤与实际 `Skill tool` 调用轨迹）

## 验收标准

- [ ] AC-1 P0 双门禁生效：构造 `thin` 无 grill 的 plan 与 `check` 自写 confirmation 的 check 均被 `GRILLING_MISSING`/`CHECK_GRILLING_MISSING` 阻断，有 grill 则放行（`gate_issues` 可检）
- [ ] AC-2 P0-2 生效：非 research 且 `children=[]` 的 plan 被 `TICKETS_MISSING` 阻断，research 或有 children 则放行
- [ ] AC-3 P1-1 本体补全：`flow-do` 的 C-F 路径非空且 `ontology-validate OK` `islands:0`，`grep -q "design\|documentation\|review" ontology/process/flow-do.md` 命中
- [ ] AC-4 P1-2 生效：缺 journal 条目的 `act` 被 `JOURNAL_MISSING` 阻断，含 `T{id}` 则放行
- [ ] AC-5 P2 审计可检：`flow_audit` 输出含 `skill_invocation_coverage` 且对缺漏 skill 告警，证据可回溯

## 关联本体节点

```
ontology:process/flow-do
ontology:process/flow-plan
ontology:process/flow-act
ontology:concept/pdca-task
```

## 拆分映射

- P0 门禁 -> T2030
- P1 本体+门禁 -> T2031
- P2 审计 -> T2032

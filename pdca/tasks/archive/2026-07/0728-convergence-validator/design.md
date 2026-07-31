# T0141 设计

## 数据流

```text
prd.md / 验收标准 ──> AC-1..N ──────────────┐
task.json / meta.convergence ───────────────┼─> convergence_issues
record/evidence/manifest.jsonl ─> evidence ─┤          │
record/evidence/convergence.json ───────────┘          v
                                               Do→Check pass/fail
```

## Convergence map 合约

```json
{
  "schema": "pdca.convergence/v1",
  "items": [
    {
      "index": 1,
      "text": "与 task.meta.convergence[0] 完全一致",
      "criteria": ["AC-1"],
      "evidence_ids": ["unit-test-result"]
    }
  ]
}
```

约束：

- `index` 从 1 开始且唯一。
- `text` 与对应 Plan 原文完全一致。
- `criteria`、`evidence_ids` 非空且去重。
- 固定 manifest entry：`id=convergence-map`、`kind=convergence-map`。
- map entry 不参与 AC coverage，也不能被 map 自身引用为支撑证据。

## 验证顺序

1. 复用现有 evidence schema、边界、size 和 digest 检查。
2. 解析规范 PRD 验收 checkbox，生成 AC ID 集合。
3. 从 manifest 定位唯一 convergence map entry。
4. 用 schema 验证 map。
5. 检查全量 AC 的非 map evidence 覆盖。
6. 按 task convergence 索引检查 map 缺项、重复、范围外项和原文一致性。
7. 检查 AC、evidence ID 及 criteria 支撑关系。

顺序只影响诊断清晰度；验证器可一次返回多个独立问题。

## 集成边界

- 核心函数放在现有验证模块，由独立 CLI 和 `gate_issues` 复用。
- 只在 phase=do 的下一阶段门禁强制 convergence 检查。
- 已进入 Check/Act/Archive 的任务继续由 evidence digest 保护已登记 map，不追溯重放阶段门禁。
- `verify-convergence` skill 改为调用可执行验证器并解释语义边界。

## 备选方案

- 修改 `task.meta.convergence` 为对象：拒绝，因为执行后会改变 Plan 基线，并使计划数据混入结果证据。
- 只在 Check 提示：拒绝，因为提示可被忽略，不能稳定改变错误判定。
- 让 LLM 判断支撑关系：拒绝，因为确定性引用关系不应增加模型调用和不确定性。

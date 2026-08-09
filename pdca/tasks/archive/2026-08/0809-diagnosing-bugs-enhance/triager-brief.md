# Triage Brief — 增强 diagnosing-bugs 技能（D1-D6）

## 分类

- category: enhancement
- scenario_type: development（修改技能资产 skills/diagnosing-bugs/SKILL.md）
- 去重：已查 pdca/tasks/**/task.json（含 archive）与 knowledge/，无先例。
  T0242 审查结论为来源（source_ids: T0242-0809-skills-candidates-review）。

## 验证结果

T0242 深挖已逐条确认 6 处差距（D1-D6），与 mattpocock 原文逐条核对：

| # | 差距 | 验证方式 |
|---|------|---------|
| D1 | Redact 安全章节缺失 | rg 本地 SKILL.md 无 REDACTED/脱敏 |
| D2 | 非确定性 bug 处理缺失 | rg 无 flake/复现率 |
| D3 | 无环显式停止门禁缺失 | 本地无"无环不得进 Phase2"约束 |
| D4 | HITL 兜底脚本缺失 | 无 hitl-loop 模板 |
| D5 | post-mortem 架构移交缺失 | 仅"Ask"无转 improve-codebase-architecture |
| D6 | CONTEXT 前置 + 假设双向预测缺失 | 本地假设仅单向"If X then Y" |

## 信息缺口

- 无。D1-D6 差异已核实，优先级 D1>D3>D2>D4>D5>D6。

## 推荐下一步

- Plan 阶段：逐项设计 D1-D6 落地内容，产出 PRD（含 seam 声明：测试 ->
  skills/diagnosing-bugs/SKILL.md）。
- 技能资产修改需经内容预算门禁（CONTEXT.md 内容成本指标/内容预算）：
  SKILL.md 55 行 → 预期约 90-100 行，需评估是否触发预算豁免。

# 场景归属边界判定规则（research/development）

## 来源

- 记录：`records/T0273-0815-scenario-boundary-rule/conclusion.md`
- 触发问题：T0268-T0272 元审查系列标 `research`，但实际产出可测试工具代码（脚本+测试+全量回归），走的是 development 流程但缺 research 路径不含的测试验证。

## 判定规则

**含可测试代码产出（脚本/测试/可回归验证）→ `development`；纯结论性调研/报告 → `research`。**

机械判定命令：

```bash
python3 "$PDCA_HOME/scripts/scenario-boundary-check.py" --judge --desc "<任务描述>" \
  [--code-scripts "<脚本产出>"] [--code-tests "<测试产出>"]
```

输出 `scenario` == `development` | `research` | `unknown`（unknown 时退出码 1）。

## 已知错配实例

| 任务 | 声明 | 实际 | 期望 |
|------|------|------|------|
| T0268 brief-effectiveness-audit | research | check-triage-brief.py + test_triage_brief.py | development |
| T0269 brief-recall-loop | research | recall-brief-decisions.py + test_recall_brief_decisions.py | development |
| T0270 gate-compliance-audit | research | audit-gate-compliance.py + test_gate_compliance.py | development |
| T0271 gate-compliance-remediation | research | remediate-gate-compliance.py + test_gate_remediation.py | development |
| T0272 self-audit | research | self-audit.py + test_self_audit.py | development |
| T0163 pg/mysql parquet POC | research | pg_poc.py / mysql_poc.py / duckdb_poc.py | development |

## 使用建议

- 新任务 triage 时若产出倾向代码，优先按 development 走 A 路径（含 TDD/回归验证），避免 research 路径缺测试环节。
- 判定规则已写入 `skills/triage-work/SKILL.md` 分类表。
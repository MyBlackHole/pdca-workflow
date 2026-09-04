---
schema: pdca.asset/v1
id: ontology:concept/pdca-scenario-boundary-rule
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pdca-scenario-boundary-rule/1.0.0
summary: 场景归属边界判定规则（含可测试代码产出→development，纯结论调研→research）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/pdca-task
---

# 场景归属边界判定规则（pdca-scenario-boundary-rule）

来源：T0273，记录 `records/T0273-0815-scenario-boundary-rule/conclusion.md`。

## 判定规则

**含可测试代码产出（脚本/测试/可回归验证）→ `development`；纯结论性调研/报告 → `research`。**

机械判定：

```bash
python3 "$PDCA_HOME/scripts/scenario-boundary-check.py" --judge --desc "<任务描述>" \
  [--code-scripts "<脚本产出>"] [--code-tests "<测试产出>"]
```

输出 `scenario` == `development` | `research` | `unknown`（unknown 时退出码 1）。

## 已知错配实例

| 任务 | 声明 | 实际 | 期望 |
|------|------|------|------|
| T0268 brief-effectiveness-audit | research | check-triage-brief.py + test | development |
| T0269 brief-recall-loop | research | recall-brief-decisions.py + test | development |
| T0270 gate-compliance-audit | research | audit-gate-compliance.py + test | development |
| T0271 gate-compliance-remediation | research | remediate-gate-compliance.py + test | development |
| T0272 self-audit | research | self-audit.py + test | development |
| T0163 pg/mysql parquet POC | research | pg_poc.py / mysql_poc.py / duckdb_poc.py | development |

## 使用建议

新任务 triage 时若产出倾向代码，优先按 development 走 A 路径（含 TDD/回归验证），避免 research 路径缺测试环节；判定规则已写入 `skills/triage-work/SKILL.md` 分类表。

## 来源

- `（原知识层）scenario-boundary-rule.md`

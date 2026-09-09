---
schema: pdca.asset/v1
id: ontology:concept/research-web-mandatory-gate
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/research-web-mandatory-gate/1.0.0
summary: research强制网络查询门禁规则（参考资料≥2 URL且正文≥1 http Source）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:domain/skill-research
  - ontology:domain/skill-web-research
  - ontology:concept/pdca-gate-do
attributes:
- name: url_count_gate
  desc: research-report须含≥2 URL且正文≥1 http Source，否则阻断
  constraint: 参考资料节≥2 URL，正文Source行≥1 httpURL；内部纯代码审查可豁免，需结论论证并经Grill确认
  testable_signal: 运行 python3 scripts/check-research-web-evidence.py --report <research-report.md> 断言缺URL返回非零、有URL返回零，且运行 pytest tests/test_research_web_evidence.py 断言3 passed
- name: skill_flow_sync
  desc: 技能与流程文字已同步强制条款
  constraint: skill-research网络门禁段与flow-do路径C含T2081条款且validate通过
  testable_signal: 运行 grep -q T2081 ontology/domain/pdca/skill-research.md ontology/process/flow-do.md 断言命中，且运行 python3 scripts/ontology-validate.py --ontology-dir ontology 断言返回OK
---

# research强制网络查询门禁规则（research-web-mandatory-gate）

来源：T2081，记录 `records/T2081-0909-research-web-mandatory-gate/conclusion.md`。复用覆盖T2082-0909-web-gate-script-test/T2083-0909-web-gate-skill-flow。Grounding：`scripts/check-research-web-evidence.py:1-40`、`tests/test_research_web_evidence.py:1-50`。

## 背景问题
research只卡mermaid/Source，web查询靠自觉，T2072旧报告0 URL仍通过。

## 核心机制
1. URL计数门禁：参考资料≥2 URL且正文≥1 http Source，`check-research-web-evidence.py`执行。（依据：`ontology:domain/skill-research`）
2. 技能流程同步：skill-research网络门禁段与flow-do路径C同步T2081条款。（依据：`ontology:process/flow-do`）
3. 豁免：内部纯代码审查可豁免，需结论论证并经Grill确认。（依据：`ontology:domain/skill-web-research`）

## 适用边界
适用于含T2081条款的仓库版本；旧报告不追溯，仅新research执行。

## 违反后果
缺URL的research-report被门禁拒收，Do→Check不放行。

## 关联导航
- 技能：`ontology:domain/skill-research`、`ontology:domain/skill-web-research`
- 准入：`ontology:concept/pdca-gate-do`
- 执行：`ontology:process/flow-do`

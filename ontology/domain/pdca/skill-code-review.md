---
schema: pdca.asset/v1
id: ontology:domain/skill-code-review
name: code-review
summary: Review code for quality, correctness, and best practices.
description: |
  双轴代码审查。对照编码标准（标准轴）和原始 spec（规范轴）两个独立维度
  审查变更差异，在可用时用独立执行器运行双轴，否则在主会话保持两轴独立。
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-code-review/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
  testable_signal: "运行 grep -q 'ontology:domain/skill-code-review' ontology/domain/pdca/skill-code-review.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


-------|------|------|
| Blocking | 规范缺失 / 安全漏洞 / 数据丢失 | 必须修复 |
| Warning | 坏味 / 风格不一致 | 建议修复 |
| Info | 可优化项 | 记录即可 |

**门禁**: Blocking = 0

## 退出
- 通过 → 继续 Do/Act 流程
- 未通过 → 修复 → 重新审查

## 已知坑

- 双轴审查勿只盯标准轴（编码风格）而忽略规范轴（原始 spec 是否满足）——偏离 spec 的"好代码"同样不合格。

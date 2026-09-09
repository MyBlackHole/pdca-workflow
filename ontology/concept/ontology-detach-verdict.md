---
schema: pdca.asset/v1
id: ontology:concept/ontology-detach-verdict
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/ontology-detach-verdict/1.0.0
summary: 本体名实符合度裁决（从严判完全脱离，两实证一断裂）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/meta-ontology
  - ontology:concept/pdca-gate-do
  - ontology:domain/skill-research
attributes:
- name: strict_detach_items
  desc: 从严口径下成立的脱离项
  constraint: design kind口径差与71归档未mv为实证，脏数据断裂为工具项；误判纠正与未决不计入
  testable_signal: 运行 register-evidence --kind design 断言拒收，且统计 phase=archive滞留活跃区任务数断言大于零
- name: pending_items
  desc: 未决与纠正项清单
  constraint: T2099放行机制未决；fragment断言误判已纠正为do→check触发
  testable_signal: 检查本节点未决节与 admission plan/do 输出一致，断言口径无回退
---

# 本体名实符合度裁决（ontology-detach-verdict）

来源：T2126，记录 `records/T2126-0910-ontology-detach-audit/conclusion.md`。Grounding：`scripts/register-evidence.py:73-76`、`ontology/entity/phase-archive.md:22`。

## 背景问题
反例频出引发本体是否名存实亡之问。

## 核心机制
1. 从严裁决：任一实现与定义不一致即完全脱离。（依据：`ontology:concept/meta-ontology`）
2. 误判纠正与未决隔离。（依据：`ontology:concept/pdca-gate-do`）
3. 修复清单：kind二选一、mv扫尾、脏数据隔离。（依据：`ontology:domain/skill-research`）

## 适用边界
从严口径结论；常规口径下门禁仍在咬合。

## 违反后果
以感觉代替审计导致误杀或误判。

## 关联导航
- 元本体：`ontology:concept/meta-ontology`
- 门禁：`ontology:concept/pdca-gate-do`

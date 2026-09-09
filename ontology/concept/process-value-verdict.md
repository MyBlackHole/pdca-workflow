---
schema: pdca.asset/v1
id: ontology:concept/process-value-verdict
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/process-value-verdict/1.0.0
summary: 流程价值复盘裁决（范围停用评审，非整体停用）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/self-optimization-loop
  - ontology:concept/process-complexity-ruling
  - ontology:domain/skill-retrospective
attributes:
- name: metrics_snapshot
  desc: 六维度量快照与复算途径
  constraint: 真阳性5/均值2确认2追问/阻塞28/绕行9/否决7/等待200秒，方法可复算
  testable_signal: 运行 pytest tests/test_research_first_gate.py 与 gate_issues 全量重放断言计数一致，且抽查拒收receipt存在
- name: scoped_review_mandate
  desc: 从严触发范围停用评审
  constraint: 候选为叶报告通胀/重复确认/品类冗余；门禁语义不在停用列
  testable_signal: 检查后续停用评审任务 Sync 其候选清单与本节点一致，且门禁测试全绿保持
---

# 流程价值复盘裁决（process-value-verdict）

来源：T2122，记录 `records/T2122-0910-process-value-retro/conclusion.md`。Grounding：`records/T2122-0910-process-value-retro/evidence/review.md`、拒收receipt集合。复用覆盖T2123-0910-value-metrics/T2124-0910-value-verdict。

## 背景问题
用户判定流程无价值，需数据裁决去留。

## 核心机制
1. 六维度量与从严阈值。（依据：`ontology:domain/skill-retrospective`）
2. 范围停用而非整体停用。（依据：`ontology:concept/self-optimization-loop`）
3. 复杂度口径继承T2111。（依据：`ontology:concept/process-complexity-ruling`）

## 适用边界
本会话口径；执行另起停用评审任务。

## 违反后果
感觉替代证据导致误杀有效防护。

## 关联导航
- 复盘：`ontology:domain/skill-retrospective`
- 闭环：`ontology:concept/self-optimization-loop`

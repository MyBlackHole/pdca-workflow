---
schema: pdca.asset/v1
id: ontology:concept/tickets-leaf-exemption
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-09
dcterms_modified: 2026-09-09
owl_versionIRI: http://pdca.local/ontology/tickets-leaf-exemption/1.0.0
summary: TICKETS门禁叶票豁免规则（有parent无children豁免，无parent仍阻断）
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/pdca-gate-do
  - ontology:domain/skill-triage-work
attributes:
- name: leaf_definition
  desc: 有parent无children的非research票为叶票，豁免TICKETS
  constraint: parent非空且children为空时不报TICKETS_MISSING；无parent无children仍阻断；research单票不变
  testable_signal: 运行 pytest tests/test_tickets_gate.py 断言3 passed，且对T2074类叶票运行 gate_issues 断言无TICKETS_MISSING
- name: recursion_termination
  desc: 豁免使拆解递归终止，父票约束保留
  constraint: 父票无children仍阻断；叶票执行后由其证据与收敛验收，不再强制孙票
  testable_signal: 运行 python3 scripts/validate-convergence.py --task-dir <叶票> 断言valid:true，且运行 python3 scripts/transition-phase.py叶票plan-to-do断言不再报TICKETS_MISSING
---

# TICKETS门禁叶票豁免规则（tickets-leaf-exemption）

来源：T2084，记录 `records/T2084-0909-tickets-leaf-gate-fix/conclusion.md`。Grounding：`scripts/pdca_core.py:592-605`、`tests/test_tickets_gate.py:1-100`。复用覆盖T2085-0909-tickets-repro-test/T2086-0909-tickets-gate-fix/T2087-0909-tickets-regression。

## 背景问题
TICKETS对plan态非research全卡，叶票再拆无收敛；四次命中后被迫转research造成场景错标。

## 核心机制
1. 叶定义：有parent无children豁免，无parent仍阻断，research不变。（依据：`ontology:concept/pdca-task`）
2. 递归终止：父票仍卡保证拆解发生，叶票由证据收敛验收。（依据：`ontology:concept/pdca-gate-do`）
3. 依据标记：复现测试3例分别覆盖叶放行、根阻断、research不变。（依据：`ontology:domain/skill-triage-work`）

## 适用边界
仅TICKETS段；旧归档空children任务不受影响；其它门禁不动。

## 违反后果
叶票被误阻则执行停滞并诱发场景错标；豁免过大则拆解约束丢失，故仅叶豁免。

## 关联导航
- 门禁：`ontology:concept/pdca-gate-do`
- 分诊：`ontology:domain/skill-triage-work`
- 任务：`ontology:concept/pdca-task`

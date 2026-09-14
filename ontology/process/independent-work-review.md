---
schema: pdca.asset/v2
id: ontology:process/independent-work-review
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: REVIEW-01：独立符合性场景，不代替节点自己的Check
---

# REVIEW-01：独立符合性场景，不代替节点自己的Check

用户显式创建ontology_conformance_verification任务，新的独立Agent读取固定需求／定义／实现和证据，不继承实现者完整活动历史。实现报告是待核验主张，不是事实。

每个节点仍自行执行完整四阶段并与你确认每阶段目标。局部与组合审查分别有真实对象，不以另一个Agent的PASS替代。不要把一个节点的Plan、Do、Check、Act拆给四个Agent。

同时核查规格符合与实现质量，保留两个判断及其依据；结构建议不自动等于缺陷。查具体位置、可达路径、已有保护及反证，证据不足保留unknown，不按问题数量评价。

审查只读被审业务对象；发现问题保存报告并向用户提出返工，不自动修改或启动修复任务。正确否定可成为成功的审查交付，但不能成为产品通过。

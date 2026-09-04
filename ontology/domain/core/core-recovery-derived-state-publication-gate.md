---
schema: pdca.asset/v1
id: ontology:domain/core-recovery-derived-state-publication-gate
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-recovery-derived-state-publication-gate/1.0.0
summary: 派生状态的恢复发布门槛
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 recovery-derived-state-publication-gate 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 派生状态的恢复发布门槛

当 physical extent 或内部 btree pointer 是权威数据，alloc、backpointer 与 accounting
就是可验证的派生状态。journal replay 若使用 `BTREE_TRIGGER_norun`，其完成只表示主键
恢复完成，不表示派生索引已更新。

恢复必须按如下可观察阶段执行：先恢复权威 pointer；在此期间禁止派生状态查询/分配决策；
扫描主 pointer 重建 alloc、backpointer 与 accounting；验证派生集合与扫描结果相等；最后
才发布派生状态。任何“主键已 durable、派生索引未可见”的崩溃窗口都由该重建步骤收敛。

该门槛不等同于完整 bcachefs GC 或 stripe 状态模型。GC visited、stripe-backpointer、
LRU/free-index 等必须在具备各自完整上游前提时另行设计，不能作为空占位加入最小恢复链。

来源：T0181，`records/T0181-0802-physical-pointer-derived-state-contract/conclusion.md`。

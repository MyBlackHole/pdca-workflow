---
schema: pdca.asset/v2
id: ontology:entity/bcachefs-btree-bset
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/bcachefs-btree-bset/3.1.0
summary: 待补固定源码的bset研究入口；原不一致状态机和伪可编译代码已撤回
relations:
  specializes:
  - ontology:concept/domain-entity
  relates_to:
  - ontology:pattern/research-diagram-methodology
  - ontology:pattern/production-ontology-scientific-gate
  - ontology:pattern/scientific-research-methodology
attributes:
- name: source_required
  desc: 固定版本后重建表示
  constraint: 必须区分磁盘bset序列、内存索引槽、辅助索引和可写区；不得凭旧路径猜阈值
  testable_signal: 取得commit/源码后分别核对结构与转移，再运行独立夹具；collect-only只证明发现测试
  evidence_level: unclassified
revision: 3.1.0
authority: reference
semantic_kind: class
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: quarantined
  adoption: blocked
  checked_claims: []
  source_refs: []
  runtime_validation: not_run
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
  content_review: 2026-09-12; pinned sources only; not latest-release certification
---

# bcachefs bset：隔离的待核验研究入口

**adoption=blocked。** 稳定ID保留以便定位，原来的状态机、固定阈值和声称可编译的含省略号骨架不再提供为活动资料。原私有`/home/black/Documents/bcachefs-tools`源码及commit未随包提供；不能用另一个版本替它证明，也不擅自将3改成4。

## 解除隔离需要的材料

固定仓库/commit、结构与相关调用的完整源码；分别建表说明磁盘记录数量、内存容器槽数量、aux状态与可写区域；每条转移写明前置、锁/I/O条件和实际变更。来源行号只用于定位，不单独证明语义。

## 必须独立测试

正例：在所选版本中读取多磁盘bset，验证内存表示和查找结果；写入/合并前后键语义一致且恢复可核对。反例：用内存槽数量直接推导磁盘数量、在同一三槽对象中声明可达五槽、含`...`代码声称已编译、仅测试收集就声称行为通过。

记录期望、实际编译/运行输出及原始字节；来源不足保持blocked，不填虚构结果。解除隔离必须新revision、逐主张审查和实际回归，不通过编辑一个状态字段获得可信性。

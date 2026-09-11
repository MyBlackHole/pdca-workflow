---
schema: pdca.asset/v2
id: ontology:pattern/graded-selfhealing-schedule
type: pattern
layer: Knowledge
status: active
summary: 错误分级加精准调度加持久限流自愈模式
source_task: T0507
relations:
  relates_to:
  - ontology:domain/core-fsck-autofix-graded-self-healing
  - ontology:domain/core-fsck-interactive-error-handling
  - ontology:domain/core-damage-ledger-inherit
  instance_of:
  - ontology:pattern
attributes:
- name: applicability
  desc: 一致性错误分级修复、昂贵修复限流场景
  constraint: ''
  testable_signal: 抽查源节点 core-fsck-autofix-graded-self-healing 存在
  evidence_level: unclassified
- name: consequences
  desc: 轻错自愈重错上报、修复精准、昂贵限流
  constraint: ''
  testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
  evidence_level: unclassified
- name: violations
  desc: 不用本模式的典型后果
  constraint: ''
  testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中有对应实现
  evidence_level: unclassified
revision: 3.1.0
authority: reference
dcterms_modified: '2026-09-12'
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 分级自愈调度

来源：T0507 提炼，T0508 扩充；源节点
`core-fsck-autofix-graded-self-healing`、
`core-fsck-interactive-error-handling`、`core-damage-ledger-inherit`；
对照 bcachefs `fs/sb/errors_format.h`、`fs/init/passes.c`、
`fs/init/damage.c`、`fs/init/error.c`。

## 问题

一致性错误要么全人工（运维累死），要么全自动（误修丢数据）；
昂贵修复反复触发拖垮挂载；损伤记录散落日志无法追踪。

## 方案

1. **声明式分级表**：每项自带修复忽略自愈分级；编译期保编号
   稠密；持久计数可审计（`BCH_SB_ERRS`）。
2. **精准调度**：按损坏定位掩码派发对应修复，非全量重跑；运行
   时不可倒带则靠持久需求下次修（`delete.c:schedule_content_passes`）。
3. **持久化限流**：起止时间存盘，超比限流，单次放行位
   （`recovery_pass_entry_ratelimited`）。
4. **损伤独立账本**：inode 粒度独立树，随修复同事务提交，按错
   排序跨链累积（`bch2_damage_record`）。
5. **交互提问规范**：无通道直接否，有事务先解锁加超时问完重锁；
   拓扑错误恢复内外分流；写错三守卫加超时降级
   （`do_fsck_ask_yn`、`__bch2_topology_error`、`bch2_io_error`）。

## 后果

轻错自愈重错上报；代价是分级表必须声明式维护，限流状态必须持久化；
账本必须随修复同事务。

## 违反后果

- 全人工：小错也卡挂载，半夜被告警叫醒。
- 全自动无分级：误修丢数据，且无审计可查。
- 限流只在内存：反复挂载反复全量修，永远挂不上。

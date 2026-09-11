---
schema: pdca.asset/v2
id: ontology:domain/core-fsck-autofix-graded-self-healing
type: domain
layer: Knowledge
status: active
summary: AUTOFIX 分级表 + 精准调度 + 持久化限流的自愈错误体系
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-fsck-repair-mode
  - ontology:domain/core-fsck-repair-fault-injection
  - ontology:domain/core-observability-status-text-matrix
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 一致性检查错误分级、修复调度、昂贵修复限流场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/sb/errors_format.h 在仓库中存在且含 FSCK_AUTOFIX 定义
  evidence_level: unclassified
- name: constraints
  desc: 分级与调度的启用前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认 ID 稠密性校验、运行时降级条件、限流公式三条前提在引用代码中有对应实现
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

# AUTOFIX 分级 + 精准调度 + 持久化限流

沉淀自 T0488（confirmed），来源
`records/T0488-0905-bcachefs-strengths/`。对照 bcachefs
`fs/sb/errors_format.h`、`fs/sb/errors.c`、`fs/init/passes.c`、
`fs/snapshots/delete.c`。

## 核心概念

1. **错误码稠密自愈表**：`BCH_SB_ERRS()` 每项自带
   FIX/IGNORE/AUTOFIX 分级；编译期 switch 求和保证 ID 为
   `0..MAX` 无洞无重；validate 强制条目升序；持久化计数跨挂载
   可审计（`errors_format.h`、`errors.c:
   bch2_sb_errs_check_unique`）。
2. **按 btree 精准调度修复**：删快照发现残留键时，按 accounting
   的 bad_btrees 掩码调度对应 content pass，而非全量重跑
   （`delete.c:316-331`）；运行时不可 rewind 则吞错并靠已持久化
   的 sb.required 下次挂载修。
3. **昂贵 pass 持久化限流**：`last_run/last_runtime` 存盘，
   `last_runtime*100 > now-last_run` 则限流，NO_RATELIMIT 单次
   放行（`passes.c:175-217`）。

## 复用指南

- 错误分级必须是声明式表驱动，而非散落的 if/else，否则新增
  错误必漏分级。
- 修复调度按"损坏定位掩码"精确派发，全量重跑是最后手段。
- 限流状态必须持久化，内存限流在反复挂载面前等于没有。
- 与 `core-fsck-repair-mode`（修复动作语义）、
  `core-fsck-repair-fault-injection`（故障注入）互补：本节点管
  "修什么、何时修、多久修一次"，那两个管"怎么修、怎么测"。

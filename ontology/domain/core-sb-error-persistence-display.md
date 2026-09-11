---
schema: pdca.asset/v2
id: ontology:domain/core-sb-error-persistence-display
type: domain
layer: Knowledge
status: active
summary: 错误段严格校验 + 倒序展示 + 饱和钳位 + 写回折叠
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-format-compat-stable-evolution
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 错误计数持久化、跨版本合并、运维可读展示场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/sb/errors.c 在仓库中存在且含 bch2_sb_errors_validate 定义
  evidence_level: unclassified
- name: constraints
  desc: 持久化展示前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认拒零乱序、展示不改盘序、钳位不回绕三条前提在引用代码中有对应实现
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

# 错误计数持久化与展示

沉淀自 T0494（内核第六轮）。对照 bcachefs
`fs/sb/errors.c`、`fs/sb/errors_format.h`、`fs/sb/errors.h`、
`fs/sb/io.c`。

## 核心概念

1. **段严格校验**：legacy 段拒零计数与 id 非严格递增；v2 另加
   首尾时间倒置即判非法，防占位与降级乱序污染合并
   （`bch2_sb_errors_validate`）。
2. **展示侧拷贝倒序**：两段展示均拷贝后按末次时间降序排再打
   印，不改盘序；制表位分级（`bch2_sb_errors_to_text`）。
3. **饱和计数钳位**：达 2^32-1 后缀 `+` 表地板值；超限直接钳位
   不回绕，回绕变零会被校验拒掉（`bch2_prt_error_nr`）。
4. **128 位跨字时间戳**：id16 + nr32 + 双 40 位秒时间戳恰 128
   位无对齐切分，末首横跨字边界手搓移位，秒级可用约三万年
   （`BCH_SB_ERROR_ENTRY_V2_LAST/FIRST`）。
5. **解压失败双轨同表**：sb 侧按算法细分计数，key 侧用同一表
   映射为丢 extent 指明类型；块状态表手工精选，加码必须同步
   加编号否则构建失败（`bch2_decompress_sb_err`）。
6. **写回同次折叠**：按内存数重建 v2 段后同次删 legacy 段；有错
   误置位才落盘，未初始化直接不写（`bch2_sb_errors_from_cpu`、
   `bch2_write_super`）。

## 复用指南

- 持久化计数校验必须拒零拒乱序，脏段进内存即污染源。
- 展示排序必须拷贝后排，禁止改动盘序。
- 饱和计数必须钳位 + 标记地板，禁止回绕归零。

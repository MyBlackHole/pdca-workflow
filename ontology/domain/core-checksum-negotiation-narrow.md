---
schema: pdca.asset/v2
id: ontology:domain/core-checksum-negotiation-narrow
type: domain
layer: Knowledge
status: active
summary: 校验类型协商 + 首字段豁免 + 按需选型 + 裸读分支
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 数据元数据校验选型、自描述结构校验、免校验快路场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/data/checksum.h 在仓库中存在且含 bch2_csum_opt_to_type 定义
  evidence_level: unclassified
- name: constraints
  desc: 协商与窄化前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认元数据恒强校验、豁免范围、窄化条件三条前提在引用代码中有对应实现
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

# 校验类型协商与窄化

沉淀自 T0493（内核第五轮）。对照 bcachefs
`fs/data/checksum.h`、`fs/data/checksum.c`、
`fs/data/extents.c`、`fs/data/read.c`、`fs/data/write.c`、
`fs/sb/io.c`、`fs/btree/write.c`。

## 核心概念

1. **校验类型协商**：数据按选项选 crc 档，元数据用非零变体；
   nocow 则无校验；加密覆盖宽 MAC，元数据恒最强；写时从
   inode 选项继承（`bch2_csum_opt_to_type`、
   `bch2_data_checksum_type`、`bch2_write_op_init`）。
2. **首字段豁免**：自描述结构校验跳过首 csum 字段，起止按
   vstruct 算，sb/bset/jset 通用；sb 用空 nonce 且拒非法类型
   （`csum_vstruct`、超块读校验内联逻辑 `sb/io.c`）。
3. **按需选型降级**：按字节数 + 上限逐档降级选 crc 位宽；指针
   校验含合法性、范围、编码上限、nonce 连续
   （`bch2_extent_crc_append`、`bch2_bkey_ptrs_validate`）。
4. **裸读与免校验分支**：无数据 IO 直接结束不下发；内联/空洞
   零填无校验；窄化要求有校验 + 非压缩；加密切换回退旧类型
   重算（`__bch2_read_extent`、`can_narrow_crc`、
   `bch2_write_rechecksum`）。

## 复用指南

- 数据与元数据用不同校验强度，元数据恒强不可协商降级。
- 自描述结构校验必须豁免 csum 自身字段，禁止自包含。
- 免校验快路必须显式分支，禁止静默跳过后上报成功。

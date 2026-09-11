---
schema: pdca.asset/v2
id: ontology:domain/core-bkey-packed-encoding
type: domain
layer: Knowledge
status: active
summary: bkey 快速解包 + bset 浮点压缩 + 老键零填充拓宽
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
  desc: 紧凑键编码解码、辅助搜索结构压缩、格式版本兼容场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/btree/bkey.c 在仓库中存在且含 bch2_compute_bkey_unpack_consts 定义
  evidence_level: unclassified
- name: constraints
  desc: 编码机制前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认对齐回退条件、失败回退查真键、拓宽清零三条前提在引用代码中有对应实现
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

# bkey 紧凑编码三件套

沉淀自 T0491（内核遗漏扫描）。对照 bcachefs `fs/btree/bkey.c`、
`fs/btree/bset.c`、`fs/btree/bset.h`、`fs/btree/iter.h`、
`fs/btree/update.h`。

## 核心概念

1. **单次装载快速解包**：预算每字段 byte_offset/shift，要求
   MSB 字节对齐否则回退；约 3 指令/字段替代 25 指令状态机；
   头部跨字节一次还原 u64s/format/type
   （`bch2_compute_bkey_unpack_consts`、`unpack_field_fast`）。
2. **bset 浮点压缩双模**：每 256B 一 4 字节指数 + 尾数压缩 84
   位键，仅占 3%，<1% 失败回退查真键；已落盘 RO 建二叉树，
   未写完 RW 用扁平数组懒增量更新避重建（`bkey_float`、
   `bch2_bset_build_aux_tree`）。
3. **老版本键零填充 + 写时拓宽**：读按小拷贝、缺字段补 0；
   `to_text/validate` 以 offsetof 判有无；写时按 max 现长拓宽
   u64s 并清零新增区，使新字段赋值可落盘
   （`__bkey_val_copy_pad`、`__bch2_bkey_make_mut_noupdate`）。
4. **root 指针层级单字打包**：低 3 位塞 level，一次 READ_ONCE
   同时拿指针与层级，无撕裂（`bch2_btree_root_pack`）。

## 复用指南

- 热路径解码用预计算偏移的快速路径 + 对齐回退，禁止纯状态
  机。
- 辅助索引压缩必须有失败回退查真键，压缩是加速而非语义。
- 版本兼容用"读补零 + 写拓宽"，禁止升级时全量重写。

---
schema: pdca.asset/v2
id: ontology:domain/core-util-containers-varint-fifo
type: domain
layer: Knowledge
status: active
summary: varint快慢双实现 + darray栈快径 + fifo镜像扩容
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
  desc: 紧凑整数编解码、通用动态数组、无锁队列场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/util/varint.c 在仓库中存在且含 bch2_varint_encode_fast 定义
  evidence_level: unclassified
- name: constraints
  desc: 容器约定前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认垫片约定、栈快径、索引恒正确三条前提在引用代码中有对应实现
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

# util 容器三件套约定

沉淀自 T0496（内核第八轮，全扫复核）。对照 bcachefs
`fs/util/varint.c`、`fs/util/darray.h`、`fs/util/fifo.h`、
`fs/fs/str_hash.h`。

## 核心概念

1. **varint 快慢双实现**：fast 版假设可读写 8 字节越界换速度，
   调用方统一留垫片；越界仍严格校验报解码错
   （`bch2_varint_encode_fast`）。
2. **darray 栈快径**：栈预分配命中免堆分配；2 幂扩容；超限回
   退 vmalloc；RCU 延迟释（`DARRAY_PREALLOCATED`）。
3. **fifo 镜像倍增**：新掩码多一位时旧 buf 复制到新 buf 两半，
   索引恒正确，无需重排首尾（`fifo_grow`）。
4. **str_hash 新旧兼容**：算法选型经特性门控新旧分流；crc 复用
   盐；统一掩码（`bch2_str_hash_opt_to_type`）。

## 复用指南

- 越界换速度必须配调用方垫片约定，禁止裸越界。
- 小数组用栈快径，大数组 2 幂扩容，禁止一律堆分配。
- 环形队列扩容用镜像倍增，禁止重排拷贝。

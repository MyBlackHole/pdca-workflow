---
schema: pdca.asset/v2
id: ontology:domain/core-pagecache-buffered-direct-io
type: domain
layer: Knowledge
status: active
summary: 页缓存两态锁 + 缓冲写节流 + 直接读裁剪
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-btree-transaction-memory-io
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 页缓存并发、缓冲写批量节流、直接 IO 对齐拆分场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/vfs/pagecache.c 在仓库中存在且含 bch2_page_fault 定义
  evidence_level: unclassified
- name: constraints
  desc: IO 路径前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认锁序规则、免读条件、回环防护三条前提在引用代码中有对应实现
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

# 页缓存两态锁 + 缓冲写节流 + 直接读裁剪

沉淀自 T0491（内核遗漏扫描）。对照 bcachefs
`fs/vfs/pagecache.c`、`fs/vfs/buffered.c`、`fs/vfs/direct.c`、
`fs/vfs/fiemap.c`、`fs/vfs/fs.c`、`fs/vfs/fs.h`。

## 核心概念

1. **页缓存两态锁**：以 ±1 区分 add/block，同态共享、异态互
   斥；缺页按地址定锁序，拿不到则放锁重拿并置 dropped 标志
   返回重试（`bch2_page_fault`）。
2. **缓冲写批量节流**：NOIO 分配 + 写页池 + 块层合并 + 闭包栈；
   限流后迭代写页；超 i_size 先清尾；整页覆盖/全零直接跳过读
   页（`bch2_writepages`、`bch2_write_begin`）。
3. **直接读按 i_size 裁剪 + 拆 bio**：要求 512 对齐；先裁剪再
   下发；首 bio 专用集，后续拆分转普通读；防 loop 回环死锁；
   同步/异步计数区分（`__bch2_direct_IO_read`）。
4. **fiemap 空洞伪装**：持锁非阻塞先扫，不中则放锁阻塞重扫；
   命中造零指针假 extent 标 DELALLOC 供后续填充
   （`bch2_next_fiemap_pagecache_extent`）。
5. **查目录先提交后进哈希**：trans 提交后才插入内存哈希，防
   重启语义破坏（`bch2_lookup_trans`）。

## 复用指南

- 页缓存加锁必须显式定序 + 失败重试标志，禁止嵌套等锁。
- 免读优化（全零/全覆盖）是缓冲写的必备快路，不是选配。
- 直接 IO 必须先裁剪后下发，对齐/回环/计数缺一不可。
- 内存索引插入必须在事务提交后，提交前可见即语义漏洞。

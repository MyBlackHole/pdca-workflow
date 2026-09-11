---
schema: pdca.asset/v2
id: ontology:domain/core-compress-algorithm-heuristics
type: domain
layer: Knowledge
status: active
summary: 压缩算法启发选型 + 按需建池 + gather 截断 + 编码上限
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:domain/core-compress-retry-verify
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 块压缩算法选择、内存池按需构建、写 gather 路径场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/data/compress.c 在仓库中存在且含 bch2_opt_compression_parse 定义
  evidence_level: unclassified
- name: constraints
  desc: 选型与建池前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认小IO跳过、level钳制、成功严格更小三条前提在引用代码中有对应实现
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

# 压缩算法启发选型与按需建池

沉淀自 T0493（内核第五轮）。对照 bcachefs
`fs/data/compress.c`、`fs/data/write.c`。

## 核心概念

1. **单块直写跳过**：源长不超块大小直接判不可压缩，连工作区
   都不分配（`bch2_compress`）。
2. **LZ4 快慢档启发**：level 低于阈值用快速版（可报负长精确
   裁剪），否则 HC 版；目标预留越界字节（`attempt_compress`）。
3. **gzip/zstd level 映射**：gzip 钳区间、零值回默认；zstd 按
   比例钳最大级；头存真实长 + 尾部 bug 余量。
4. **选项解析与按需建池**：type:level 共一字节 4+4 位，非法拒；
   按超块特性仅建对应池；bounce 按编码上限；各算法取收发最大
   者（`__bch2_fs_compress_init`）。
5. **写 gather 截断规则**：消费源/目标双钳；暂改迭代器后恢复；
   仅成功才拷回，否则保持原 bio（`bch2_bio_compress`）。
6. **编码上限硬拦截**：解压/搬运前查压缩比上限，超限报错；
   写解码同阈值先验后解（`bch2_bio_uncompress`）。

## 复用指南

- 小 IO 跳过压缩是硬规则，禁止为统一路径而浪费。
- 算法档位用 level 阈值切换，快慢版内存语义不同必须分别
  预留。
- 内存池按超块特性按需建，禁止全算法常驻。
- 与 `core-compress-retry-verify`（重试/验证/传播）互补：本
  节点管"选什么、建什么"，那个管"失败怎么办"。

---
schema: pdca.asset/v1
id: ontology:domain/core-str-hash-multialgo
type: domain
layer: Knowledge
status: active
summary: str_hash四算法选型 + 掩码 + whiteout跳过 + 快照查找
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-bkey-packed-encoding
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 目录与 xattr 哈希选型、快照内查找、消毒镜像豁免场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/fs/str_hash.h 在仓库中存在且含 bch2_str_hash_opt_to_type 定义"
- name: constraints
  desc: 哈希查找前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认算法门控、掩码保留、洞截断三条前提在引用代码中有对应实现"
---

# str_hash 多算法选型与快照查找

沉淀自 T0498（内核第十轮）。对照 bcachefs `fs/fs/str_hash.h`、
`fs/fs/str_hash.c`、`fs/fs/dirent.c`、`fs/fs/xattr.c`。

## 背景

目录与 xattr 需哈希索引，但算法要演进、快照要隔离、消毒镜像要
豁免。若哈希写死一种算法，升级即全量重建；若无视快照，跨快照
查错键。

## 核心概念

1. **四选一播种**：crc32c/crc64 直映射，siphash 按特性位选新
   旧版；旧版额外经 sha256 派生密钥
   （`bch2_str_hash_opt_to_type`）。
2. **去符号位掩码**：64 位哈希右移去符号位；31 位模式掩码，
   标志取自 inode；dirent 前两位保留给 `.`/`..`
   （`bch2_str_hash_end`）。
3. **whiteout 跳过与洞截断**：whiteout 空语句跳过继续找；非
   whiteout 空洞截断插入；辅助找首不可见槽
   （`bch2_hash_lookup_in_snapshot`）。
4. **快照内查找**：先取快照号，再区间遍历；可见性按子卷过滤
   （`bch2_hash_lookup`）。
5. **消毒镜像豁免**：sanitize 抹名未更新哈希位，同长名必碰撞，
   故直接跳过修复（`bch2_str_hash_check_key`）。

## 复用指南

- 哈希算法选型必须经特性门控，禁止硬切。
- 保留槽位（`.`/`..`）必须在掩码层保证，禁止调用方记忆。
- 消毒镜像的派生不一致必须豁免而非修复。

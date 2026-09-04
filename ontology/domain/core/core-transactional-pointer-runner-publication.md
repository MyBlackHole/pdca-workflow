---
schema: pdca.asset/v1
id: ontology:domain/core-transactional-pointer-runner-publication
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-transactional-pointer-runner-publication/1.0.0
summary: Transactional pointer runner 与 publication 边界
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 transactional-pointer-runner-publication 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# Transactional pointer runner 与 publication 边界

## 可复用规则

对 bcachefs 风格存储引擎，transaction trigger runner 必须按 btree sort-order 分组，
在每组内重复扫描直到没有 trigger 追加 update；同一 update 的 insert/overwrite 状态
各执行一次，`norun` update 全程跳过。派生 alloc/backpointer update 必须回到同一事务，
这样 replace/delete 的 old→new 顺序不会产生悬挂引用或重复计数。

recovery 的 journal replay 只安装 primary pointer（使用 `norun`），不能提前发布派生树。
replay 完成后清空派生树，扫描 primary 重建并校验，成功后才允许查询派生状态。

对 interior split/grow，节点写回必须先完成新节点的 durable write，再在独立的
nodes-written transaction 中按 old trigger + overwrite journal、new trigger + btree/root
journal 的顺序发布；split restart 期间要保留 old/new 状态，不能在 restart 分支直接触发。

## 适用边界

本规则适用于单格式、members-v2 geometry 已 attach 的存储核心；allocator、GC、stripe、
LRU 和 VFS 仍需独立的上游对照与任务验收。

## 来源

`records/T0182/conclusion.md`；本地对照源码为
`/home/black/Documents/bcachefs-tools/fs/btree/commit.c`、`alloc/buckets.c`、
`alloc/backpointers.h`、`btree/interior.c` 与 `init/recovery.c`。

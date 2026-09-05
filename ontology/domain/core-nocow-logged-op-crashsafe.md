---
schema: pdca.asset/v1
id: ontology:domain/core-nocow-logged-op-crashsafe
type: domain
layer: Knowledge
status: active
summary: nocow符号锁 + logged_op截断状态机 + fallocate双路径
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-reflink-trigger-refcount-self-delete
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 桶粒度读写互斥、截断插洞崩溃安全、预留与直分双路径场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/data/nocow_locking.c 在仓库中存在且含 bch2_bkey_nocow_lock 定义"
- name: constraints
  desc: 互斥与状态机前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认符号互斥、游标幂等、双路径分叉三条前提在引用代码中有对应实现"
---

# nocow 符号锁与 logged_op 崩溃安全

沉淀自 T0496（内核第八轮，全扫复核）。对照 bcachefs
`fs/data/nocow_locking.c`、`fs/data/io_misc.c`。

## 核心概念

1. **桶符号计数共享锁**：拷贝与更新符号互斥；哈希桶复用少量
   槽；慢路径排序后定序重抢防死锁（`bch2_bkey_nocow_lock`）。
2. **logged_op 截断插洞状态机**：截断/插洞分开始/移位/完成多
   阶段提交，游标幂等可续；持快照创建锁防竞态
   （`bch2_truncate`、`__bch2_resume_logged_op_truncate`、
   `bch2_fcollapse_finsert`）。
3. **fallocate 双路径**：按 nocow 与版本门限分叉；预留路径算
   新副本加部分预留对冲空间不足（`bch2_extent_fallocate`）。
4. **与既有节点边界**：reflink 节点管共享计分，本节点管桶互斥
   与前台变更崩溃安全。

## 复用指南

- 桶粒度互斥用符号计数而非读写锁，拷贝与更新语义不同。
- 多阶段变更必须游标幂等可续，崩溃后 resume 而非重做。

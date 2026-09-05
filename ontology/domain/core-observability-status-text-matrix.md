---
schema: pdca.asset/v1
id: ontology:domain/core-observability-status-text-matrix
type: domain
layer: Knowledge
status: active
summary: 全子系统 status_to_text 自白矩阵 + sysfs 统一通道
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-journal-reclaim-proptest-pattern
  - ontology:domain/core-fsck-repair-mode
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 长任务黑盒问题定位、挂死现场取证、统一运维接口场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/debug/sysfs.c 在仓库中存在且含 bch2_fs_show 定义"
- name: constraints
  desc: 自白矩阵的前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认只读不持长锁、流式分段、挂死可用三条前提在引用代码中有对应实现"
---

# 全子系统 status_to_text 自白矩阵

沉淀自 T0490（纵深分析）。对照 bcachefs `fs/debug/sysfs.c`、
`fs/debug/debug.c`、`fs/data/reconcile/work.c`、
`fs/init/passes.c`、`fs/journal/journal.c`。

## 核心概念

1. **自白矩阵**：reconcile/recovery/journal/btree_cache/
   copygc_wait/nocow_locks/io_timers 全实现 `__cold void
   *_to_text(printbuf*,…)`，`bch2_fs_show` 按需调度；挂死时
   `cat internal/*` 即得等待者 + 锁 + 进度，无需复现。
2. **sysfs 零样板通道**：一个 SHOW 宏承包全部只读属性（内存
   打印 → 换行 → 截断 → err 转换）；分发靠属性指针比对；
   `*_to_text` 与 sysfs 解耦，可复用于 dmesg/debugfs。
3. **trans 全景 + 死锁自证**：`btree_transactions` 以 srcu 快照
   全部事务并逐个打印 backtrace；`btree_deadlock` 循环调环检测
   找环，找到即停（`debug.c:bch2_btree_transactions_read`）。
4. **debugfs 增量流式 dump**：分段 copy_to_user + memmove；
   每键 trans_unlock + flush；扫缓存用 RCU，不持长锁
   （`debug.c:bch2_debugfs_flush_buf`）。

## 复用指南

- 每个长任务必须实现状态文本函数并挂入统一展示点；"黑盒
  长任务"是设计缺陷而非运维常态。
- 取证接口必须在挂死时可用：只读、不持长锁、流式分段。
- 展示层（sysfs/dmesg/debugfs）与内容生成（to_text）解耦。

---
schema: pdca.asset/v1
id: ontology:domain/core-util-sync-primitives
type: domain
layer: Knowledge
status: active
summary: seqmutex乐观重锁 + io时钟调度 + vstruct遍历
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-six-slowpath-wakeup
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 轻量乐观锁、IO扇区逻辑时钟、变长结构链遍历场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/util/seqmutex.h 在仓库中存在且含 seqmutex_relock 定义"
- name: constraints
  desc: 原语使用前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认双检防ABA、批叠时钟、无丢失等待三条前提在引用代码中有对应实现"
---

# 轻量同步原语三件套

沉淀自 T0497（内核第九轮，二轮复核）。对照 bcachefs
`fs/util/seqmutex.h`、`fs/util/clock.c`、`fs/util/vstructs.h`。

## 核心概念

1. **seqmutex 乐观重锁**：mutex + seq 混合；lock 时 seq++，
   relock 双检 seq + trylock 防 ABA（`seqmutex_relock`）。
2. **io 时钟扇区调度**：per-CPU 批量叠加 + 原子 now + 最小堆
   定时器；过期到发立即执行；无丢失唤醒 kthread 等待
   （`bch2_io_timer_add`、`__bch2_increment_clock`）。
3. **vstruct 变长链遍历**：`_data + u64s` 链按类型区分位宽 +
   对齐断言 + 安全遍历宏（`vstruct_next`、
   `vstruct_for_each_safe`）。
4. **与既有节点边界**：six 节点管读写锁，closure 节点管异步，
   本节点管轻量乐观锁与时钟调度。

## 复用指南

- 短临界用 seqmutex 而非读写锁，重锁双检缺一不可。
- 定时调度用逻辑时钟 + 最小堆，禁止每定时器一线程。

---
schema: pdca.asset/v1
id: ontology:domain/core-six-usage-discipline
type: domain
layer: Knowledge
status: active
summary: SIX锁调用方四规范：快慢分发/预标记/持有跟踪/身份快照
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-six-intent-seq-deadlock-free-locking
  - ontology:domain/core-six-slowpath-wakeup
  - ontology:domain/core-btree-transaction-memory-io
  - ontology:pattern/intent-staged-update
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: SIX 锁调用方规范、快慢分发、持有跟踪场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 btree_node_lock 系列函数在仓库中存在"
- name: constraints
  desc: 调用方义务前提
  constraint: 见正文
  testable_signal: "通读正文四规范节，确认每条规范的调用方义务在引用代码中有对应实现"
---

# SIX 锁调用方四规范

沉淀自锁教学收官（T0538）。对照 bcachefs `fs/btree/locking.h`、
`fs/btree/locking.c`。本节点只讲调用方如何正确使用锁，不讲锁机制
本身（机制见 six-intent/six-slowpath 节点）。

## 背景

SIX 原语故意保持最小，把跟踪、预判、快照推给调用方。用错不报错，
只表现为随机挂死。本节点收敛四条调用方铁律。

## 核心概念

调用方四规范总览（详见下节 q）：

1. **快慢分发诚实化**：`btree_node_lock` 快路 trylock，确知竞争用 `contended` 跳检
2. **预标记写先行**：取写前先标记，检测器提前视你为写者
3. **持有跟踪上移**：path 位图补 per-thread 跟踪，同级已持即复用
4. **身份快照防幻影**：key 哈希快照，睡前比对，不等重启

## 规范一：快慢分发诚实化

`btree_node_lock` 快路一次 trylock，失手进慢路；确知竞争用
`contended` 跳检。调用方必须诚实：确知才跳，否则慢路开销反超。
慢路内重 try 兜底跳检误判。

## 规范二：预标记写先行

取写前先标记写持有，再 trylock。因 SIX 非公平、读遇写等待阻塞，
检测器须提前视你为写者，否则漏边。宣告先于获取是通用原则
（per-CPU 读宣告同理）。

## 规范三：持有跟踪上移

SIX 不做 per-thread 跟踪，调用方用 path 位图补：跨 path 发现本事务
别处已持同级锁即 increment 复用，避免自死。重入计数与解锁配对，
漏配对即锁泄漏。

## 规范四：身份快照防幻影

查到指针有效时快照其哈希（须用 key 的哈希而非节点当前值，否则
回收重哈希到新身份恰相等而漏检）；睡眠前比对，不等强制重启；
0 值禁用。reclaim 与重用竞态转为可检测重启，而非挂死。

## 违反后果

- 快慢撒谎：该慢不慢烧 CAS，该快不快走慢路，两头亏。
- 不预标记：死锁检测漏边，环 journ 存在但查不出。
- 不跟踪持有：自死锁，表现为固定场景挂死。
- 不快照身份：幻影节点睡眠，永不唤醒，极难排查。

## 复用指南

- 封装锁调用时，四规范逐条检查：分发诚实否、预标记否、跟踪否、
  快照否。
- 危险原语（批量借还）收敛到单一调用点，禁止扩散。

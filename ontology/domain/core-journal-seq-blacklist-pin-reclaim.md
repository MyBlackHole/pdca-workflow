---
schema: pdca.asset/v1
id: ontology:domain/core-journal-seq-blacklist-pin-reclaim
type: domain
layer: Knowledge
status: active
summary: journal seq 黑名单保序 + pin 分级 reclaim + clean 段跳过回放
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-journal-key-layout-validation
  - ontology:domain/core-journal-reclaim-proptest-pattern
  - ontology:domain/core-observability-status-text-matrix
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 日志结构存储的崩溃恢复保序、回收死锁避免、干净关闭加速场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/journal/seq_blacklist.c 与 fs/sb/clean.c 在仓库中存在"
- name: constraints
  desc: 三机制的启用前提与代价
  constraint: 见正文
  testable_signal: "通读正文约束节，确认黑名单持久化、分级门限、clean 校验失败回退三条前提在引用代码中有对应实现"
---

# seq 黑名单保序 + pin 分级 reclaim + clean 段

沉淀自 T0488（confirmed），来源
`records/T0488-0905-bcachefs-strengths/`。对照 bcachefs
`fs/journal/seq_blacklist.c`、`fs/journal/reclaim.c`、`fs/sb/clean.c`。

## 核心概念

1. **seq 黑名单保序**：crash 后若 bset 先于其 journal 落盘，直接
   重放会乱序。bset 记 journal_seq，启动时"新于最新 journal"则
   丢弃，且该 seq 永不复用并持久化到超块
   （`seq_blacklist.c:13-49`）；区间合并 + Eytzinger 二分使高频
   查询 O(log n)。
2. **pin 分级 reclaim**：刷 pin 需耗 journal 空间，超前于 replay
   会死锁，故遇 unreplayed 即停；按 pin 类型分 btree/key_cache/
   other 分级放行（`reclaim.c:778-801`）。慢路径等待按最慢成员
   延迟算（flushing commit 要 preflush 全部 rw 成员），满时就地
   reclaim 防 workitem 冻结（`journal.c:924-962`）。
3. **clean 段跳过回放**：干净关闭把树根/用量/时钟塞入 clean 段；
   下次比对 journal_seq 与树根，不一致则丢弃 clean 强制走日志
   （`clean.c:bch2_fs_mark_clean/bch2_verify_superblock_clean`）。

## 复用指南

- 任何"先记日志后改数据"的引擎：落盘顺序与重放顺序必须由 seq
  单调性 + 黑名单共同保证，不能只靠时间戳。
- reclaim 与 replay 的先后关系必须显式建模，超前即停优于死锁
  后排查。
- clean 段是纯加速结构：校验失败必须能回退到全量回放。
- 与 `core-journal-key-layout-validation`（单 key 布局校验）、
  `core-journal-reclaim-proptest-pattern`（reclaim 测试模式）互补。

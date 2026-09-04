---
schema: pdca.asset/v1
id: ontology:domain/core-journal-reclaim-proptest-pattern
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-journal-reclaim-proptest-pattern/1.0.0
summary: journal reclaim 属性测试设计模式
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
  testable_signal: "检查本文件 journal-reclaim-proptest-pattern 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# journal reclaim 属性测试设计模式

来源：T0173-0801-journal-reclaim-proptest（bcachefs 风格 Rust 存储引擎属性测试）。

## 上下文与约束

reclaim 裁剪路径（`last_seq` 推进、旧 journal 记录回收）在随机属性测试中
天然是冷路径：8MB journal 区 + ~120 组 ops 远不足以触发 high watermark
后台回收。T0169 修复的丢键 bug 恰在裁剪后恢复路径，无属性级回归保障。

## 假设与行动

- 属性测试中显式调用直接路径 `reclaim_journal()`（checkpoint_locked：
  flush pins → 推进 last_seq），确定性强、无需超时等待。
- 裁剪生效用 `metrics().journal_last_sequence_ondisk`（engine.rs:204 公开
  字段）断言单调不倒退（`>=`，容忍无覆盖数据时不推进）。
- 裁剪正确性（推进过头丢键）由恢复后 `assert_model` 隐式验证。

## 结果与证据

- 5/5 AC 通过；8 轮 × 64 cases 稳定；lib 173/173、集成 9/9。
- 恢复重放起点 = `last_seq`（bcachefs recovery.c:763 `journal_replay_seq_start`）。

## 成功原因

- 触发频率（reclaim_every 3..=6）高于 crash 频率（crash_every 9..=17），
  保证多数崩溃窗口前已发生过 reclaim，裁剪后恢复路径被充分踩到。
- 直接路径 + 公开计数器断言，无自造检查逻辑（约束 12/13）。

## 适用与不适用条件

- 适用：引擎有显式同步 API + 可观察持久化计数器的场景。
- 不适用：无公开触发 API、或回收是纯后台异步且无等待接口的场景
  （此时需 wait_for_reclaim 类接口，测试耗时上升）。

## 下一轮建议

- 若后台 worker 路径需属性级覆盖，可加 `request_reclaim + wait_for_reclaim`
  变体测试；本次按用户决策留作既有单测职责。

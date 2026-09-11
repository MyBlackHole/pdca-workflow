---
schema: pdca.asset/v2
id: ontology:domain/core-closure-sync-waitlist
type: domain
layer: Knowledge
status: active
summary: closure同步休眠语义 + 单归属等待队列 + 返回分化
domain:
- ontology:domain/core
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/core
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 引用计数异步原语、同步等待异步完成、公平唤醒场景
  constraint: 见正文
  testable_signal: 抽查正文引用的 fs/vendor/closure.c 在仓库中存在且含 bch2_closure_wait 定义
  evidence_level: unclassified
- name: constraints
  desc: 等待队列前提
  constraint: 见正文
  testable_signal: 通读正文约束节，确认单归属、引用占位、内存屏障三条前提在引用代码中有对应实现
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

# closure同步休眠 + 公平等待队列

沉淀自 T0492（内核第四轮）。对照 bcachefs
`fs/vendor/closure.h`、`fs/vendor/closure.c`。

## 核心概念

1. **SLEEPING 休眠语义**：sync 将调用者记为 sleeper 并置换初始
   计数，循环睡到计数剩 1（而非归零）再唤醒
   （`__bch2_closure_sync`、`bch2_closure_sub`）。
2. **单归属 waitlist + FIFO 公平**：先查防双挂，再原子占引用
   后入队；唤醒侧全取 + 保序逐个减引用；对外唤醒先内存屏障
   （`bch2_closure_wait`、`__bch2_closure_wake_up`）。
3. **同步/析构返回分化**：异步返回走 requeue/done + 放 parent；
   同步返回等 outstanding、不重装计数，后续 get 必失败；
   析构返回以标志延迟调析构且析构时仍持有 parent 引用。
4. **守卫断言 + 超时可撤销**：归零但非常规标志仍在即告警；
   DEBUG 下 get 越界 BUG_ON；超时 CAS 加回计数并清标志返
   ETIME；条件等待宏以栈闭包 + 循环 + 尾部唤醒实现
   （`closure_val_checks`、`__bch2_closure_sync_timeout`）。

## 复用指南

- 同步等待语义必须是"剩 1"而非"归零"，调用者自身占一份。
- 等待队列必须单归属 + 入队前占引用，禁止无引用入队。
- 超时路径必须能撤销等待状态并返回可区分错误码。

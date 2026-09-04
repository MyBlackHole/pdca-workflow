---
schema: pdca.asset/v1
id: ontology:domain/core-concurrent-combined-commit-log
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-concurrent-combined-commit-log/1.0.0
summary: 并发组合提交日志：多写者 × 崩溃恢复精确断言（T0203）
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
  testable_signal: "检查本文件 concurrent-combined-commit-log 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 并发组合提交日志：多写者 × 崩溃恢复精确断言（T0203）

## 适用场景

2-3 个写者线程在同一持久化引擎上交错执行组合 op（btree put/delete ×
allocate/reclaim/queue_discard/run_discard_worker_once），崩溃后恢复
状态必须**精确**等于已提交 op 的确定性重放模型（非最终一致）。

## 关键事实（引擎语义）

1. **提交顺序 = 持久化顺序**：引擎全局 fs 锁串行化所有事务提交
   （T0199 并发矩阵实测）。因此只要在**同一把测试锁内**完成
   "引擎提交 + 日志追加"（原子成对），日志行顺序就 == 真实提交
   顺序——日志是精确性的确定性来源，交错只改变日志内容，不改变
   可重放性。
2. **崩溃点协议**：日志落盘（sync_all）→ engine.sync()（journal
   落盘）→ abort。全部已提交 op durable；恢复 = replay 已落盘记录
   （journal replay 只回放 seq_ondisk 边界内记录，fs/journal/read.c
   journal_replay_maybe_drop_overwrites）。
3. **日志行二元组协议**：`<op 编码> | <结果编码>`。重放依赖**引擎
   真实结果**（ok/err 编码）驱动模型转换——allocate 成功解析返回
   offset 断言落在模型桶域、失败按 err 编码分支；并发 -28（空间
   耗尽）、-17（重复 queue 幂等）、worker 回旋、-11（空队）全部由
   真实结果驱动，无需预判守卫。这使模型与真实提交序列**同构**。
4. **Barrier 起跑**：N 写者 Barrier 同步后各自执行随机计划（每写者
   6..=12 步），保证并发窗口真实重叠；引擎 fs 锁决定实际交错。

## 模型结构

- T0202 BucketModel 三态（0=free/1=btree-owned/2=need-discard）+
  queued[4] + VecDeque + btree BTreeMap；崩溃后 alloc 树投影
  rebuild_bucket_state（data_type 三态映射）做精确断言。
- 断言面：btree 内容精确相等 + alloc 三态精确相等 + discard 队列
  空（open_persistent 不自动入队）+ discover 树位计数 == need-discard
  桶数 + verify_all。

## 与 T0201 的关系

T0201 并发崩溃只断言最终一致（后台 reclaim 竞态）；T0203 以提交
日志锁定提交序列后做到精确断言——两者是递进关系：先证明"一致"，
再证明"等于确定性重放"。

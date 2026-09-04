---
schema: pdca.asset/v1
id: ontology:domain/core-public-guard-assertions
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-public-guard-assertions/1.0.0
summary: 公开守卫断言套件（verify_guard_invariants 模式）
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
  testable_signal: "检查本文件 public-guard-assertions 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 公开守卫断言套件（verify_guard_invariants 模式）

## 适用场景

存储引擎已有散落的守卫不变量（open/not_rw 桶保护、drop 无泄漏、队列
耗尽），需要提升为可复用公开断言 API 供测试与调用方共用。

## 模式要点

1. **单入口聚合**：对齐 bch2_check_allocations（check.c:1097-1160）
   recovery pass 语义——一个入口校验全部不变量，失败返回具体错误变体，
   不修改状态。聚合入口让调用方一次运行全部守卫，避免遗漏。

2. **断言只读**：校验 API 为纯快照式（持有 fs 锁完成扫描），与
   verify_bucket_indexes 行为一致；不改变被校验对象的运行行为。

3. **查询与断言分离**：drop 无泄漏用查询 API（open_bucket_count）而非
   校验 API——泄漏检测的强制点在 Drop panic（T0192），查询 API 供调用方
   提前自查；队列空用查询（discard_queue_empty）而非 worker 内自动校验，
   因为 EAGAIN 轮转（-11）时队列非空是合法状态，自动校验会误报。

4. **锁序复用**：聚合校验在 fs 锁内按既有锁序（fs→open_buckets→rw_devs）
   取快照，与 reclaim/discard 一致，不引入新锁序；校验 API 本身与守卫
   实现互为验证（守卫拒绝非法转移，断言验证状态从不进入非法态）。

## 错误建模

守卫违背复用既有 EngineError::DerivedState 通道，新增枚举变体
（OpenBucketFree/NotRwBucketFree），不引入新错误码。

## 测试迁移价值

既有定向测试与属性测试切换到公共断言后，实现与测试共享单一事实源；
属性测试逐 op 调用聚合断言，可删除模型内的重复局部检查（模型只保留
自身决策逻辑）。

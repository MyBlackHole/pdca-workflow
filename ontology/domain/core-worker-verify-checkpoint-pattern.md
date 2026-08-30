---
schema: pdca.asset/v1
id: ontology:domain/core-worker-verify-checkpoint-pattern
type: domain
layer: Knowledge
status: active
summary: worker 变体最终一致性检查点模式
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
  testable_signal: 由领域实践与测试验证
---

# worker 变体最终一致性检查点模式

## 适用场景

系统存在后台 worker（discard/reclaim/回收线程）维护派生状态（freespace、
need_discard、journal 回收），需要验证"worker 运行后引擎仍一致"。

## 模式要点

1. **测试级检查点**：不新增"worker 后自动 verify"的公开 API（上游无对应
   函数，约束 8）——把 verify_all + 队列空断言组合成测试级检查点矩阵，
   复用既有公开 API（verify_all、discard_queue_empty）与内部辅助
   （prepared_bucket_engine、add_free_bucket）。

2. **矩阵维度**：
   - 正常 drain：队列清空后 verify_all Ok + 队列空。
   - 并发入队：多个生产者并发 queue 后单 worker drain 全部，verify_all Ok。
   - EAGAIN 旋转：桶延迟但队列非空是**合法状态**，verify_all 仍通过。
   - not_rw 设备：worker 跳过、恢复 rw 后 verify_all Ok。
   - 非法态：not_rw free 桶是故意构造的非法态，verify 必须报对应错误名
     （NotRwBucketFree）——检查点区分"合法态必须通过"与"非法态必须报错"。

3. **端到端重开验证**（最关键的检查点价值）：worker 完成后 flush →
   drop → open_persistent → verify_all + 数据核对仍通过——验证 worker
   维护的派生状态**持久化后**仍可被一致性校验验证（对齐上游
   alloc/check.c:323-345 freespace 校验语义）。

4. **reclaim checkpoint 验证**：request_reclaim → wait_for_reclaim
   （completed≥requested、last_error=None）→ verify_all → 重开核对数据
   完整（对齐 journal/reclaim.c checkpoint 驱动语义）。

## 测试模式

- 既有单校验断言切换为 verify_all 聚合后，多数 worker 测试自动带检查点
  （T0194 切换 35 处）；新任务先盘点既有覆盖找缺口，避免重复构造。
- flush_journal 必须在 drop 前调用，确保清除/checkpoint 持久化后再重开，
  否则重开验证产生假阳性（需区分 flush 与未 flush）。

## 边界

- 非法态（not_rw free 桶）保留单校验断言（verify_guard_invariants）或
  verify_all 报错断言，不在检查点矩阵中强制通过。
- worker 后重开验证是"持久化一致性"检查，不是"恢复语义"测试
  （后者属于 crash/restart 专项）。

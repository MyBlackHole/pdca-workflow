---
schema: pdca.asset/v1
id: ontology:domain/linux-epoll-eventloop-event-loop-time-conservation
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/linux-epoll-eventloop-event-loop-time-conservation/1.0.0
summary: 事件循环时间守恒分解（event-loop time conservation accounting）
domain:
- ontology:domain/linux-epoll-eventloop
relations:
  specializes:
  - ontology:domain/linux-epoll-eventloop
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# 事件循环时间守恒分解（event-loop time conservation accounting）

来源: records/T0296-0816-reactor-phase-accounting/conclusion.md
适用: 需要把事件循环的"忙"归因到明确域，且想知道"时间去哪了"的系统

## 核心思路

事件循环线程的时间，用**两域不相交会计**拆成三部分：

```text
callback_wall_ns + phase_wall_ns + residual_ns == reactor_wait_ns
```

- **callback 域**：leaf 回调（FD 事件、post 回调、timer 回调）的执行时间；
- **phase 域**：内部 bookkeeping（epoll 等待、事件 dispatch 前/后、post 批量 drain、
  timer 分发）的执行时间；
- **residual**：两域都解释不了的时间（线程去调度、未插桩 gap、调度器噪声）。

三部分都在同一个 enqueue→run 墙钟区间内度量，求和守恒。

## 关键设计点

1. **会计域不相交是守恒前提**：相位区间刻意记录在 leaf callback 体之外——
   事件 dispatch 前埋一次点、回调返回后再埋一次点，中间的回调执行区间只进
   callback 历史。两域不重计、不遗漏，求和才是"总忙"。
   ```text
   [dispatch_begin ──── dispatch_pre_end]     相位(EVENT_DISPATCH)
                         [callback 执行]        callback 历史
                                            [callback_return ──── now]  相位(EVENT_DISPATCH)
   ```
2. **固定基数、无 payload**：相位记录只有 `{seq, begin_ns, end_ns, enum}`，
   不携带 FD/路径/负载/标签。环形容量固定（callback 256 / phase 512），
   可观测性不随业务规模膨胀，也不互相挤占。
3. **双序列快照窗口**：producer（worker 入队时）用 acquire 快照两个序列游标
   （callback_sequence/phase_sequence）+ 时间戳；consumer（回调运行时）按
   "序列 > 快照值 且 ≤ 当前"过滤 + [enqueue, run] 区间重叠裁剪。天然处理并发与覆盖。
4. **环回绕显式报 truncated，不假装完整**：环形被写满时 `coverage_complete=false`，
   该窗口不产出守恒归因——宁可缺证据，不做假分解。
5. **残差是保守信号，不是根因断言**：residual 只说"两域都解释不了这么多时间"
   （线程去调度/未插桩 gap 是候选），证据边界与根因猜测严格分离。

## 诊断分级（离线消费侧）

| finding | 条件 | 语义 |
|--------|------|------|
| phase-history-truncated | 相位环回绕 | 拒绝归因（证据不足） |
| internal-phase-busy | 相位墙钟 ≥ 阈值 | 归因到具体相位（top_phase + 明细） |
| residual-delay | 残差 ≥ 阈值 | 归因到域外（去调度/未插桩） |

三者都是 confirmed 置信度但语义逐级保守。

## 陷阱与边界

- `epoll-wait` 相位含线程去调度时间，不能直接解读为 epoll 问题。
- 相位与 callback 共享一个使能开关时，无法只开相位长期采集。
- 减数非负检查失败（会计域重叠 = bug）时若静默省略字段，会掩盖实现缺陷——
  建议输出显式哨兵。
- 窗口只覆盖 enqueue→run，不含 work 执行本身。

## 验收信号

- 有窗内数值验证守恒等式（如 backupstream 集成测试：callback 100M + phase 200M +
  residual 1200M == wait 1500M）。
- 高事件率下历史频繁 truncated 时，只产生"拒绝归因"而非"错误归因"。
- 诊断能指出不可见忙到底在相位还是域外，而不是笼统的"reactor 忙"。

## 参考实现

backupstream v101（commit 867da08）：reactor.cpp/reactor.hpp（记录+窗口）、
work_pool.cpp（producer 快照）、agent_observability.cpp（server 归因）、
backup_observe.cpp（离线 diagnose）。
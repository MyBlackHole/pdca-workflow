---
schema: pdca.asset/v1
id: ontology:pattern/weighted-fair-allocation
type: pattern
layer: Knowledge
status: active
summary: 虚拟时间加权公平分配模式
source_task: T0507
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-allocator-wfq-watermark-reservation
  - ontology:domain/core-lru-bitmap-selfheal
attributes:
  - name: applicability
    desc: 多资源按容量加权分配、新成员加入场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-allocator-wfq-watermark-reservation 存在
  - name: consequences
    desc: 按需分配无饿死、新成员不独占、需虚拟时间同步
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
  - name: violations
    desc: 不用本模式的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中定位
---

# 虚拟时间加权公平分配

来源：T0507 提炼，T0508 扩充；源节点
`core-allocator-wfq-watermark-reservation`、`core-lru-bitmap-selfheal`；
对照 bcachefs `fs/alloc/foreground.c`、`fs/alloc/lru.c`。

## 问题

多盘按空闲分配时，简单轮询饿死小盘，贪心最空盘饿死大盘；新盘加入
瞬间独占分配；计数溢出丢公平性。

## 方案

1. **虚拟时间加权**：每资源虚拟时间，最小者胜出、步长按空闲加权
   （`dev_stripe_state`）。
2. **新成员抬升**：新盘抬到旧盘最小值而非零，避免独占
   （`dev_stripe_state_sync`）。
3. **溢出重缩放**：计数溢出下溢重缩放不丢信息
   （`bch2_stripe_state_rescale`）。
4. **故障域优先**：先比域再比时间，纠删时同域硬剔除
   （`__dev_alloc_list`）。
5. **位图自愈配套**：位图缺失单向补齐，反向校验归位，消费侧只
   读不修（`bch2_lru_check_set`）。

## 后果

按需分配无饿死；代价是虚拟时间需同步维护，新成员抬升策略必须显式；
位图生产消费必须分离。

## 违反后果

- 轮询/贪心：小盘或大盘饿死，容量越用越斜。
- 新盘零起：新盘被打爆，旧盘闲置，失衡数天。
- 消费侧修位图：读写竞争，位图永远对不上。

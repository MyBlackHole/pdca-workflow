---
schema: pdca.asset/v1
id: ontology:pattern/unified-relocation-engine
type: pattern
layer: Knowledge
status: active
summary: 单引擎加谓词注入统一搬迁模式
source_task: T0507
relations:
  specializes: [ontology:pattern]
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:domain/core-reconcile-phased-orchestration
  - ontology:domain/core-copygc-fragment-selection
attributes:
  - name: applicability
    desc: 多搬迁策略共存（清运/疏散/均衡/修复）场景
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-move-unified-relocation-engine 存在
  - name: consequences
    desc: 策略扩展只加谓词、IO管线单一、调度契约纯函数
    constraint: ""
    testable_signal: 通读正文后果节，确认三条后果在源节点与引用代码中有对应实现
  - name: violations
    desc: 不用本模式的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中定位
---

# 单引擎谓词注入统一搬迁

来源：T0507 提炼，T0508 扩充；源节点
`core-move-unified-relocation-engine`、
`core-reconcile-phased-orchestration`、`core-copygc-fragment-selection`；
对照 bcachefs `fs/data/move.c`、`fs/data/reconcile/work.c`、
`fs/data/copygc.c`。

## 问题

清运疏散均衡修复各一套 IO 管线，重复代码且语义漂移；调度契约
各说各话，分配器与清运互相等死。

## 方案

1. **策略与管线解耦**：谓词只决策搬跳与目标，异步管线全共享
   （`bch2_move_extent_pred`）。
2. **整单元优先**：条带整搬不打碎，碎条带不重写活数据
   （`may_reuse_stripe`）。
3. **调度契约纯函数**：分配器与清选用同一判据，永不等错
   （`bch2_copygc_can_make_progress`）。
4. **九阶段流水线编排**：扫描分型各走各路，满目标转待定闭环，
   物理有序扇出，无丢失唤醒（`reconcile_phases`）。
5. **碎片排序选桶**：按碎片度排序选最差桶，自留预留，在途去重，
   独立线程（`bch2_copygc_get_buckets`）。

## 后果

新策略只加谓词；代价是引擎必须足够通用，谓词禁碰 IO 细节；
调度契约必须是纯函数，多方共用。

## 违反后果

- 多套管线：修一处漏三处，语义悄悄漂移。
- 判据各说各话：分配器与清运互相等待，死锁只能重启。
- 无预留清运：把空间搬空后无处落笔，自饿死。

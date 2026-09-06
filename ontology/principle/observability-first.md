---
schema: pdca.asset/v1
id: ontology:principle/observability-first
type: principle
layer: Knowledge
status: active
summary: 可观测优先原则
source_task: T0508
relations:
  specializes: [ontology:principle]
  relates_to:
  - ontology:domain/core-observability-status-text-matrix
  - ontology:domain/core-time-stats-cheap-instrumentation
  - ontology:domain/core-sb-persistent-counters
attributes:
  - name: applicability
    desc: 长任务黑盒消除、挂死取证、性能埋点
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-observability-status-text-matrix 存在
  - name: violations
    desc: 违反本原则的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中定位
---

# 可观测优先

来源：T0508 提炼；源节点 `core-observability-status-text-matrix`、
`core-time-stats-cheap-instrumentation`、`core-sb-persistent-counters`；
对照 bcachefs `fs/debug/sysfs.c`、`fs/util/time_stats.c`、
`fs/sb/counters.c`。

## 背景问题

长任务（恢复、清运、重建）动辄数小时，黑盒即误杀（90 秒超时杀恢复
的教训）；挂死时 dmesg 无信息只能复现碰运气；性能埋点太贵不敢开，
出问题两眼一抹黑。

## 约定

1. **每个长任务实现状态文本并挂统一展示点**：reconcile/recovery/
   journal/btree_cache 全是 `*_to_text`，sysfs 同一目录暴露；挂死
   `cat` 即得等待者加锁加进度，无需复现。
2. **取证接口挂死可用**：只读、不持长锁、流式分段；展示层与内容
   生成解耦，一套 to_text 供 sysfs/dmesg/debugfs。
3. **埋点开销分级**：冷路径直写、热路径攒批、超热可关，切换自动
   按阈值；一个宏一次定义数十事件，sysfs 表自动生成，加埋点只
   加一行。
4. **统计双视角**：全量均值与加权近期均值并列，一眼区分一直慢与
   刚变坏；分位数常数内存近似，默认关闭按需开。
5. **计数持久化**：通用计数 stable 映射落盘，延迟采样，ioctl 可查；
   命名围栏让关机时说出谁没放引用。

## 违反后果

- 长任务无状态文本：用户误杀、运维盲飞，恢复被杀循环真实发生过。
- 取证持长锁：挂死时取证接口同样挂死，形同虚设。
- 单均值统计：长尾与漂移误导优化方向，白忙一场。

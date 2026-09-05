---
schema: pdca.asset/v1
id: ontology:domain/core-sb-persistent-counters
type: domain
layer: Knowledge
status: active
summary: SB持久计数器stable映射 + 延迟采样 + ioctl查询
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-observability-status-text-matrix
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 超块持久计数、跨版本兼容、运维查询场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/sb/counters.c 在仓库中存在且含 bch2_sb_counters_to_cpu 定义"
- name: constraints
  desc: 计数持久化前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认 stable 映射、延迟采样两条前提在引用代码中有对应实现"
---

# SB 持久计数器

沉淀自 T0499（内核第十一轮）。对照 bcachefs `fs/sb/counters.c`。

## 核心概念

1. **percpu 计数 + stable 映射**：内存 percpu 累加，落盘经
   stable_id 兼容映射（`bch2_sb_counters_to_cpu/from_cpu`）。
2. **半秒延迟采样**：work 延迟采样落盘， Balance 开销与实时性
   （`bch2_sb_counters_work`）。
3. **ioctl 查询**：用户态经 ioctl 读计数。
4. **与既有节点边界**：错误计数是错误专用，本节点是通用持久
   计数器框架。

## 复用指南

- 持久计数必须 stable 映射隔离版本，禁止裸枚举落盘。
- 采样落盘必须延迟批量，禁止每次累加即写。

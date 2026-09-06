---
schema: pdca.asset/v1
id: ontology:domain/core-ec-rs-algorithm
type: domain
layer: Knowledge
status: active
summary: EC底层RS算法复用与分级恢复
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:domain/core-read-replica-pick
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 纠删底层编解码、内核版本兼容、分级恢复场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 raid_gen/raid_rec 在仓库中存在"
- name: constraints
  desc: 算法复用前提
  constraint: 见正文
  testable_signal: "通读正文三段，确认复用内核库、冗余上限、分级恢复三条在引用代码中有对应实现"
---

# EC 底层 RS 算法复用与分级恢复

沉淀自 T0542 补充（用户下令补充 EC 算法本体）。对照 bcachefs
`fs/data/ec/io.c:20-110`。本节点只讲底层编解码算法，不讲条带
生命期与修复流程（见 ec-repair 节点）。

## 背景

bcachefs 不自研 RS 数学，复用内核 raid 库，自写部分只做分级调度
与版本兼容。算法正确性由内核保证，bcachefs 保证调用正确。

## 核心概念

1. **复用内核库加版本垫片**：XOR 与 syndrome 调内核 `raid/pq.h`、
   `raid/xor.h`；7.1 改名 xor_blocks→xor_gen、7.2 改 raid6 接口，
   自写 shim 抹平，调用方版本无关（`io.c:20-54`）。
2. **生成分两档**：1 parity 用 raid5 算法，2 parity 加 raid6
   syndrome；超 2 直接 BUG，上限 RAID6（`raid_gen:67`）。
3. **恢复按坏数分级**：0 坏直返；1 坏分数据坏与 parity 坏；2 坏分
   双数据、数据加 P、数据加 Q、双 parity 四分支；超 2 直接 BUG
   （`raid_rec:76`）。
4. **raid5 恢复三步**：换首、拷贝、异或（`raid5_recov:56`）。

## 违反后果

- 自研 RS：数学 bug 即静默 corrupt，且无人审计。
- 无版本垫片：新内核编译不过，老内核行为漂移。
- 无上限 BUG：超冗余静默错算，不如早炸。

## 复用指南

- 成熟算法优先复用内核库，自写只做调度与兼容。
- 恢复必须按坏数分级，超限直接 BUG 不猜。

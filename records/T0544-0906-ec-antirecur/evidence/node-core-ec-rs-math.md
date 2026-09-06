---
schema: pdca.asset/v1
id: ontology:domain/core-ec-rs-math
type: domain
layer: Knowledge
status: active
summary: RS纠删数学原理：异或P与syndrome Q
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-rs-algorithm
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 纠删数学原理理解、PQ 生成恢复语义场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文 P/Q 生成恢复规则与 io.c 调用对应"
- name: constraints
  desc: 数学子集前提
  constraint: 见正文
  testable_signal: "通读正文三节，确认只讲 bcachefs 用到的 P/Q 子集且上限明确"
---

# RS 纠删数学原理（bcachefs 子集）

沉淀自 T0543。对照 bcachefs `fs/data/ec/io.c:56-110`
（`raid5_recov`、`raid_gen`、`raid_rec`）。本节点只讲 bcachefs
用到的子集，不展开通用编码理论。

## 背景

bcachefs 只用两种冗余：1 parity（P）与 2 parity（P+Q），对应
RAID5 与 RAID6 子集。超 2 直接 BUG，不支持更高冗余。

## 核心概念

1. **P 即异或**：P = D1⊕D2⊕…⊕Dn。丢任一块，余块异或即恢复
   （`raid5_recov`：换首、拷贝、异或三步）。
2. **Q 即 syndrome**：伽罗瓦域上第二组线性方程，与 P 联立解
   二元一次方程组，可恢复任意 2 块（内核 `raid6_gen_syndrome`）。
3. **生成分档**：1 parity 只算 P，2 parity 算 P+Q（`raid_gen`）。
4. **恢复分级**：0 坏直返；1 坏分数据/parity；2 坏分双数据、
   数据加 P、数据加 Q、双 parity；超 2 直接 BUG（`raid_rec`）。

## 违反后果

- 自研数学：无人审计的域运算 bug 即静默 corrupt。
- 超限不炸：3 坏硬算得错解，不如早 BUG。

## 复用指南

- P 理解为异或即可，Q 理解为第二方程即可，不必深究域表。
- 上限写死，不支持即 BUG，不猜。

## 实际问题与修复

1. **内核改名致编译失败**：7.2 重命名 raid6 公共接口，旧名调用编译不过（`a03937a2a`）。修复：shim 宏映射新名到旧 API，调用方版本无关。防复发：条件编译隔离版本差异，新版直调旧版垫片。

---
schema: pdca.asset/v1
id: ontology:domain/core-ec-stripe-geometry
type: domain
layer: Knowledge
status: active
summary: 条带几何结构：变长段与拓宽计数
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
  desc: 条带磁盘结构解析、拓宽计数理解场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文结构字段与 format.h 对应"
- name: constraints
  desc: 结构解析前提
  constraint: 见正文
  testable_signal: "通读正文三节，确认字段语义、变长顺序、拓宽饱和三条在引用代码中有对应"
---

# 条带几何结构

沉淀自 T0543。对照 bcachefs `fs/data/ec/format.h`
（`struct bch_stripe`）。

## 背景

条带键是变长结构，一次读出全部几何。解析顺序错即读错指针。

## 核心概念

1. **固定头**：扇区数、算法 4 位、待重整标志、拓宽计数 3 位、
   总块数、冗余数、校验粒度与类型、盘标签。
2. **变长三段**：指针数组、校验二维数组（按粒度分片）、每块扇
   计数组。顺序固定，作者自注校验应垫后（XXX 注释）。
3. **拓宽计数**：3 位饱和 0-7，记本条在当前更宽几何下可增数据
   块数；写者须钳制。以读写成员视图为准，瞬时上下线不触发全
   盘重写（`bch2_disk_label_ec_rw_member_devs`）。

## 违反后果

- 顺序读错：指针校验块错位，静默 corrupt。
- 拓宽不钳制：3 位溢出回绕，几何错乱。

## 复用指南

- 变长结构解析顺序写死，XXX 注释即技术债标记。
- 饱和计数必须钳制，写者负责。

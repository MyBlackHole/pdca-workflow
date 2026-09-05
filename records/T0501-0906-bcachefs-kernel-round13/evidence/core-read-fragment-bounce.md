---
schema: pdca.asset/v1
id: ontology:domain/core-read-fragment-bounce
type: domain
layer: Knowledge
status: active
summary: 读片段浅继承 + 弹跳全读置位
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-read-promote-tiering
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 读 bio 片段拆分、弹跳缓冲、全读标志场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/data/read.h 在仓库中存在且含 rbio_init_fragment 定义"
- name: constraints
  desc: 片段继承前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认浅继承范围、置位条件两条前提在引用代码中有对应实现"
---

# 读片段浅继承与弹跳置位

沉淀自 T0501（内核第十三轮）。对照 bcachefs `fs/data/read.h`、
`fs/data/read.c`。

## 核心概念

1. **片段浅继承**：仅继承上下文选项失败错，新建分裂标志，
   清零其余，不继承弹跳与向量由分配回填
   （`rbio_init_fragment`）。
2. **弹跳全读置位**：数据更新强制全读；压缩校验失配、加密映
   射、必弹则弹跳加全读；提升按三条件算全读回写标志；非全
   读裁剪校验为切片（`__bch2_read_extent`、`promote_alloc`）。
3. **与既有节点边界**：提升节点管分层决策，本节点管片段继承
   与缓冲标志。

## 复用指南

- 片段拆分必须浅继承加显式回填，禁止深拷贝全部状态。
- 缓冲标志必须按条件置位，禁止一律弹跳。

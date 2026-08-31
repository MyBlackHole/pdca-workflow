---
schema: pdca.asset/v1
id: ontology:domain/core-device-bucket-geometry-pointer-contract
type: domain
layer: Knowledge
status: active
summary: 设备 bucket geometry 与 physical pointer 合约
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
  testable_signal: "检查本文件 device-bucket-geometry-pointer-contract 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 设备 bucket geometry 与 physical pointer 合约

physical pointer 的 bucket 归属必须从持久化 members-v2 geometry 得出：

`bucket = ptr.offset / member.bucket_size`，
`bucket_offset = ptr.offset % member.bucket_size`，
`bucket_position = (ptr.dev, bucket)`。

offset 不能直接作为 bucket。有效 mapping 的前置是 member record 存在且 alive、device
online、bucket size 非零，且 `first_bucket <= bucket < nbuckets`；pointer generation 还必须
与 alloc generation 相容。插入无效 pointer 不得创建派生 alloc/backpointer 状态。

members-v2 已是单一格式持久化 geometry 的权威来源。recovery 必须先验证、载入 members
并建立 online-device state，随后才 replay/scan physical pointers。bucket mapping 本身不
包含 allocator、LRU、discard、GC 或 stripe 策略。

来源：T0184，`records/T0184-0802-device-bucket-geometry-contract/conclusion.md`。

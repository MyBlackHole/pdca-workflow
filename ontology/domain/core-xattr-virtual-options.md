---
schema: pdca.asset/v1
id: ontology:domain/core-xattr-virtual-options
type: domain
layer: Knowledge
status: active
summary: xattr虚拟选项双命名空间 + 哈希描述符复用
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-vfs-namespace-operations
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: inode 级选项经 xattr 暴露、生效视图只读场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/fs/xattr.c 在仓库中存在且含 bch2_xattr_hash_desc 定义"
- name: constraints
  desc: 虚拟选项前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认哈希复用、继承偏置、生效只读三条前提在引用代码中有对应实现"
---

# xattr 虚拟选项双命名空间

沉淀自 T0498（内核第十轮）。对照 bcachefs `fs/fs/xattr.c`。

## 核心概念

1. **哈希描述符复用 str_hash**：类型加名散列做 xattr 哈希表
   （`bch2_xattr_hash_desc`）。
2. **双命名空间**：可写命名空间加偏置继承，只读命名空间为
   生效视图，写操作空实现（`bcachefs_effective`）。
3. **与既有节点边界**：选项表节点管全局挂载选项，本节点管
   inode 级选项的 xattr 暴露。

## 复用指南

- 分级选项用命名空间隔离可写与生效视图，禁止同名双义。
- 哈希复用已有算法，禁止为 xattr 单开哈希。

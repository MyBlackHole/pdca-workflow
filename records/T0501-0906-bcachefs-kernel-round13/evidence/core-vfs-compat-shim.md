---
schema: pdca.asset/v1
id: ontology:domain/core-vfs-compat-shim
type: domain
layer: Knowledge
status: active
summary: 跨内核VFS拆除路径双分支垫片
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
  desc: 跨内核版本 VFS 接口兼容、拆除路径适配场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/vfs/ioctl.c 在仓库中存在且含 start_removing_user_path_at 定义"
- name: constraints
  desc: 垫片前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认版本分支、写者配对两条前提在引用代码中有对应实现"
---

# 跨内核 VFS 拆除垫片

沉淀自 T0501（内核第十三轮）。对照 bcachefs `fs/vfs/ioctl.c`。

## 核心概念

1. **双分支垫片**：适配新旧内核拆除接口，处理写者计数与父目
   录重验（`start_removing_user_path_at`、
   `bch2_fs_file_ioctl`）。
2. **与既有节点边界**：命名空间节点管操作语义，本节点管版本
   兼容垫片。

## 复用指南

- 跨版本接口必须双分支垫片，禁止单分支假设。
- 写者计数与重验必须配对，禁止半截适配。

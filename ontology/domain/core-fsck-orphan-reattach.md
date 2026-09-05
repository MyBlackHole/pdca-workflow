---
schema: pdca.asset/v1
id: ontology:domain/core-fsck-orphan-reattach
type: domain
layer: Knowledge
status: active
summary: 失亲inode重挂 + 反向指针摘除 + 计数重建
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-fsck-autofix-graded-self-healing
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 文件系统检查失亲节点恢复、链接计数重建场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/fs/check_dir_structure.c 在仓库中存在且含 reattach_subvol 定义"
- name: constraints
  desc: 重挂前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认摘除先行、重挂计数两条前提在引用代码中有对应实现"
---

# 失亲节点重挂恢复

沉淀自 T0501（内核第十三轮）。对照 bcachefs
`fs/fs/check_dir_structure.c`、`fs/fs/check.c`、
`fs/fs/check_nlinks.c`、`fs/fs/check_extents.c`。

## 核心概念

1. **摘除后重挂**：失亲节点先摘反向指针，再挂回失物目录
   （`remove_backpointer`、`reattach_subvol`）。
2. **计数重建**：链接数重计数，extent 引用校验
   （`bch2_check_nlinks`、`bch2_check_extents`、
   `bch2_reattach_inode`）。
3. **与既有节点边界**：自愈分级节点管分级调度，本节点管失亲
   重挂执行。

## 复用指南

- 失亲恢复必须先摘后挂，禁止带旧指针重挂。
- 计数必须重建校验，禁止信任原值。

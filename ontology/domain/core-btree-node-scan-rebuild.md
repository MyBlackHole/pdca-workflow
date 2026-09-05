---
schema: pdca.asset/v1
id: ontology:domain/core-btree-node-scan-rebuild
type: domain
layer: Knowledge
status: active
summary: btree根丢失时裸盘扫描重建与副本归并
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-btree-gc-mark-sweep
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 超块树根丢失、根指针不可信时的暴力扫描恢复场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/btree/node_scan.c 在仓库中存在且含 bch2_scan_for_btree_nodes 定义"
- name: constraints
  desc: 扫描重建前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认不依赖超块、副本归并、覆盖裁剪三条前提在引用代码中有对应实现"
---

# btree裸盘扫描重建

沉淀自 T0497（内核第九轮，二轮复核）。对照 bcachefs
`fs/btree/node_scan.c`。

## 核心概念

1. **不依赖超块的暴力数据源**：根丢失时按 cookie 归并副本，
   最小堆裁剪覆盖，Eytzinger 二分定位
   （`bch2_scan_for_btree_nodes`、`handle_overwrites`、
   `try_read_btree_node`）。
2. **与既有节点边界**：GC 清扫假设树可用，journal 恢复假设
   日志可用，本节点是两者皆不可用时的最后数据源。

## 复用指南

- 根丢失恢复必须有不依赖任何元数据的扫描路径，禁止假设
  超块永远可读。
- 多副本归并用堆裁剪覆盖，禁止首个命中即信。

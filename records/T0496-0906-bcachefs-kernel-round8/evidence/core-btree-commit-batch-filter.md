---
schema: pdca.asset/v1
id: ontology:domain/core-btree-commit-batch-filter
type: domain
layer: Knowledge
status: active
summary: 提交同叶批处理 + 空洞合成 + 快照过滤写位缓存
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-btree-transaction-memory-io
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 事务提交写锁段合并、空洞读合成、快照读过滤场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/btree/commit.c 在仓库中存在且含 bch2_trans_commit_write_locked 定义"
- name: constraints
  desc: 批处理过滤前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认同叶去重、合成非搜索、过滤不误写三条前提在引用代码中有对应实现"
---

# btree提交批处理与读过滤

沉淀自 T0496（内核第八轮，全扫复核）。对照 bcachefs
`fs/btree/commit.c`、`fs/btree/iter.c`。

## 核心概念

1. **同叶批处理**：写锁段内同叶更新去重加锁，按叶累加持写锁
   预检容量，防他线程改空间（`bch2_trans_commit_write_locked`、
   `same_leaf_as_prev`、`btree_key_can_insert`）。
2. **空洞现场合成**：slot 模式无覆盖时伪造 hole 键，非搜索而
   是合成（`bch2_btree_iter_peek_slot`）。
3. **快照过滤写位缓存**：读过滤中为跳过无关分支另建更新路径
   缓存写位置，避免误写；含 whiteout/祖先状态机
   （`btree_iter_filter_snapshots`）。
4. **与既有节点边界**：事务内存节点管 bump 分配，搜索编码节点
   管定位编解码，本节点管提交段合并与读过滤。

## 复用指南

- 提交写锁段必须同键合并 + 容量预检，禁止逐键加锁。
- 无覆盖读用合成键而非报错，合成必须标明非持久。
- 读过滤跳过分支时缓存写位置，禁止误写跳过区。

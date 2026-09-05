---
schema: pdca.asset/v1
id: ontology:domain/core-btree-node-cache-statemachine
type: domain
layer: Knowledge
status: active
summary: btree节点缓存五态机 + 物理指针哈希 + 食人逐出
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-interior-gc-update-gate
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 内存 btree 节点缓存管理、逐出与复用场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/btree/cache.c 在仓库中存在且含 bch2_btree_node_evict 定义"
- name: constraints
  desc: 缓存迁移前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认单原语迁移、逐出顺序两条前提在引用代码中有对应实现"
---

# btree 节点缓存五态机

沉淀自 T0499（内核第十一轮）。对照 bcachefs `fs/btree/cache.c`。

## 核心概念

1. **五态单原语迁移**：内存节点按物理指针哈希表管理，以
   NONE/FREED/FREEABLE/CLEAN/DIRTY 五态单原语迁移
   （`bch2_btree_node_transition_state`）。
2. **收缩与食人逐出**：shrinker 与食人任务逐出，cannibal 串行
   拆借缓存（`bch2_btree_node_evict`）。
3. **与既有节点边界**：GC 清扫管内容回收，扫描重建管启动扫描，
   键缓存管键，本节点管内存节点生命周期。

## 复用指南

- 内存缓存状态机必须单原语迁移，禁止多锁拼凑。
- 逐出必须分级（收缩先行、食人兜底），禁止一刀切。

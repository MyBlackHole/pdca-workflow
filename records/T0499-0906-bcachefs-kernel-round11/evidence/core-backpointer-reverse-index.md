---
schema: pdca.asset/v1
id: ontology:domain/core-backpointer-reverse-index
type: domain
layer: Knowledge
status: active
summary: backpointer独立btree逆查 + 匹配校验 + 写缓冲旁路
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-move-unified-relocation-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 物理位置反查属主、迁移定位、校验场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/alloc/backpointers.c 在仓库中存在且含 bch2_backpointer_get_key 定义"
- name: constraints
  desc: 逆查前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认独立成树、匹配校验两条前提在引用代码中有对应实现"
---

# backpointer 逆向索引

沉淀自 T0499（内核第十一轮）。对照 bcachefs
`fs/alloc/backpointers.c`。

## 核心概念

1. **独立 btree 逆查**：物理位置反查属主键，与正向 extent 树
   分离（`bch2_backpointer_get_key`）。
2. **匹配校验**：逆查结果与正向比对，不一致即错
   （`extent_matches_bp`、`bch2_backpointer_validate`）。
3. **写缓冲旁路开关**：特定路径旁路写缓冲保证读到最新
   逆查。
4. **与既有节点边界**：触发器分流是通用分发，本节点是独立逆
   查树；move 引擎用逆查定位待迁数据。

## 复用指南

- 物理到逻辑必须有独立逆查，禁止全表扫描。
- 逆查结果必须与正向比对校验，禁止单边信任。

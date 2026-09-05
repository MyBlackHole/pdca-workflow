---
schema: pdca.asset/v1
id: ontology:domain/core-str-hash-seed-callers
type: domain
layer: Knowledge
status: active
summary: str_hash种子派生兼容 + 调用面差异
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-str-hash-multialgo
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 哈希种子派生、目录与 xattr 调用差异场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/fs/str_hash.c 在仓库中存在且含 bch2_hash_info_init 定义"
- name: constraints
  desc: 种子调用前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认旧版派生、调用面差异两条前提在引用代码中有对应实现"
---

# str_hash 种子派生与调用差异

沉淀自 T0501（内核第十三轮）。对照 bcachefs
`fs/fs/str_hash.c`、`fs/fs/dirent.c`、`fs/fs/xattr.c`。

## 核心概念

1. **种子派生兼容分支**：直填种子，仅旧版对种子做哈希再截断
   派生；大小写关闭报错；种子源头随机生成
   （`__bch2_hash_info_init`）。
2. **调用面差异**：目录对折叠名哈希且保留点位，xattr 对类型
   加名哈希；描述符区分树与键类型
   （`bch2_dirent_hash`、`bch2_xattr_hash`）。
3. **与既有节点边界**：多算法节点管算法选型，本节点管种子派
   生与调用差异。

## 复用指南

- 旧版兼容派生必须隔离分支，禁止污染新版路径。
- 不同调用面哈希输入必须显式区分，禁止复用同一输入。

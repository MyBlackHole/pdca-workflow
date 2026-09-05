---
schema: pdca.asset/v1
id: ontology:domain/core-bio-iov-bridge
type: domain
layer: Knowledge
status: active
summary: bio与iov迭代器钉页桥接 + 调用栈暂存
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-dio-write-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 块层 bio 与用户 iov 迭代器桥接、页钉住场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/vendor/bio_iov_iter.c 在仓库中存在且含 bch2_bio_iov_iter_get_pages 定义"
- name: constraints
  desc: 桥接前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认页钉住、栈暂存两条前提在引用代码中有对应实现"
---

# bio-iov 钉页桥接

沉淀自 T0500（内核第十二轮）。对照 bcachefs
`fs/vendor/bio_iov_iter.c`。

## 核心概念

1. **钉页桥接**：bio 与 iov_iter 间页获取桥接，钉住用户页供
   DMA（`bch2_bio_iov_iter_get_pages`）。
2. **调用栈暂存**：DIO 写侧拷贝 iov 防调用栈失效
   （`bch2_dio_write_copy_iov`）。
3. **与既有节点边界**：DIO 引擎节点管读写流程，本节点管底层
   页桥接原语。

## 复用指南

- 跨层页传递必须显式钉住，禁止裸指针跨层。
- 调用栈 iov 必须暂存，禁止异步引用栈内存。

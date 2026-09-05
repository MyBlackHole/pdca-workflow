---
schema: pdca.asset/v1
id: ontology:domain/core-journal-write-assembly
type: domain
layer: Knowledge
status: active
summary: jset动态组装 + 写校验分叉 + 空预留压缩
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-journal-seq-blacklist-pin-reclaim
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 日志提交写组装、版本兼容校验、空预留回收场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/journal/write.c 在仓库中存在且含 bch2_journal_write_prep 定义"
- name: constraints
  desc: 组装校验前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认空丢弃、根补全、分支先验三条前提在引用代码中有对应实现"
---

# journal写组装流水线

沉淀自 T0496（内核第八轮，全扫复核）。对照 bcachefs
`fs/journal/write.c`。

## 核心概念

1. **写前整理**：遍历 jset 丢弃空预留，翻转写缓冲键并落盘，
   再补齐缺失树根、追加时间与超块尾缀，断言防超预留
   （`bch2_journal_write_prep`）。
2. **校验分叉门**：按校验类型是否加密与版本新旧决定先验分支；
   组装 magic/version/nonce/csum（`bch2_journal_write_checksum`）。
3. **与既有节点边界**：空间记账节点管预留配额，恢复三区管读
   恢复，本节点管提交后写组装，三段各司其职。

## 复用指南

- 日志提交分预留、组装、校验三段，禁止一锅烩。
- 空预留在组装段丢弃，禁止占用落盘空间。
- 版本兼容校验必须分支先验，禁止先组装后验证。

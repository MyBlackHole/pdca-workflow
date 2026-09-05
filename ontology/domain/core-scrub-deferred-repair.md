---
schema: pdca.asset/v1
id: ontology:domain/core-scrub-deferred-repair
type: domain
layer: Knowledge
status: active
summary: scrub只记不修 + journal异步修 + 两次连续好停
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 全盘 scrub 检查、延迟批量修复、误报抑制场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/data/move.c 在仓库中存在且含 bch2_scrub_journal 定义"
- name: constraints
  desc: 延迟修复前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认只记不修、倒序验证、连续好停三条前提在引用代码中有对应实现"
---

# scrub 只记不修与异步修复

沉淀自 T0496（内核第八轮，全扫复核）。对照 bcachefs
`fs/data/update.c`、`fs/data/move.c`。

## 核心概念

1. **只记不修**：读后仅入修复数组，不即时修
   （`bch2_data_update_read_done`）。
2. **journal 异步修**：按落盘区间倒序验证，两次连续好即停；
   修复经掩码重映射转自愈重写（`bch2_scrub_journal`、
   `scrub_journal_repair_one`）。
3. **与既有节点边界**：EC 修复节点管单条带即时修，本节点管全
   盘 scrub 延迟批量修。

## 复用指南

- scrub 必须只记不修，修复走异步批量，禁止读路径即时修。
- 修复前倒序验证，两次连续好即停，防抖动误修。

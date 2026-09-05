---
schema: pdca.asset/v1
id: ontology:domain/core-move-unified-relocation-engine
type: domain
layer: Knowledge
status: active
summary: move 统一搬迁引擎 + 谓词注入 + copygc 单一判据
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-open-bucket-lifecycle-and-device-rw
  - ontology:domain/core-device-bucket-geometry-pointer-contract
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 数据搬迁多策略共存（清运/疏散/ scrub/均衡/修复）场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/data/move.c 在仓库中存在且含 bch2_move_extent_pred 定义"
- name: constraints
  desc: 引擎复用的前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认谓词纯决策、EC 整搬、判据单一三条前提在引用代码中有对应实现"
---

# move 统一搬迁引擎 + 谓词注入

沉淀自 T0490（纵深分析），来源 T0488 报告与数据面深挖。对照
bcachefs `fs/data/move.c`、`fs/data/move.h:92`、
`fs/data/copygc.c`、`fs/data/reconcile/work.c`。

## 核心概念

1. **策略与 IO 机制解耦**：`move_pred_fn` 只决策"搬/跳"与
   `ptrs_kill/target`；`bch2_move_extent_pred → bch2_move_extent →
   __bch2_move_extent → data_update_init + __bch2_read_extent`
   异步管线全共享。copygc/疏散/scrub/reconcile/EC 整搬同引擎
   （`move.c:226,418,902`）。
2. **EC 整搬不打碎 stripe**：stripe 须整条搬迁，碎 stripe 不重写
   活数据（`may_reuse_stripe/get_old_stripe`）。
3. **调度契约收敛为单一纯函数**：`can_make_progress =
   wait_amount <= 0`，分配器 blocked→kick/wait/bail 与建 device
   list 用同一判据，永不"等不来的 run/错过该等的 run"
   （`copygc.c:555-562`）。碎片 LRU 免全盘扫；`dev_leaving`
   计入 free 防搬离中误触发；EC/普通 copygc 二选一
   （`should_do_ec_copygc`）。

## 复用指南

- 多搬迁策略：一个引擎 + 多谓词，禁止每策略一套 IO 管线。
- 调度契约必须是纯函数，多方共用同一判据；注释写明"与 XX
  同判据"。
- 整单元搬迁（stripe/桶）优先于零散搬迁，保持大单元完整性。

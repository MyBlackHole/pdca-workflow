---
schema: pdca.asset/v1
id: ontology:domain/core-format-compat-stable-evolution
type: domain
layer: Knowledge
status: active
summary: FEATURE/COMPAT 双位 + stable 映射 + X 宏防漂移的格式演进
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 磁盘格式向前兼容、内存枚举与磁盘位隔离、多后端选项一致性场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/bcachefs_format.h 在仓库中存在且含 BCH_COMPAT 定义"
- name: constraints
  desc: 演进机制的启用前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认拒挂条件、映射表完整性、生成一致性三条前提在引用代码中有对应实现"
---

# FEATURE/COMPAT 双位 + stable 映射 + X 宏防漂移

沉淀自 T0488（confirmed），来源
`records/T0488-0905-bcachefs-strengths/`。对照 bcachefs
`fs/bcachefs_format.h`、`fs/init/passes.c`、`fs/opts.c`、
`fs/errcode.h`。

## 核心概念

1. **FEATURE/COMPAT 双位体系**：新特性显式位 + 兼容位门控
   （如 `BCH_COMPAT_stripe_frag_accounting(5)`）；老内核见不识
   别位拒挂而非 corrupt（`bcachefs_format.h:1379-1411`）。
   升级/降级表驱动：按版本声明所需 pass 与静默错误，写前校验
   版本（`sb/downgrade.c`）。
2. **stable 映射隔离磁盘格式**：内存 `enum bch_recovery_pass`
   随意增删，磁盘只存 stable 位，双向 u8 表重映射
   （`passes.c:44-70`）。内存演进永不污染磁盘位。
3. **X 宏防多后端漂移**：选项表由 `BCH_OPTS()` 统一生成，
   mount/sysfs/sb 三后端同源，synonym 兼容旧名
   （`opts.c:282-480`）；errcode 一宏双表 + codegen 自动生成
   Rust 绑定（`errcode.h:63`、`codegen.rs:262`）；未知码统一
   兜底不崩（`errcode.c:21-109`）。

## 复用指南

- 磁盘格式演进三件套：特性位声明 + 兼容位门控 + 老版本拒挂，
  缺一即静默 corrupt。
- 内存枚举与磁盘位之间必须有显式映射层，禁止直接复用同一
  枚举值。
- 多后端消费同一声明时用代码生成而非手写同步；未知输入的
  默认行为必须是拒绝或兜底，绝不能是误判成功。

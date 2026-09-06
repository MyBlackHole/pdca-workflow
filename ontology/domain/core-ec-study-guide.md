---
schema: pdca.asset/v1
id: ontology:domain/core-ec-study-guide
type: domain
layer: Knowledge
status: active
summary: EC纠删专题学习指南与节点导航
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-ec-repair-evacuate-retry
  - ontology:domain/core-read-replica-pick
  - ontology:pattern/unified-relocation-engine
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: EC 纠删机制系统学习、节点导航场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 3 个 EC 相关节点 id 全部存在"
- name: constraints
  desc: 学习顺序前提
  constraint: 见正文
  testable_signal: "通读正文学习路径节，确认三阶段顺序与每阶段节点映射在正文中明确"
---

# EC 纠删专题学习指南

沉淀自 T0516（EC 纠删专题学习报告），来源
`records/T0516-0906-study-ec/`。对照 bcachefs `fs/data/ec/`。

## 背景

EC 知识分散在修复、读优选、搬迁引擎节点与 4600 行源码中，
初学者无入口。本节点做导航聚合，不重复机制内容。

## 学习路径（三阶段）

1. **路线语义**：先读 T0516 报告一二节（后台整桶、无写洞），
   再读 create.c 头 DOC_LATEX。
2. **生命期与修复**：`core-ec-repair-evacuate-retry`（疏散重试）
   与 `core-read-replica-pick`（读优选），对照 create.c 修复与
   io.c 重建。读重建执行细节见 T0534 报告（三重检查、分阶段证明、
   独立记错、两次校验、分级限流）：快慢分离，锁内靠锁 IO 后靠钉。
3. **搬迁协同**：`pattern/unified-relocation-engine`（整搬），
   理解 copygc 与 EC 的边界。

## 八条启示速查

见 T0516 学习报告第八节：后台整桶、不可变加原子、整体生命期、
显式三态、先验后算、阈值显式、无害化并发、降级静默。

## 复用指南

- 学 EC 先定路线（前台切分 vs 后台整桶），路线错全错。
- 重建与修复分开学：重建是读路径，修复是后台任务。

详见 T0535 代码级精讲扩充版报告（`records/T0535-0906-detail-batch1/`，含5项与现源码差异纠偏）。

---
schema: pdca.asset/v1
id: ontology:concept/pdca
type: concept
layer: Knowledge
summary: PDCA 管理模型元本体根概念
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-10
owl_versionIRI: http://pdca.local/ontology/pdca/1.0.3
docType: Concept
tags: [pdca, meta-ontology]
---
# pdca

PDCA（Plan-Do-Check-Act，又称 **Deming Cycle** / **Shewhart Cycle**）是本工作流采用的管理模型元本体根概念。

- **定义**：基于科学方法的四阶段持续改进循环。起源上由 Walter Shewhart 提出统计过程控制思想，经 W. Edwards Deming 在日本战后（1950 年代）推广而广为人知，故又称 Deming Cycle。
- **经典四阶段**（方法论本身，见 `ontology:concept/pdca-phase`）：**plan（计划）→ do（执行）→ check（检查）→ act（处理/标准化）**。注意：**archive 不是 PDCA 方法论阶段**，它是本工作流单任务生命周期的运维扩展（见 `ontology:entity/phase-archive`）。
- **持续改进循环**：act 之后应回到 plan 开启新一轮（"a circle has no end"），由 `ontology:concept/pdca-continuous-improvement` 承载；本工作流把单任务建模为终止于 `archive` 的流水线，但方法论上的"下一轮 plan"对应于新建任务或任务内新迭代。
- **术语注记**：Deming 本人更偏好 **PDSA**（Plan-Do-Study-Act），Study 强调深度学习；PDCA 的 Check 为日方简化后的通俗变体，本工作流沿用 PDCA 命名。
- **子概念（本元本体的构成）**：
  - 阶段：`pdca-phase`（四阶段元概念）、`phase-plan` / `phase-do` / `phase-check` / `phase-act` / `phase-archive`（实体节点）。
  - 转换：`pdca-transition`（合法 phase→phase 边元概念）、`transition-*.md` 实体节点。
  - 门禁：`pdca-gate`、`pdca-gate-do`、`pdca-ontology-ready`（do 准入）。
  - 证据与判定：`pdca-evidence`、`pdca-verdict`、`pdca-acceptance-criterion`。
  - 载体：`pdca-task`（一个完整 PDCA 周期的载体，由 `task.json` 跟踪）。
  - 循环：`pdca-continuous-improvement`。
- **控制与执行消费**：`scripts/ontology_reason.py` 读取上述节点驱动阶段转换/准入/证据识别；`scripts/pdca_context.py` 在各阶段入口实时输出对应元本体知识（见 `ontology/README.md`）。

## 设计核心：本体树驱动（B→A→C）

- **本体是什么**：本体是知识的最小可验证单元，即一个 `ontology/<type>/<slug>.md` 资产：有全局唯一 id、有类型（concept/entity/pattern/process/domain）、有关系边（specializes/part_of/relates_to/composed_of）、有可验证信号（attributes/testable_signal）。分层验证：普通本体四件套显式具备；根本体（无父节点，如本节点）的验证信号是其子树的整体校验（`ontology-validate` 通过 + 孤岛检查为零）。
- **本体树**：一个任务目标就是本体的实现；实体由一个或多个本体构成，本体又由一到多个本体构成——所以是棵树。树中每个节点都须满足叶标准才停：独立单职责、可直接实现、无需再拆。
- **B（建树，走知识产出路径）**：产出或者更新本体树；每个本体发起独立的 B 子任务（子 agent），递归至每节点满足叶标准即停。方向为根→叶：从根实体经 `composed_of` 逐层拆至叶子，100%覆盖。B 必有本体更新（新建或修订，不接受零更新）。
- **A（按树实现，走代码变更路径）**：对 B 产出的本体树进行实现，每个本体发起一个子任务（子 agent）；严格一对一：一个本体恰一实现，一实现恰属一本体；共享能力须明确唯一主归属本体，其余使用者记跨本体调用（调用不占归属）。细节不管，但细节必有主：实现内部的每个逻辑单元（函数/分支/拒绝码）必须回链到其归属本体定义的某一要素（职责/关系/验收/testable），无本体依据的细节不得存在。方向为叶→根：叶实现先行并行，根聚合随后（batches [[叶],[根]]）。
- **C（逐项校验，走评审校验路径）**：A 的产出内容都是根据本体进行的，与 B 的产出本体树一一对应（每本体恰一实现）；逐项校验是否遵循本体。
- **路径映射**：B→`flow-do` 路径 B（知识产出），A→路径 A（代码变更），C→路径 C（评审校验）。
- **方向总述**：B 场景的本体树是从根到叶子创建的，A 场景的本体树是从叶到根开发的。
- **闭环语义**：PDCA 是单个本体的执行闭环；B、A、C 是知识产出、代码变更、评审校验三类大任务的抽象；B/A/C 各阶段的每本体子任务都跑完整循环。


---
schema: pdca.asset/v1
id: ontology:concept/pdca
type: concept
layer: Knowledge
summary: PDCA 管理模型元本体根概念
status: active
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
- **控制与执行消费**：`scripts/ontology_reason.py` 读取上述节点驱动阶段转换/准入/证据识别；`scripts/pdca_context.py` 在各阶段入口实时输出对应元本体知识（见 `docs/ONTOLOGY_GUIDE.md`）。


# T0405 设计草案（P2 终稿候选 — 重量化门禁 + Phase0 内自举）

## 目标
将本体提升为 PDCA 流程一等公民，且**门禁 / 转换逻辑全本体化（重量）**：所有阶段判定由 PDCA 元本体驱动的语义推理得出，而非硬编码。两层本体均融入流程。

## 两层本体
1. **PDCA 元本体**：描述 PDCA 自身（`pdca-task` / `pdca-phase` / `pdca-evidence` / `pdca-verdict` / `pdca-transition` / `pdca-gate` 等）及关系——如 `pdca-transition` 定义合法 phase→phase、`pdca-gate` 定义某阶段准入条件、`evidence` 类型与 `AC` 的满足关系。落在 `ontology/`。
2. **领域本体**：每任务 Do 前构建的专属领域实体 / 关系片段（强约束）。

## 自举（Phase 0，留在 T0405 内，不拆子任务）
- T0405 的 Do 阶段第一步 bootstrap PDCA 元本体：创建 `pdca-*` 概念节点 + 关系，落入 `ontology/`。
- 该步骤豁免"先有 PDCA 本体"前置（否则死锁）；其产出即元本体本身。
- 引导期 `transition-phase.py` 以硬编码最小核心（plan/do/check/act/archive）回退运行，元本体就位后切换为本体驱动。

## 门禁全本体化（重量，本任务核心）
- 新增**本体推理层**（模块 / 脚本）：读取 `ontology/` 的 `pdca-*` 节点，回答：
  - 某 phase→phase 转换是否合法（依据 `pdca-transition` 关系）。
  - 某阶段准入是否满足（依据 `pdca-gate` 节点描述的必要条件，如 do 准入需 `ontology-ready`）。
  - evidence 类型是否满足某 AC（依据 evidence 与 AC 的关系）。
- `transition-phase.py` / flow SKILL 改为调用本体推理层，不再硬编码枚举。
- 复用 `ontology-validate` 作为领域 / 元本体的结构校验。

## 四阶段嵌入（分阶段）
- **Phase 0**：bootstrap PDCA 元本体 + 本体推理层最小可用。
- **Phase 1**：plan 加"本体构建"步骤（对齐元本体 + 抽取领域片段）；do 前置 `ontology-ready` 关卡（由 `pdca-gate` 定义，本体驱动）；门禁全本体化落地。
- **Phase 2（后续迭代）**：check 对照两层本体；act 沉淀领域实体回 `ontology/`（复用 T0404 闭环）。

## ADR
`ADR-0032（ontology-driven-pdca）`：两层本体、自举豁免、门禁全本体化、分阶段。涉及 `task.schema.json` 与 transition 逻辑本体化（严格 schema 冻结变更，需评审）。

## 取舍与风险
- 重量化门禁长期收益高（流程规则可演进、可解释），但实现面大：需本体推理层 + 改 `transition-phase.py` / flow SKILL + 可能的 schema 大改。
- 自举回退：元本体缺失时脚本硬编码回退，须与元本体同步。
- 分阶段降低风险：先元本体 + 推理层最小可用，再扩流程改造。
- 衔接 T0404：领域沉淀复用半自动归纳辅助 + 校验闸门。

## 验收构想（聚焦 Phase 0+1）
- AC-1：`ontology/` 落地 PDCA 元本体（`pdca-*` 节点 + 关系）。
- AC-2：本体推理层可回答转换合法性 / 阶段准入 / evidence–AC 满足。
- AC-3：`transition-phase.py` 改为调用推理层（不再硬编码枚举）。
- AC-4：`ontology-ready` 关卡由 `pdca-gate` 本体驱动，fixture 验证拦截 / 放行。
- AC-5：每任务 `meta.ontology_fragment` 强约束；plan 构建领域片段。
- AC-6：回归测试覆盖自举回退 + 门禁本体化。

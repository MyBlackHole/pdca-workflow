# ADR-0032: 本体驱动 PDCA（ontology-driven PDCA）

日期: 2026-08-29
状态: Accepted

## 背景

此前已完成知识库本体化（T0402 归档）与半自动归纳辅助（T0404 归档），但 PDCA 流程自身的门禁/转换逻辑仍散落在 `transition-phase.py` 与 `flow-*.md` 的硬编码枚举与文本约定中，规则不可机读、不可演进。用户要求：开发项目先构建本体，且 PDCA 自身也需一个本体（元本体），流程要引用它。

## 决策

将本体提升为 PDCA 流程一等公民，且**门禁/转换逻辑全本体化（重量）**：

1. **两层本体**：
   - **PDCA 元本体**：描述 PDCA 自身（`pdca-task` / `pdca-phase` / `pdca-evidence` / `pdca-verdict` / `pdca-transition` / `pdca-gate` / `pdca-ontology-ready` 等）及关系，落在 `ontology/`。
   - **领域本体**：每任务 Do 前构建的专属领域实体/关系片段（强约束）。
2. **自举（Phase 0）**：PDCA 元本体由首批任务（如 T0405）在 `ontology/` 下创建；该引导步骤豁免"先有 PDCA 本体"前置，其产出即元本体本身。元本体缺失时 `transition-phase.py` 回退硬编码最小核心（plan/do/check/act/archive），避免死锁。
3. **门禁全本体化**：新增 `scripts/ontology_reason.py` 推理层，读取 `pdca-*` 节点回答（a）phase→phase 转换合法性（依 `pdca-transition` 的 `composed_of`）；（b）阶段准入条件（依 `pdca-gate` / `pdca-ontology-ready`）；（c）evidence 类型识别（依 `pdca-evidence` 实例）。`transition-phase.py` 的转换合法性判定改为调用该推理层。
4. **ontology-ready 关卡**：`do` 阶段准入由元本体 `pdca-ontology-ready` 驱动，校验任务 `meta.ontology_fragment` 指向的领域片段存在且结构合法；自举任务经 `meta.ontology_exempt` 豁免。
5. **schema 变更**：`task.schema.json` 的 `meta` 增加 `ontology_fragment`（相对路径/可空）与 `ontology_exempt`（布尔），属严格 schema 冻结变更，经本 ADR 评审通过。

## 影响

- `transition-phase.py` 不再硬编码相邻阶段逻辑，改由元本体驱动；新增/调整阶段或转换只需改 `ontology/` 节点，无需动脚本。
- `meta.ontology_fragment` 成为开发类任务的强约束入口；引导任务（构建元本体者）豁免。
- 复用既有 `ontology-validate.py` 作为结构与引用校验闸门，不另造校验器。
- 风险：元本体与硬编码回退需保持同步；存量任务（T0402/T0404 等）本任务不强制迁移，留 Phase 2。
- 衔接 T0404：领域片段沉淀复用半自动归纳辅助与校验闸门。

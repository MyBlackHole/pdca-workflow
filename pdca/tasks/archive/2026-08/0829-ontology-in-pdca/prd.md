# T0405 PRD：本体驱动 PDCA 流程（ontology-driven PDCA）

## 1. 背景与痛点
- 当前 PDCA 门禁/转换逻辑散落在 `transition-phase.py` 与 `flow-*.md` 的硬编码枚举与文本约定中，规则不可机读、不可演进、难以解释。
- 此前已完成知识库本体化（T0402 归档）与半自动归纳辅助（T0404 归档），但流程本身未引用本体；用户要求：开发项目先构建本体、PDCA 自身也需本体且流程要引用它。

## 2. 目标
将本体提升为 PDCA 一等公民，且**门禁/转换逻辑全本体化（重量）**：阶段判定由 PDCA 元本体驱动的语义推理得出，而非硬编码。两层本体（PDCA 元本体 + 领域本体）融入 plan/do/check/act。

## 3. 范围
**本期（Phase 0 + Phase 1）包含**
- Phase 0：自举 PDCA 元本体（落在 `ontology/`）+ 本体推理层最小可用。
- Phase 1：plan 增加"本体构建"步骤；do 前置 `ontology-ready` 关卡由 `pdca-gate` 本体驱动；门禁/转换逻辑改读元本体。
- 每任务 `meta.ontology_fragment` 强约束（领域本体片段）。

**本任务不做（留 Phase 2）**
- check/act 阶段本体嵌入（对照本体验证关系图、领域实体沉淀回 `ontology/`）。
- 存量任务（T0402/T0404 等）批量迁移对齐元本体。

## 4. 交付物
1. `ontology/` 下 PDCA 元本体：`pdca-task` / `pdca-phase` / `pdca-evidence` / `pdca-verdict` / `pdca-transition` / `pdca-gate` 等概念节点 + 关系。
2. 本体推理层（`scripts/ontology_reason.py` 或并入 `ontology-validate`）：读取 `pdca-*` 节点，回答转换合法性 / 阶段准入 / evidence–AC 满足。
3. `transition-phase.py` 改为调用推理层（元本体缺失时硬编码最小核心回退）。
4. plan triage 的"本体构建"步骤与 do 前置 `ontology-ready` 关卡（由 `pdca-gate` 驱动）。
5. `task.schema.json` 增加 `meta.ontology_fragment`（严格 schema 冻结变更，需评审）。
6. `ADR-0032（ontology-driven-pdca）` 文档。
7. 回归测试：自举回退 + 门禁本体化拦截/放行 fixture。

## 验收标准
- [ ] AC-1：`ontology/` 落地 PDCA 元本体（`pdca-*` 节点 + 关系），`ontology-validate` 通过。
- [ ] AC-2：本体推理层可回答（a）phase→phase 转换合法性（依 `pdca-transition`）；（b）阶段准入（依 `pdca-gate`）；（c）evidence 类型满足某 AC（依 evidence–AC 关系）。
- [ ] AC-3：`transition-phase.py` 改为调用推理层；元本体缺失时回退硬编码核心，不报错死锁。
- [ ] AC-4：`ontology-ready` 关卡由 `pdca-gate` 本体驱动，fixture 验证：领域片段缺失/校验失败→拦截；齐备→放行。
- [ ] AC-5：每任务 `meta.ontology_fragment` 强约束；plan 步骤能构建/声明领域本体片段。
- [ ] AC-6：回归测试覆盖自举回退（`tests/test_ontology_reason.py` 或并入现有测试），CI 可跑。

## 6. 依赖
- T0404（已归档）：`scripts/ontology_induction.py` 半自动归纳辅助、`ontology-validate` 校验闸门——本任务复用其校验与候选生成能力。

## 7. 风险与缓解
- **自举死锁**：引导步骤豁免"先有 PDCA 本体"前置；脚本在元本体缺失时硬编码回退（须与元本体同步，缓解漂移）。
- **实现面大（重量门禁）**：分阶段，先元本体+推理层最小可用，再扩流程改造；每步有回归测试。
- **严格 schema 冻结**：`meta.ontology_fragment` 变更走 ADR-0032 + schema 评审。
- **存量兼容**：Phase 2 才处理，本期不破坏既有任务。

## 8. 测试策略
- 单元：推理层对 `pdca-transition` / `pdca-gate` 的判定（合法/非法转换、准入满足/不满足）。
- 集成：fixture 任务验证 `ontology-ready` 拦截/放行；`transition-phase.py` 在元本体缺失与就位两种态下均正常。
- 回归：并入 `tests/`，与 T0404 测试 coexistence。

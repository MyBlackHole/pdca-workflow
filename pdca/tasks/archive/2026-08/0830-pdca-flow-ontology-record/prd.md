# T0418 PDCA 流程本体化（0829 协调子流）

- 任务 ID：T0418
- 父任务：T0829（知识表达按本体论重构，提供 ontology-validate / ontology-check 机制）
- 依赖：T0829（机制）、T0417（task_identity 已锚定 pdca-task，流程实体可直接继承该锚定）
- 场景类型：documentation

## 背景与问题

PDCA 工作流本身是 PDCA 本体的实体，但当前：
1. 四个流程 `flows/flow-{plan,do,check,act}.md` **尚未成为本体实体**，仅以 SKILL 文档形式存在，无法挂接本体图谱、无法被关系树检索/复用。
2. 大量**外部 PDCA 实体的描述与决策记录**散落且冗余：
   - `knowledge/pdca-flow/`（16 文件：架构、CLI 行为、销毁清理安全、执行器适配边界、外部证据收集、外部项目注入、通用 AI 工作流内核、全局仓库配置、opencode tmux 适配、真实项目机制验证、真实使用效能审计、知识来源溯源、运行时转换协调、自优化回路、任务记录身份不变量、时间线完整性门禁）
   - `knowledge/pdca-workflow/`（6 文件：AI 友好确认、架构评审指标、ID 冲突修复、可证明技能增量、场景边界规则、源图文档校验）
   - `docs/adr/ADR-0032~0036`（本体驱动 PDCA 的决策记录）
   这些内容一旦本体化即成为"多余"，应迁移进本体作为唯一事实源。

父任务 T0829 已建立"完整本体 + 校验机制"，本任务为其**协调子流**，专门处理 PDCA 元工作流自身的本体化，复用既有机制、不重建。

## Seam 分析

### 测试接缝
- `scripts/ontology-validate.py`：复用 T0829 的校验器验证新建/迁移后的本体节点（`--all` 退出码 0、无悬空引用、无环）。

### 声明的测试接缝
- seam: tests/test_pdca_flow_ontology.py -> scripts/ontology-validate.py

## 设计概览

### Part 1 流程即本体实体
为四个流程各建一个本体流程实体：
- `ontology/process/flow-plan.md` / `flow-do.md` / `flow-check.md` / `flow-act.md`
- `type: process`，`specializes: [ontology:concept/process]`（与既有 `ontology:process/code-review-process` 模式一致：流程在知识图谱中是 process 的特化）。如需表达"流程本身即 PDCA 任务实例"，追加 `relates_to: [ontology:concept/pdca-task]`（T0417 的 `meta.ontology_anchor=pdca-task` 是任务管理的独立轴，不与本体 type/specializes 混用）
- `relations`：
  - `part_of: [ontology:concept/pdca]`（属 PDCA 周期）
  - `guides` / `relates_to`：对应 phase 实体（`phase-plan` 等）
  - `do` 流程额外 `relates_to: [ontology:concept/pdca-ontology-ready, ontology:concept/pdca-gate-do]`
- body：该流程的权威描述 + 关键决策（从 `knowledge/pdca-flow/` 与 ADR 沉淀）

### Part 2 pdca-flow 知识迁移
将 `knowledge/pdca-flow/` 16 个文件的描述与决策，按主题归入：
- 四个流程实体本身（与其直接相关的描述）
- 必要的 supporting 节点（如 `ontology:concept/executor-adapter`、`ontology:concept/transition-coordinator`、`ontology:concept/timeline-integrity-gate` 等，若确为独立 PDCA 实体）
迁移后执行引用审计（grep 全仓）：仅当 `knowledge/pdca-flow/` 路径零残留引用（或引用已改为本体重写 id）后**删除**该目录；supporting 节点仅在确为独立 PDCA 实体时创建，其余内容并入流程实体或既有 concept 节点，避免节点爆炸（YAGNI）。

### Part 3 pdca-workflow 知识迁移
将 `knowledge/pdca-workflow/` 6 个文件迁移进既有本体节点：
- 如 `ai-friendly-confirmation` → `ontology:concept/pdca-verdict` 的属性/关系
- `architecture-review-metrics` / `provable-skill-increments` / `source-diagram-doc-verification` → `ontology:concept/pdca-acceptance-criterion` 相关
- `id-collision-remediation` / `scenario-boundary-rule` → 对应 concept 节点
迁移后执行引用审计（grep 全仓）：仅当 `knowledge/pdca-workflow/` 路径零残留引用（或引用已改为本体重写 id）后**删除**该目录。

### Part 4 PDCA ADR 决策沉淀
- ADR-0032（本体驱动 PDCA）、ADR-0033（本体指南采纳）、ADR-0034（元本体门禁）、ADR-0035（元本体门禁运行时）、ADR-0036（本体全生命周期门禁）的决策，沉淀进相关本体节点（流程实体 / `pdca-task` / `pdca-ontology-ready` / `ontology-creation-gate`）。
- 每个 ADR 文件顶部加 `superseded-by-ontology: <ontology id>` 标注，保留为历史决策记录（不删除）。

### Part 5 机制复用与引用清理
- 全部新节点经 T0829 的 `scripts/ontology-validate.py` 与 `ontology-check` 门禁校验（**不新建机制**）。
- grep 确认原 `knowledge/pdca-flow/`、`knowledge/pdca-workflow/` 路径无残留引用；SKILL/docs 中对这些知识的引用更新为本体重写 id。

## 验收标准

- [ ] AC-1（流程即实体）：`ontology/process/flow-{plan,do,check,act}.md` 四个实体创建，`type=process` 且 `specializes=[ontology:concept/process]`（与 code-review-process 一致），可选 `relates_to=[ontology:concept/pdca-task]`，relations 关联对应 phase 实体与 gate，body 含权威描述与关键决策
- [ ] AC-2（pdca-flow 迁移）：`knowledge/pdca-flow/` 16 文件的描述与决策迁移进本体（流程实体或 supporting 节点），引用审计无误后删除 `knowledge/pdca-flow/` 目录
- [ ] AC-3（pdca-workflow 迁移）：`knowledge/pdca-workflow/` 6 文件迁移进相关本体节点，引用审计无误后删除 `knowledge/pdca-workflow/` 目录
- [ ] AC-4（ADR 迁移）：ADR-0032~0036 决策沉淀进相关本体节点，每个 ADR 文件加 `superseded-by-ontology` 标注
- [ ] AC-5（机制复用）：全部新节点经 T0829 的 `ontology-validate.py` 校验通过（退出码 0、无悬空引用、无环），未新建校验机制
- [ ] AC-6（引用清理）：grep 确认原 `knowledge/pdca-flow/`、`knowledge/pdca-workflow/` 路径无残留引用；外部对它们的引用已更新为本体重写 id

## 非目标

- 不重建 `ontology-validate.py` / `ontology-check`（T0829 拥有）
- 不迁移 tls 域等具体领域知识（T0829 试点范围）
- 不改动四个流程的运行时行为或脚本
- `docs/pdca-workflow-*.md` 等渲染视图保留（人类可读，不视为冗余描述）

## 风险与缓解

- **删除知识目录风险**：删除前用 grep 全仓扫描引用（AC-6），仅当零引用或引用已更新后才删除；SKILL 引用优先改为指向本体 id。
- **ADR 标注遗漏**：逐一对 ADR-0032~0036 加 `superseded-by-ontology`，避免历史决策丢失语义。
- **节点爆炸**：supporting 节点仅在确为独立 PDCA 实体时创建，避免为每篇笔记建节点（YAGNI）。

## 关联本体节点

ontology:concept/process
ontology:concept/pdca-task
ontology:concept/pdca
ontology:concept/pdca-phase
ontology:concept/pdca-transition
ontology:concept/pdca-gate-do
ontology:concept/pdca-ontology-ready
ontology:concept/pdca-verdict
ontology:concept/pdca-acceptance-criterion
ontology:concept/ontology-creation-gate
（以及本任务新建的 ontology:process/flow-{plan,do,check,act} 等）

---
schema: pdca.asset/v1
id: ontology:process/flow-do
type: process
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/flow-do/1.0.3
summary: Do 阶段流程实体：按 ontology_role 与 execution_contract 执行、ontology-ready 关卡、证据登记与执行器边界
relations:
  specializes:
  - ontology:concept/process
  part_of:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca-phase
  - ontology:entity/phase-do
  - ontology:concept/pdca-ontology-ready
  - ontology:concept/pdca-gate-do
  - ontology:concept/executor-adapter
  - ontology:concept/external-evidence-collection
  - ontology:concept/destructive-cleanup-safety
  - ontology:concept/real-project-mechanism-validation
  - ontology:concept/pdca-home
  - ontology:domain/skill-tdd
  - ontology:domain/skill-code-review
  - ontology:domain/skill-research
  - ontology:domain/skill-codebase-design
  - ontology:domain/skill-design-it-twice
  - ontology:domain/ontology-hybrid-develop-bottomup
  - ontology:domain/ontology-hybrid-research-topdown
  - ontology:domain/ontology-hybrid-leaf-middleout
  testable_signal: "引用存活：test $(grep -rl 'ontology:process/flow-do' ontology/ tests/ scripts/ | wc -l) -ge 6"
---

# PDCA Do 流程（flow-do）

Do 阶段按 `meta.ontology_role` 的本体职责执行，具体动作由本体产出的 `execution_contract` 决定，是 PDCA 周期中唯一产生实现产物的阶段。

## 阶段步骤（权威描述）

1. **全新子 Agent 前置门禁**：协调 Agent 经 Adapter 调用 `agent.spawn`，为当前 PDCA 任务一次性启动一对一的全新子 Agent/子智能体上下文。禁止复用既有任务、并行任务或协调 Agent 的活动执行上下文；跨任务输入只从明确引用的持久化 PRD、任务元数据、证据与 context pointer 加载。`agent.spawn` 不可用时 fail-closed，当前任务保持未执行，不产生 Do 产物或执行证据，也不得回退协调 Agent。
2. **职责与契约**：`flow-do` 依据 `task.json.meta.ontology_role` 选择本体职责，再读取 `execution_contract` 的产物、动作、约束和可验证信号；执行器和工具只是实现这些动作的适配器。
3. **ontology-ready 关卡**：`meta.ontology_fragment` 指向的领域片段须存在且结构合法（自举任务经 `meta.ontology_exempt` 豁免）。只有 `execution_contract.required_actions` 明确要求基于来源的调研时，当前任务自身的 `research-report.md` 才须通过图与网络证据校验（`mermaid≥3/Source≥3/http Source≥1/URLs≥2`）；关联任务状态或产物不得代理当前任务准入。若当前 `execution_contract.work_product` 本身就是调研报告，则只校验该产物质量，不要求它先为自身提供前置证据。`research` 仅为可选 skill 名称，不是任务路由或门禁控制字段。
4. **自主执行与挂起**：一次性启动成功后，协调 Agent 立即进入 `suspended_waiting_agent` 并停止运行。绑定当前 PDCA 任务的全新子 Agent 自主调用对应 skill；外部产物先复制 `workspace/external-artifacts/` 再登记 Evidence。
5. **证据登记**：`register-evidence` 把产物锚定到 `pdca-evidence` 子类型。
6. **恢复后的本体实现符合性验证**：子 Agent 将状态、证据、转换记录与工作产物写入当前任务自身文件。协调 Agent 恢复后只读当前任务的 `task.json`、transition receipts、evidence manifest 与工作产物，构造 `result=pending` 的内容寻址审查包；任务原 `ontology_role` 不变，`ontology_conformance_verification` 是 review action。确定性门禁不得自行写入通过，协调器须另行绑定 review digest、`confirmed|rejected` 决定与理由后才能结束执行状态。禁止读取子 Agent 活动上下文或检查其他任务。需要用户确认时，`awaiting_confirmation` 拒绝 Agent 直接完成；由主会话写回真实 clarification 后，协调器绑定请求后新增条目及摘要，才将同一 Agent 恢复到 `suspended_waiting_agent`。子 Agent不得代签。
7. **门禁**：`pdca-gate-do` 校验后才能收尾进入 Check。

`suspended_waiting_agent` 与 `awaiting_confirmation` 都是执行状态，不是新增 PDCA phase。任务之间的 `parent` 与 `dependencies` 仅表达拆分和调度关系，不表达生命周期控制或验收代理。

## 关键决策（已迁移自外部知识）

- **执行器边界**（详 `ontology:concept/executor-adapter`）：`meta.ontology_role` 表达本体专业职责，`execution_contract` 声明产物、动作、约束和可验证信号；Executor ID 只表达完成该契约所需的执行角色，开放 Executor type 表达执行协议或平台类别，Registry adapter 指向可替换平台插件。核心 Planner 只判定 ready，Registry preflight 解析类型、能力与信任策略；Adapter 统一承担输入映射、会话、权限、超时/取消、流式事件和结果归一化。Codex/OpenCode/Claude Code/API Agent/MCP 差异都留在 Adapter，核心无平台分支。仅 automatic 且能力满足可直接调用；命令型/Agent 型默认需审批。tmux 驱动 OpenCode 须固定工作目录、变更白名单、超时重试与可观测性；阶段推进交由流程控制，安全边界与最终判定由执行器负责。
- **外部项目注入**：workflow root 与 agent 工作目录分离时，启动器须为目标项目执行平台 setup 并显式传入 workflow root，仅当目标缺 `AGENTS.md` 才写入（保护用户已有说明），setup 失败则拒绝启动。
- **外部证据收集**（详 `ontology:concept/external-evidence-collection`）：中央 manifest 只接受 workflow root 内安全相对路径，拒绝绝对路径/符号链接；外部产物复制副本到 `workspace/external-artifacts/` 后登记。
- **销毁清理安全**（详 `ontology:concept/destructive-cleanup-safety`）：可恢复清理须 dry-run 生成精确清单并固定恢复源为删除前不可变 commit（不引用会漂移的 HEAD）；apply 前重新验证每个目标仍处允许删除状态，任一漂移/越界/不可恢复则整批失败关闭。
- **全局仓库配置**（详 `ontology:concept/pdca-home`）：`$PDCA_HOME` 为第一优先级；仅含 `ontology/process/flow-plan.md` 的目录为有效 workflow 仓库；外部项目经 `scripts/init-external.sh` 初始化。

## 按本体职责执行

### 本体建模（`ontology_modeling`）

从问题证据抽取概念、关系、约束和可验证信号，产出研究报告、文档或本体节点。研究类产出须追溯 primary sources、登记 evidence，并在 Check/Act 完成本体沉淀。

### 本体投射（`ontology_projection`）

将本体树叶节点的约束投射为代码、测试或配置变更。先确认行为边界，再以失败测试或可复现证据驱动最小实现；完成垂直切片后运行定向验证和项目支持的全量验证。

### 本体符合性验证（`ontology_conformance_verification`）

对设计、实现或知识产出执行符合性检查，逐项映射 acceptance criteria、边界和证据，产出可审查的符合性结论。

具体执行方式由 `execution_contract` 决定。工具、skill、文档类型和测试方式属于执行适配层，不是 PDCA 流程本体职责，也不应在门禁中复制为另一套分类。

## 路由值说明

`meta.ontology_role` 只允许 `ontology_modeling`、`ontology_projection`、`ontology_conformance_verification`；`execution_contract` 必须声明产物、动作、约束和可验证信号。

## 来源

- `（原知识层）executor-adapter-boundary.md`
- `（原知识层）opencode-tmux-executor-adapter.md`
- `（原知识层）external-project-workflow-injection.md`
- `（原知识层）external-evidence-collection.md`
- `（原知识层）destructive-cleanup-safety.md`
- `（原知识层）global-repo-config.md`
- `（原知识层）real-project-mechanism-validation.md`

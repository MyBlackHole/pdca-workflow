# 本体树驱动的多 Agent PDCA：设计目标

## 目的

将复杂工作建模为可审查的本体树，再依据固定本体实施，并独立验证本体与实现的一致性。目标是让 Agent 的上下文、责任、证据和依赖边界由本体定义，而非依赖完整对话记忆或临时调度判断。

本文件只固定已确认的设计目标和边界，不构成实施计划，也不改变当前运行规则。

## 核心定义

- **PDCA** 是一个最小可验收工作节点的单独闭环：一个 `task_id`、一个 `attempt`、一个原 Agent，以及自己的 Plan、Do、Check、Act、授权和证据。每个阶段开始都必须取得用户对该节点、该阶段和固定对象的明确确认；前一阶段完成、节点 ready 或任务已派发都不构成下一阶段授权。
- **本体树** 是项目或复杂工作的定义、分解、依赖与汇聚结构；它是协调容器，不应被误作一个替所有子项执行的 PDCA 任务。
- **可实施节点** 是边界清晰、可指定目标位置、具有验收标准且可独立验证的节点。只有此类节点可派发实施 Agent。
- **容器节点** 只组织子项或表达领域结构，不直接派发实施 Agent。
- **汇聚节点** 依赖子项产物，并负责跨节点接口、整体约束或端到端行为；其验证不能由子项 PASS 的数量代替。汇聚节点可以实施集成代码、接口适配、装配或端到端配置，但必须显式声明 `implementation_target`；未声明时只做组合验证。

## 三条工作链

### 1. `pdca-model`：自顶向下建立本体树

建模从主实体开始；当一个节点过大、边界不清或无法独立验收时，将其拆成子实体与子本体，直至获得可实施叶节点。父节点必须保留子项之间的关系、依赖和整合约束。

本体至少能够表达：

- 稳定 `node_id`、节点种类与父子关系；
- 目标、对象、关系、约束、不变量、验收标准、边界与未知项；
- `depends_on` 和实现目标；
- 固定的 `ontology_revision`。

### 2. `pdca-implement`：自底向上实施本体树

首次实施只使用整棵树已固定版本的本体；未冻结的新子树不得混入已有版本的实施。从没有未满足依赖的可实施叶节点开始，逐步向根推进。每个可实施节点只有在用户确认后才由宿主派发独立上下文的 Agent，并形成独立 PDCA 任务；该 Agent 只读取完成本节点所需的本体切片、依赖产物和授权。

实施记录本体元素到实际代码、文档、配置或其他业务产物位置的映射。父级协调只依据真实完成记录解除依赖，不代替子 Agent 执行、回答、验收或伪造完成。

### 3. `pdca-verify`：自底向上逐项验证本体与实现

验证也按依赖自底向上推进：先验证可实施叶节点，只有子节点验证结论与证据齐全，才验证父节点的汇聚约束。验证由独立于实施 Agent 的 Agent 执行，对每个实施节点建立并核验以下链路：

```text
原始需求 → 本体节点 → 实现产物 → 单元测试／必要实际行为
```

验证不只统计测试通过，还应检查本体映射是否完整、约束和不变量是否落实、反证和未知是否被保留，以及父节点的跨节点接口和端到端行为是否正确。

## 不可破坏的边界

- 本体、实施和验证都由 PDCA 组成，但不把三个名称理解为三个共享同一上下文的阶段。
- 每个独立 PDCA 的 Plan、Do、Check、Act 均逐阶段等待用户确认；任何节点、父级、依赖状态或 Agent 都不能预先批准后续阶段。
- 一个实施节点对应独立 Agent 与独立上下文；验证不得由同一实施 Agent 自证。
- 本体发生实质变化时产生新 `ontology_revision`，并标识受影响的实施和验证结果；旧 PASS 不得静默迁移到新本体。
- 日常任务经验可形成知识候选，但不能自动变成共享知识或新的执行规则；共享发布仍需要 Act 的明确授权。
- Markdown 可以承载本体，但文件数量、树形目录或测试输出存在均不等于本体正确或实现完成。

## 成功标准

1. 每个已派发 Agent 都可定位其唯一本体节点、依赖、输入范围、实施目标和验收标准。
2. 每个已实现节点都可反向定位到固定版本的本体元素和真实产物位置。
3. 每个验证结论都能定位到需求、本体、实现和测试／行为证据，且保留反证、限制和 unknown。
4. 根级结论在子项结论之外，额外证明跨节点约束与整体行为。
5. 本体变更能够准确显示哪些实施和验证结果需要重新处理。

## 节点状态索引

为每个本体节点维护可重建的 `ontology-node-state` 索引。它方便查询哪些节点可实施、可验证或已经失效，但不单独证明任何结论；任务、交付、映射、验证报告和证据记录才是权威事实。

```yaml
schema: pdca.ontology-node-state/v5
work_id: <本体树所属工作>
tree_revision: <冻结树版本>
node_id: <稳定节点 ID>
node_kind: container | implementable | aggregate

ontology_ref: <固定本体节点与 ontology_revision>
parent_ref: <父节点>
dependency_refs: []

implementation:
  task_refs: []
  delivery_refs: []
  mapping_refs: []
  state: not_ready | ready | awaiting_confirmation | running | delivered | failed | stale

verification:
  task_refs: []
  review_refs: []
  evidence_refs: []
  state: not_ready | ready | awaiting_confirmation | running | verified | failed | stale

derived_status: <由事实派生的总状态>
blocking_reasons: []
stale_reason: null
recomputed_from: []
recomputed_at: <时间>
```

索引删除后应能从集中 records 重建。它不能直接填写 `verified` 绕过独立验证，也不能从 Agent 自述或目录存在推导交付完成。

## 就绪与用户确认

就绪只表示输入和依赖满足，系统最多提出建议；实际执行必须由用户确认具名动作。

```text
draft
→ awaiting_ontology_freeze_confirmation
→ ontology_frozen
→ implement_ready
→ awaiting_implement_confirmation
→ implementing
→ implemented
→ verify_ready
→ awaiting_verify_confirmation
→ verifying
→ verified
```

任意阶段可为 `blocked`、`failed` 或 `stale`。本体冻结、创建实施任务、创建验证任务，以及每个独立任务内部的 Plan、Do、Check、Act，均要求各自针对固定对象的真实用户确认；任何前置完成或 ready 状态都不能替代下一阶段确认。

- `implement_ready` 要求节点可实施、当前本体已冻结，且必需依赖交付可用并与当前本体兼容。
- 叶节点的 `verify_ready` 要求本节点实施交付、映射和测试／行为证据齐全。
- 父或汇聚节点的 `verify_ready` 还要求全部必需子节点已经 `verified`，随后独立核验跨节点接口、整体约束和端到端行为。
- 系统可计算 ready、blocked 与 stale，但不得自动创建 Agent、启动阶段、重试、发布或覆盖旧结论。

## 三个短入口

短入口只是现有场景语义的名称收敛，不复制工作流、records、Agent、授权或版本规则。

| 短入口 | 对应现有场景 | 职责 |
|---|---|---|
| `pdca-model` | `ontology_modeling` | 自顶向下建立或修订本体树，等待用户确认冻结。 |
| `pdca-implement` | `ontology_projection` | 提示 `implement_ready` 的具名节点；用户确认后由宿主派发独立实施 Agent。 |
| `pdca-verify` | `ontology_conformance_verification` | 提示 `verify_ready` 的具名节点；用户确认后由宿主派发独立验证 Agent。 |

三个入口只处理当前绑定项目和固定本体版本。它们读取节点状态索引以提出建议，随后仍由宿主原生机制创建或路由独立任务。实施 Agent 不得验证自己的交付；父级只根据真实记录更新索引，不监工、代答或自动推进。

## 本体变更与失效传播

本体的目标、关系、约束、不变量、验收标准、依赖或实施目标发生实质变化时，必须创建新的 `ontology_revision`，不得原地改写已冻结版本。

新版本冻结后，系统按引用关系计算影响范围：

1. 直接修改节点的实施映射与验证结论标为 `stale`。
2. 依赖其接口、约束、输入/输出或交付的节点，其实施和验证均标为 `stale`。
3. 只受验证覆盖影响的节点，至少验证标为 `stale`。
4. 必需子节点为 `stale` 时，父汇聚节点不得保持 `verified`。
5. 不受影响的节点保留其交付与证据，可作为新版本的固定输入。

运行中的实施或验证任务发现输入版本变化时必须 `blocked`，保留已发生副作用和证据，不能将旧输入结果写入新版本。系统只展示影响清单和建议；用户确认新的本体冻结，并逐节点或逐具名批次确认返工与重新验证。`stale` 不等于 `failed`，旧结果仍是历史事实，只是不再证明新本体版本。

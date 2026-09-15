# 本体树驱动的多 Agent PDCA：设计目标（v2 — 假设层扩展）

## 目的

将复杂工作建模为可审查的本体树，再依据固定本体实施，并独立验证本体与实现的一致性。目标是让 Agent 的上下文、责任、证据和依赖边界由本体定义，而非依赖完整对话记忆或临时调度判断。

本体是 Agent 推理的结构化前提，具有分层结构：稳定层（契约）定义职责边界，假设层（演进）定义接口细节。假设是待验证的陈述，具有置信度，在实施和验证中被检验。

本文件只固定已确认的设计目标和边界，不构成实施计划，也不改变当前运行规则。

## 核心定义

- **PDCA** 是一个最小可验收工作节点的单独闭环：一个 `task_id`、一个 `attempt`、一个原 Agent，以及自己的 Plan、Do、Check、Act、授权和证据。每个阶段开始都必须取得用户对该节点、该阶段和固定对象的明确确认；前一阶段完成、节点 ready 或任务已派发都不构成下一阶段授权。
- **本体树** 是项目或复杂工作的定义、分解、依赖与汇聚结构；它是协调容器，不应被误作一个替所有子项执行的 PDCA 任务。
- **本体分层**：本体分为稳定层（契约）和假设层（演进）。稳定层定义节点职责边界、核心依赖关系、验收标准的"是什么"，变更需要正式 revision；假设层定义接口细节、实现约束、验收标准的"怎么测"，变更通过假设检验记录。
- **假设** 是本体中待验证的陈述，具有置信度和状态。假设是 Agent 对未知的推理前提，不是已确定的事实。假设的状态包括：hypothesis（待验证）、validated（已验证）、invalidated（已推翻）、revised（已修正）。
- **置信度** 是假设的可信程度（0-1），基于实施和验证证据计算。置信度趋势包括：improving（提高）、stable（稳定）、declining（下降）。
- **可实施节点** 是边界清晰、可指定目标位置、具有验收标准且可独立验证的节点。只有此类节点可派发实施 Agent。
- **容器节点** 只组织子项或表达领域结构，不直接派发实施 Agent。
- **汇聚节点** 依赖子项产物，并负责跨节点接口、整体约束或端到端行为；其验证不能由子项 PASS 的数量代替。汇聚节点可以实施集成代码、接口适配、装配或端到端配置，但必须显式声明 `implementation_target`；未声明时只做组合验证。

## 三条工作链

### 1. `pdca-model`：每个节点独立 PDCA

建模从主实体开始；当一个节点过大、边界不清或无法独立验收时，将其拆成子实体与子本体，直至获得可实施叶节点。父节点必须保留子项之间的关系、依赖和整合约束。

**每个节点独立 PDCA**：每个节点有自己的 Plan/Do/Check/Act 流程，与 pdca-implement 和 pdca-verify 保持一致。

```yaml
# 每个节点有自己的 PDCA 流程
node_pdca:
  node_id: order-service
  plan:
    scope: "order-service 本体建模"
    assumptions_to_identify: [接口细节, 性能约束, 实现约束]
  do:
    stable_layer: "..."
    hypothesis_layer: "..."
  check:
    stability_layer_check: "..."
    hypothesis_layer_check: "..."
  act:
    action: "冻结 order-service 的 ontology_revision v1"
```

**依赖处理**：父节点依赖子节点完成。

```yaml
# 父节点依赖子节点完成
parent_dependency:
  node: order-system
  depends_on:
    - node: order-service
      state: ontology_frozen
    - node: inventory-service
      state: ontology_frozen
    - node: payment-service
      state: ontology_frozen
  action: "子节点全部冻结后，父节点才能冻结"
```

**并行建模**：多个节点可以并行建模。

```yaml
# 多个节点可以并行建模
parallel_modeling:
  - node: order-service
    state: running
  - node: inventory-service
    state: running
  - node: payment-service
    state: running
note: "三个节点可以并行建模，但父节点需要等待它们完成"
```

本体至少能够表达：

- 稳定 `node_id`、节点种类与父子关系；
- 目标、对象、关系、约束、不变量、验收标准、边界与未知项；
- `depends_on` 和实现目标；
- 固定的 `ontology_revision`。

建模同时产生假设层：对接口细节、实现约束、测试方法的陈述，标注为 hypothesis 状态，等待实施验证。

### 2. `pdca-implement`：自底向上实施本体树

首次实施只使用整棵树已固定版本的本体；未冻结的新子树不得混入已有版本的实施。从没有未满足依赖的可实施叶节点开始，逐步向根推进。每个可实施节点只有在用户确认后才由宿主派发独立上下文的 Agent，并形成独立 PDCA 任务；该 Agent 只读取完成本节点所需的本体切片、依赖产物和授权。

实施记录本体元素到实际代码、文档、配置或其他业务产物位置的映射。父级协调只依据真实完成记录解除依赖，不代替子 Agent 执行、回答、验收或伪造完成。

实施同时产生假设反馈：对假设层中的陈述进行验证，记录 validated/invalidated/revised 状态，更新置信度。假设被推翻时，系统自动建议本体修订。

### 3. `pdca-verify`：自底向上逐项验证本体与实现

验证也按依赖自底向上推进：先验证可实施叶节点，只有子节点验证结论与证据齐全，才验证父节点的汇聚约束。验证由独立于实施 Agent 的 Agent 执行，对每个实施节点建立并核验以下链路：

```text
原始假设 → 实施证据 → 测试结果 → 假设是否成立
```

验证不只统计测试通过，还应检查本体映射是否完整、约束和不变量是否落实、反证和未知是否被保留，以及父节点的跨节点接口和端到端行为是否正确。

验证同时进行假设检验：对假设层中的陈述进行最终判决，确定 supported/contradicted/inconclusive 状态，更新置信度。被推翻的关键假设触发本体修订。

### 4. 子任务拆分机制

当任务过大、边界不清或无法独立验收时，系统支持在实施阶段动态拆分子任务。详细设计见[子任务拆分详细设计](2026-09-15-subtask-splitting-design.md)。

**拆分触发条件**：
- 代码规模 > 500 LOC 或 > 10 文件
- 预计时间 > 40 小时
- Agent 置信度 < 0.7
- 复杂度 > 阈值

**拆分约束**：
- 最大拆分深度：3 层
- 最小子任务规模：50 LOC
- 最大子任务数：5 个
- 需要用户批准

**核心原则**：
- 拆分在 Do 阶段进行，需用户批准
- 每个子任务对应独立 Agent 和独立 PDCA
- 父节点协调子任务执行和结果聚合
- 支持错误处理、版本控制和回滚

## 不可破坏的边界

- 本体、实施和验证都由 PDCA 组成，但不把三个名称理解为三个共享同一上下文的阶段。
- 每个独立 PDCA 的 Plan、Do、Check、Act 均逐阶段等待用户确认；任何节点、父级、依赖状态或 Agent 都不能预先批准后续阶段。
- 一个实施节点对应独立 Agent 与独立上下文；验证不得由同一实施 Agent 自证。
- 本体发生实质变化时产生新 `ontology_revision`，并标识受影响的实施和验证结果；旧 PASS 不得静默迁移到新本体。
- 日常任务经验可形成知识候选，但不能自动变成共享知识或新的执行规则；共享发布仍需要 Act 的明确授权。
- Markdown 可以承载本体，但文件数量、树形目录或测试输出存在均不等于本体正确或实现完成。
- 假设是本体的一部分，但假设被推翻不等于本体失败，而是本体的学习过程。
- 置信度是假设的可信程度，不是节点的完成度；低置信度假设需要更多验证，不需要立即修改。
- 假设检验记录是实施和验证的产物，不能绕过实施和验证直接填写。
- 稳定层变更需要正式 revision，假设层变更通过假设检验记录，两者不可混淆。

## 成功标准

1. 每个已派发 Agent 都可定位其唯一本体节点、依赖、输入范围、实施目标和验收标准。
2. 每个已实现节点都可反向定位到固定版本的本体元素和真实产物位置。
3. 每个验证结论都能定位到需求、本体、实现和测试／行为证据，且保留反证、限制和 unknown。
4. 根级结论在子项结论之外，额外证明跨节点约束与整体行为。
5. 本体变更能够准确显示哪些实施和验证结果需要重新处理。
6. 每个假设都可追溯到其来源（建模阶段、实施反馈、验证结论），且置信度变化有证据支持。
7. 假设被推翻时，系统能够自动建议本体修订，且修订建议可追溯到被推翻的假设。
8. 置信度趋势能够反映节点的可靠性变化，且趋势计算有明确的证据基础。

## 节点状态索引

为每个本体节点维护可重建的 `ontology-node-state` 索引。它方便查询哪些节点可实施、可验证或已经失效，但不单独证明任何结论；任务、交付、映射、验证报告和证据记录才是权威事实。

```yaml
schema: pdca.ontology-node-state/v6
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
  hypothesis_feedback: []  # 假设反馈记录

verification:
  task_refs: []
  review_refs: []
  evidence_refs: []
  state: not_ready | ready | awaiting_confirmation | running | verified | failed | stale
  hypothesis_testing: []  # 假设检验记录

derived_status: <由事实派生的总状态>
blocking_reasons: []
stale_reason: null
recomputed_from: []
recomputed_at: <时间>

# 新增：置信度
confidence:
  overall: 0.0  # 0-1，基于所有假设的加权平均
  breakdown:
    - category: interface  # 接口假设
      score: 0.0
      count: 0
    - category: constraint  # 约束假设
      score: 0.0
      count: 0
    - category: test  # 测试假设
      score: 0.0
      count: 0
  trend: stable  # improving | stable | declining
  last_updated: null
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

## 假设层与稳定层的边界判定

判定一个本体陈述属于哪一层：

| 判定条件 | 层级 |
|---------|------|
| 改变此陈述需要重新冻结本体树 | 稳定层 |
| 改变此陈述不影响其他节点的职责边界 | 假设层 |
| 此陈述描述"做什么"而非"怎么做" | 稳定层 |
| 此陈述描述"怎么做"而非"做什么" | 假设层 |
| 此陈述可被单个节点的实施独立验证 | 假设层 |
| 此陈述需要跨节点协调才能验证 | 稳定层 |

## 假设分层示例

```yaml
# 稳定层（契约）
node_id: payment-service
responsibility: "处理支付请求"  # 做什么 → 稳定层
dependencies:
  - node: gateway-adapter
    nature: payment-gateway  # 依赖性质 → 稳定层

# 假设层（演进）
hypotheses:
  - statement: "gateway-adapter 提供 process_payment(amount, currency) 接口"
    category: interface  # 怎么做 → 假设层
  - statement: "支付网关响应时间 < 2秒"
    category: constraint  # 怎么测 → 假设层
  - statement: "使用 Pydantic 验证参数"
    category: implementation  # 怎么做 → 假设层
```

## 假设检验层级区分

| 阶段 | 检验类型 | 目的 | 产出 |
|------|---------|------|------|
| 实施阶段 | 假设反馈 | 记录假设在实施中的表现 | hypothesis_feedback |
| 验证阶段 | 假设检验 | 对假设做最终判决 | hypothesis_testing |

实施反馈是"观察"，验证检验是"判决"。实施反馈可能不完整（只验证了部分假设），验证检验应覆盖全部假设。

## 假设检验失败处理

假设检验可能因以下原因失败：
- **证据不足**：标记为 inconclusive，保留 hypothesis 状态
- **环境不支持**：标记为 blocked，等待环境就绪
- **检验本身出错**：标记为 error，记录错误原因，由用户决定重试或放弃

## 假设存储位置

假设层与稳定层存储在同一节点文件中，位于 `hypotheses`、`constraints`、`test_hypotheses` 字段下。不单独创建假设文件，避免不一致。

## 假设检验范围规则

| 节点类型 | 检验范围 | 说明 |
|---------|---------|------|
| 汇聚节点 | 只检验自己的假设 | 子节点假设由子节点自己检验 |
| 可实施节点 | 检验自己定义的所有假设 | 包括接口、约束、实现、测试 |
| 跨节点接口 | 在汇聚节点验证 | 但不重新检验子节点假设 |

## 假设置信度传递规则

子节点验证后的置信度传递给父节点，但父节点需要重新验证：

1. 子节点验证假设，得到验证后置信度
2. 父节点使用验证后置信度作为初始值
3. 父节点重新验证假设，得到最终置信度

示例：
```yaml
gateway-adapter 验证 PS-H1=0.77
→ payment-service 使用 0.77 作为初始置信度
→ payment-service 重新验证 PS-H1
→ 最终置信度基于 payment-service 的验证结果
```

## 假设修订后验证规则

假设修订后需要重新验证：
- 只验证修订后的假设，不重新验证其他假设
- 修订后假设的初始置信度基于旧置信度和修订置信度的加权平均

## confidence_in_revision 初始化规则

修订内容的置信度（confidence_in_revision）基于修订依据的可信度：

| 依据类型 | 置信度 |
|---------|-------|
| 有明确依据（官方文档） | 0.9 |
| 有类似项目经验 | 0.7 |
| 基于推断 | 0.5 |

## 本体复用

### 复用类型

| 类型 | 描述 | 适用场景 |
|------|------|---------|
| 节点复用 | 一个节点在多个本体树中复用 | 通用服务（如认证、通知） |
| 假设复用 | 一个假设在多个节点中复用 | 通用约束（如性能、安全） |
| 约束复用 | 一个约束在多个节点中复用 | 通用约束（如并发、超时） |
| 本体树复用 | 整个本体树在多个项目中复用 | 通用系统架构 |

### 复用规则

```yaml
reuse_rules:
  # 复用标识
  identification:
    - "节点/假设/约束必须有唯一 ID"
    - "节点/假设/约束必须有复用标记"
    - "节点/假设/约束必须有版本号"
    
  # 复用查找
  discovery:
    - "系统提供复用节点/假设/约束的查找功能"
    - "查找支持按类型、状态、版本筛选"
    - "查找支持按上下文、依赖、验证状态筛选"
    
  # 复用引用
  reference:
    - "复用时必须引用原始节点/假设/约束的 ID"
    - "复用时必须引用原始节点/假设/约束的版本"
    - "复用时必须声明复用上下文"
    
  # 复用解析
  resolution:
    - "系统自动解析复用的节点/假设/约束"
    - "系统自动处理复用节点/假设/约束的依赖"
    - "系统自动处理复用节点/假设/约束的版本"
```

### 复用与置信度

复用假设的置信度在新上下文中重新计算：

```yaml
reuse_confidence:
  # 上下文系数计算
  context_factor:
    factors:
      - "风险等级：高风险 → 0.7，中风险 → 0.8，低风险 → 0.9"
      - "重要性等级：高重要性 → 0.8，中重要性 → 0.9，低重要性 → 1.0"
      - "复杂度等级：高复杂度 → 0.8，中复杂度 → 0.9，低复杂度 → 1.0"
    calculation: "上下文系数 = 风险系数 × 重要性系数 × 复杂度系数"
    
  # 置信度计算
  confidence_calculation:
    formula: "复用置信度 = 原始置信度 × 上下文系数"
    example: |
      原始假设 PERF-H1: confidence=0.7
      上下文系数: 0.9 (低风险、中重要性、低复杂度)
      复用置信度: 0.7 × 0.9 = 0.63
```

### 复用与验证

复用假设需要在新上下文中重新验证：

```yaml
reuse_verification:
  # 验证范围
  verification_scope:
    - "原始验证结果是否适用"
    - "新上下文是否有额外约束"
    - "新上下文的实施是否符合假设"
    
  # 验证标准
  verification_criteria:
    - "复用假设的验证标准与原始假设相同"
    - "复用假设的验证证据需要在新上下文中收集"
    - "复用假设的验证结果需要在新上下文中记录"
    
  # 验证结果
  verification_result:
    - "复用假设的验证结果独立于原始验证结果"
    - "复用假设的验证结果可以不同（因为上下文不同）"
    - "复用假设的验证结果需要记录复用关系"
```

### 复用与版本管理

```yaml
reuse_version_management:
  # 版本引用
  version_reference:
    - "复用时引用原始节点/假设/约束的特定版本"
    - "复用时可以选择引用最新版本或特定版本"
    - "复用时必须记录引用的版本号"
    
  # 版本更新
  version_update:
    - "原节点/假设/约束更新后，复用关系保持不变"
    - "原节点/假设/约束更新后，复用方可以选择是否更新"
    - "复用方更新时，需要重新验证复用假设"
    
  # 版本冲突
  version_conflict:
    - "复用节点/假设/约束的版本冲突需要用户确认"
    - "系统提供版本冲突的检测和提示"
    - "用户可以选择保留旧版本或更新到新版本"
```

### 复用示例

#### 节点复用

```yaml
# 原始节点
notification-service:
  node_id: notification-service
  node_kind: implementable
  responsibility: "发送通知"
  dependencies:
    - node: email-provider
      nature: external-api
    - node: sms-provider
      nature: external-api
  hypotheses:
    - id: NS-H1
      statement: "邮件发送延迟 < 5秒"
      category: constraint
      confidence: 0.7
      basis: "邮件服务商 SLA"
  version: v1
  status: frozen
  reusable: true

# 复用节点
order-system:
  dependencies:
    - node: notification-service
      reuse: true
      reuse_version: v1
      context: "订单结果通知"
      adjustments:
        - hypothesis: NS-H1
          statement: "订单通知邮件发送延迟 < 3秒"
          confidence: 0.6
          basis: "订单场景对通知及时性要求更高"
```

#### 假设复用

```yaml
# 原始假设
common_hypotheses:
  - id: PERF-H1
    statement: "响应时间 < 2秒"
    category: constraint
    confidence: 0.7
    basis: "行业标准"
    version: v1
    status: validated
    reusable: true

# 复用假设
payment-service:
  hypotheses:
    - reuse: PERF-H1
      reuse_version: v1
      context: "支付网关响应时间"
      adjustments:
        statement: "支付网关响应时间 < 3秒"
        confidence: 0.6
        basis: "支付场景对响应时间要求更高"
```

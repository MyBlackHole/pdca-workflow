# T2181：投射 PDCA 子 Agent 执行契约到 runtime

## 背景

T2175 已确认 PDCA 根本体的设计核心为“权威本体图 -> 当前任务有界子图 -> 执行树/DAG”，并规定每个独立 PDCA 的 Do 由一对一全新子 Agent 自主执行。T2178 已从核心权威本体和路由文档中删除旧六场景、A/B/C 与 `scenario_type` 控制语义，但配置、Schema、Python runtime 和测试仍存在旧投射。

当前 `agent.spawn` 被能力配置声明为可选，并允许 `execute-in-main-session`；doctor 因此不会对缺失 spawn fail-closed。两份机读 contract 及其 resolver 仍按六场景和 A-F 路径路由；部分门禁还根据 `ontology_role` 隐式推导研究行为。运行时尚无可持久化的一对一派发绑定、协调挂起、当前任务恢复与本体实现符合性验证协议。

## 目标

在新 `pdca_runtime/` 目录建立与平台无关的 PDCA runtime 核心，将 `ontology:concept/executor-adapter`、`ontology:concept/capability-protocol` 和 `ontology:concept/pdca-task` 的约束投射为可执行状态机、Schema、CLI 和测试。具体工作由当前任务的 `ontology_role` 与四字段 `execution_contract` 决定，不再由场景表选择路径。

## 范围

- 建立旧控制消费者清单，覆盖配置、Schema、机读 contract、Python CLI/runtime 和测试 fixture。
- 新建 `pdca_runtime/` 核心包，负责严格读取当前任务、验证三个专业职责和四字段执行契约，并把“权威本体图 -> 当前任务有界子图 -> 执行树/DAG”物化为当前任务的内容寻址 projection manifest。
- 新增当前任务目录内的追加式 Agent execution receipts 及严格 Schema；执行状态快照只能从 receipts 推导，记录未派发、`suspended_waiting_agent`、`awaiting_confirmation`、等待符合性验证、完成或失败。这些是执行状态，不新增 PDCA phase。
- `agent.spawn` 设为必需能力。平台 Adapter 返回的一次性新子 Agent 标识和 `fresh_context` 声明必须绑定当前任务、职责、执行契约摘要和 context manifest 摘要；缺失、当前任务内重复确认或回执不匹配均拒绝。上下文新鲜度由创建上下文的平台 Adapter 保证，runtime 不通过读取其他任务证明。
- 派发成功后协调器只允许挂起；子 Agent 自主执行并把结果写入当前任务产物和 evidence。完成 receipt 必须绑定产物清单与 evidence manifest 摘要。恢复入口只读取当前任务自身的 task、transition receipts、Agent receipts、evidence manifest 与工作产物，然后执行 `ontology_conformance_verification`。
- 新增 executable-task Schema，在任务进入派发边界时强制 `execution_contract` 恰含四个权威字段；历史任务继续由生命周期 Schema 只读验证，不作为活跃 runtime 的兼容输入。删除未被任务使用的额外控制字段 `requires_fix_confirmation`。
- 删除旧场景 route/execution contract、resolver 与 Schema，不提供兼容别名或转换层；迁移仍需保留的测试和审计入口。
- 删除按职责隐式猜测研究行为的 runtime 分支；需要调研、测试、文档或审查时，由 `execution_contract.required_actions` 和 work product 明示。

## 非目标

- 不实现任何具体平台的 Agent API，也不从 Python shell 启动 Codex。
- 不读取或聚合 parent、children、dependencies 或其他任务状态。
- 不修复 doctor 报告的历史 ID 重复、旧活跃任务测试接缝或其他存量基线问题。
- 不修改历史 records、journal、归档任务和无关活跃任务。
- 不保留旧六场景、A/B/C、A-F 路由或主会话执行回退的兼容支持。

## 执行设计

1. **投影层**：从权威本体图选择当前任务 anchor、显式关联节点及所需关系，形成有界子图；再把 `required_actions`、task steps、约束和退出信号投影为可验证执行树/DAG。每个执行叶必须回链一个本体节点、一个动作和一个完成判据。
2. **模型层**：不可变解析 `task.json`，要求 `ontology_role` 为三个专业职责之一，`execution_contract` 恰含 work product、required actions、constraints 和 testable signal；只有通过 executable-task Schema 的当前任务可派发。
3. **能力层**：从能力配置读取 `agent.spawn required=true`；`PDCA_AGENT_SPAWN` 只能作为 doctor 的诊断观察，不能单独授权派发。实际 binding 必须来自平台 Adapter 的成功回执；任一缺失都 fail-closed。
4. **派发层**：从当前任务目录内的 projection/context manifest 生成带摘要的 request；平台原生 Adapter 成功创建全新子 Agent 后提交 `fresh_context=true` 回执。固定仓库锁覆盖“读取当前状态 -> 校验摘要 -> 写 binding receipt”，以 expected state 和 request digest 做单任务 CAS，防止并发双派发和 stale request。
5. **自主执行层**：runtime 不提供轮询、步骤控制或主会话代执行动作；子 Agent 只通过当前任务持久化输入和输出协作。结果 receipt 必须绑定 request、Agent ID、产物清单和 evidence manifest 摘要。
6. **恢复层**：登记子 Agent 完成或 `awaiting_confirmation` 后，协调会话可从当前任务持久化资料恢复；完成分支构造仅含当前任务资料的有界审查包，执行确定性门禁并进入 `ontology_conformance_verification`，不能检查其他任务。这里的符合性验证是 T2181 当前周期的恢复步骤，不改变 `ontology_projection` 职责，也不创建或检查另一任务。
7. **迁移层**：现有入口改用新核心；旧场景 contract、resolver、Schema 和 fixture 直接删除或重写，不设置兼容路由。

## 自举执行约束

T2181 修复的正是旧 runtime 无法正确表达原生子 Agent 能力的问题，因此不能用待实现机制证明自身。当前环境已直接验证存在原生 `spawn_agent` Adapter；本轮 P6 确认后的自举派发事务固定为：

1. 协调器在当前任务目录写入一次性 bootstrap dispatch request，绑定 task、PRD、职责、契约和 context 摘要。
2. 只允许原生 Adapter 以 `fork_context=false` 创建一个全新子 Agent，并把当前任务持久化路径作为唯一任务输入。
3. Adapter 返回后，协调器立即把真实 Agent ID 和 request digest 写入当前任务 bootstrap binding receipt；这是派发事务的最后一步。
4. 协调会话随即停止，不调用 wait/poll/send-input，不读取子 Agent 活动上下文。后续只有用户显式恢复主会话时，才读取当前任务持久化产物进行符合性验证。

这两份 bootstrap receipt 只证明 T2181 的自举执行，不得被新 runtime 接受为未来任务的兼容协议。不得使用 doctor 当前报告的 `execute-in-main-session` fallback。任务设置 `ontology_exempt=true` 仅用于通过当前代码中待删除的“projection 职责默认强制 research-report”自举门禁；本任务仍在 PRD 中强制证据、符合性审查、Check 和 Act 本体沉淀，并在验证报告中单独证明这些环节实际完成。

## 验收标准

- [ ] AC-1: 产出 runtime 消费者清单，覆盖配置、Schema、机读 contract、Python 和测试中的所有旧场景控制点；同时生成当前任务 projection manifest，明确展示权威本体图、有界子图和执行树/DAG三层，且每个执行叶可追溯到本体节点、required action 与完成判据。
- [ ] AC-2: `pdca_runtime/` 成为新的核心实现目录；executable-task Schema 和核心解析器都要求三个 `ontology_role` 之一及恰好四字段的 `execution_contract`，缺字段、额外控制字段或旧角色值均以稳定错误拒绝；历史任务 Schema 不参与活跃派发授权。
- [ ] AC-3: `agent.spawn` 在配置和 doctor 中为 required 且无 fallback；探测不可用时 doctor/runtime 明确报告 missing，当前任务保持未派发且不产生 Do 执行证据。
- [ ] AC-4: 派发请求和 binding receipt 绑定当前 task ID、ontology role、execution contract digest、projection/context manifest digest、非空子 Agent ID 与 Adapter 的 `fresh_context=true` 声明；锁保护的单任务 CAS 拒绝重复派发/绑定、stale request、摘要漂移或错误 task ID，且实现不得扫描其他任务证明新鲜度。
- [ ] AC-5: 派发成功后当前任务执行状态为 `suspended_waiting_agent`；runtime 不暴露主会话代执行、活动轮询或持续步骤控制入口。
- [ ] AC-6: 子 Agent 可追加完成、失败或 `awaiting_confirmation` receipt；完成 receipt 绑定 request、Agent ID、产物清单和 evidence manifest 摘要。协调恢复只读取当前任务持久化 task、receipts、evidence manifest 和工作产物，不读取关联任务，并在完成分支生成有界审查包、执行确定性门禁及当前周期内的 `ontology_conformance_verification`。
- [ ] AC-7: 旧场景 route/execution contract、resolver、Schema 和控制 fixture 被删除或迁移；活跃配置、Schema、Python 与测试中不存在 `scenario_type`、六场景集合、A-F 路由或 `execute-in-main-session` 控制语义。
- [ ] AC-8: runtime 不再根据 ontology role 猜测 research、development、bugfix、documentation、design 或 review 行为；工具和动作只由当前任务四字段契约显式提供。`flow-do` 中允许用归档依赖任务研究报告满足当前任务门禁的矛盾表述同步移除，以根本体的禁止跨任务检查规则为准。
- [ ] AC-9: 三个专业职责均通过独立任务投影/派发/挂起/恢复正向测试；缺失 spawn、旧角色、契约漂移、并发或重复派发、stale request、跨任务恢复、篡改结果摘要和主会话回退均有负向测试。
- [ ] AC-10: 所有本轮目标测试和受影响回归通过；完整 Python 套件已执行且相对 Plan 基线没有新增失败。基线 261 tests / 37 failures / 5 errors / 2 skipped 须按“本轮应修复”与“无关存量”逐项归因。本体契约、0 孤岛、技能索引、收敛映射及 `git diff --check` 通过。
- [ ] AC-11: T2181 自身保留一次性 bootstrap request/binding receipt，真实绑定一个 `fork_context=false` 的全新原生子 Agent；binding 后协调会话无 wait、poll、send-input 或主会话实施行为。新 runtime 不读取该 bootstrap 格式作为未来兼容入口。

### 声明的测试接缝

- seam: `pdca_runtime/tests/test_pdca_runtime.py` -> `pdca_runtime` 核心模型、派发状态机与恢复边界
- seam: `pdca_runtime/tests/test_task_contract.py` -> executable-task Schema 的三职责与四字段执行契约
- seam: `pdca_runtime/tests/test_ontology_projection_runtime.py` -> 权威本体图到任务有界子图及执行树/DAG 的可追溯投影
- seam: `tests/test_operations.py` -> capability 配置与 doctor fail-closed 诊断
- seam: `tests/test_execution_and_invocation_contracts.py` -> 职责/执行契约机读入口与旧场景 contract 移除
- seam: `tests/test_research_first_gate.py` -> execution contract 显式动作门禁

## 关联本体节点

- `ontology:concept/executor-adapter`
- `ontology:concept/capability-protocol`
- `ontology:concept/pdca-task`
- `ontology:concept/pdca`
- `ontology:process/flow-do`
- `ontology:concept/runtime-transition-coordinator`

## 拆分映射

- 子 Agent runtime 投射 -> ontology:concept/executor-adapter

## 拆分结论

不拆分子任务。本轮是 `ontology:concept/executor-adapter` 的单一有界 runtime 投射；配置、Schema、状态机、CLI 和测试共同构成同一原子契约。拆成关联任务会重新引入跨任务验收与迁移中间态，而 parent/dependencies 只能承担调度语义，不能代理本任务生命周期。

## 已知基线

- doctor 当前因多个既有活跃任务测试接缝缺失而整体 `valid=false`；该结果必须与本任务新增能力检查分别报告。
- Plan 基线为 261 tests / 37 failures / 5 errors / 2 skipped；其中旧 route/execution contract、旧 flow 标记和 doctor fallback 失败属于本轮迁移面，其他失败需保持不新增并单列归因。
- 仓库存在历史 task ID/slug 重复诊断；identity 诊断当前不参与 doctor 的 `valid` 计算，也不属于本轮范围。
- T2164/T2165 是基于已废弃 A/B/C 模型的旧活跃任务，不能作为本轮实现或兼容依据；本任务不修改其状态。

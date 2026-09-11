# T2175 PDCA 根本体验证报告 v3

## 本体修正结果

- AC-1：`ontology:concept/pdca` 与 `ontology:concept/pdca-phase` 将 PDCA 和 Deming 采用的 PDSA 区分为相关但不应无条件等同的循环表述，不再把 Deming Cycle / Shewhart Cycle 当作无保留历史归因。
- AC-2、AC-8：保留精确标题“设计核心：本体树驱动”，固定“权威本体图 -> 任务有界子图 -> 执行树/DAG”；图是语义结构，树驱动是任务投影与执行原则。
- AC-3：根节点明确本体语义节点不等同于 `ontology/<type>/<slug>.md` 的 `pdca.asset/v1` 序列化资产。
- AC-4：根节点以 `relations.composed_of` 机读连接任务、阶段、转换、门禁、验收、证据、判定、执行契约、恢复、反馈和持续改进，以 `relates_to` 连接流程模型与执行器适配边界。
- AC-5：根节点仅声明 `ontology_modeling`、`ontology_projection`、`ontology_conformance_verification` 三个专业职责；执行由 `execution_contract` 描述，不以 A/B/C 或六场景字段建模。
- AC-6：根本体没有具体 Python 文件或脚本绑定；runtime 只作为后续投射消费者。
- AC-7：关系目标存在，`ontology-validate` 通过，未发现关系环或悬空关系。
- AC-9：`pdca` 与 `pdca-task` 均声明 `execution_agent_kind: child_agent`、`allocation: fresh_child_agent_per_task`、`child_execution_mode: autonomous`、`parent_after_dispatch: suspended`、`parent_execution_state: suspended_waiting_child`、`control_after_dispatch: none`、`live_polling: forbidden`、`parent_resume_source: persisted_child_task_documents` 与 `parent_task_roles: [dispatch, suspend, resume_and_aggregate]`。父任务一次性启动子 Agent 后立即停止运行；子 Agent 自主执行，不共享活动上下文。
- AC-10：`agent.spawn` 是必需能力；不可用时 fail-closed。父任务不持续控制或轮询，仅在以后恢复时从子任务 `task.json`、transition receipts、evidence manifest 与 `conclusion.md` 重建并聚合。需要用户确认时，子任务持久化 `awaiting_confirmation`，父任务恢复后由主会话转交真实确认并再次挂起；子 Agent 不得代签。
- 旧控制语义清理：12 个 T2175 权威文件不再使用 A/B/C 映射、`scenario_type`、`scenario==research` 或六场景分类控制任务路由与门禁。`research`、`design-it-twice`、`code-review` 只作为可由 `execution_contract.required_actions` 选择的工具名称。
- 执行状态边界：`suspended_waiting_child` 与 `awaiting_confirmation` 是执行状态，不是新增 PDCA phase。

## 冲突审查范围

已审查并修正确有冲突的权威节点：

```text
ontology/concept/pdca.md
ontology/concept/pdca-task.md
ontology/concept/capability-protocol.md
ontology/concept/executor-adapter.md
ontology/concept/pdca-phase.md
ontology/process/flow-do.md
ontology/process/pdca-flow-model.md
ontology/domain/pdca/skill-to-tickets.md
ontology/domain/pdca/skill-research.md
ontology/domain/pdca/skill-code-review.md
ontology/domain/pdca/skill-design-it-twice.md
ontology/domain/pdca/skill-wayfinding-chart.md
```

这些节点在本轮修订前已由同一未提交工作批次完成版本递增；本轮接管未重复递增 `owl_versionIRI`。

## 验证结果

```text
python3 scripts/ontology-validate.py --ontology-dir ontology
OK: ontology 通过本体契约校验

python3 scripts/validate-convergence.py --task-dir pdca/tasks/0911-pdca-root-ontology-pilot
valid: true

定向扫描旧主 Agent/主会话执行回退语句
无命中（rg exit 1）

定向扫描 fresh_per_task、fresh_context_per_task 及非“子 Agent”主体歧义
无命中（rg exit 1）

定向扫描持续 observe/poll/control 与 main_agent_roles: orchestration 歧义
无命中（rg exit 1）

git diff --check
通过（exit 0）

python3 scripts/generate-skills-index.py
正常生成 SKILLS-INDEX.md

python3 scripts/generate-skills-index.py --check
通过（exit 0）

AGENTS.md 权威流程与技能路由存在性核对
全部存在；write-conclusion 与 write-journal 可在 SKILLS-INDEX.md 中解析
```

## 后续 ontology_projection 差距

本轮按范围不修改 Python runtime、能力配置或 tests。当前 `config/capabilities.yaml` 仍把 `agent.spawn` 声明为 `required: false` 且 `fallback: execute-in-main-session`；`scripts/pdca-doctor.py` 读取并报告该配置，`tests/test_operations.py` 仍断言 `execute-in-main-session`。这与本轮权威本体的 required + fail-closed 语义不一致，须由后续 `ontology_projection` 任务修改配置/runtime/tests 并增加阻断回归验证；在该投射完成前，运行时门禁不能视为已实现本体约束。

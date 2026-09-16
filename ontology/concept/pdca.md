---
schema: pdca.asset/v2
id: ontology:concept/pdca
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-14'
summary: PDCA：用户控制推进，独立任务执行
protocol_revision: 4.0.0-rc.3
rule_authorities:
  TREE-01: ontology:concept/work-ontology-tree
  NODE-01: ontology:concept/work-node-contract
  SCENE-01: ontology:process/work-scenarios
  SCHED-01: ontology:concept/work-tree-scheduling
  TASK-01: ontology:concept/pdca-task
  CAP-01: ontology:concept/capability-protocol
  CONTRACT-01: ontology:concept/pdca-execution-contract
  CONTEXT-01: ontology:process/select-task-subgraph
  TEST-01: ontology:concept/task-unit-test
  CASE-01: ontology:concept/task-test-case
  REWORK-01: ontology:concept/task-rework
  REVIEW-01: ontology:process/independent-work-review
  CONFIRM-01: ontology:concept/pdca-ai-friendly-confirmation
  GATE-01: ontology:concept/pdca-gate
  TRANSITION-01: ontology:concept/pdca-transition
  EVIDENCE-01: ontology:concept/pdca-evidence
  VERDICT-01: ontology:concept/pdca-verdict
  RECOVERY-01: ontology:concept/pdca-recovery
  LEARN-01: ontology:concept/pdca-continuous-improvement
  ONTOLOGY-01: ontology:concept/ontology-asset
  STATE-01: ontology:concept/pdca-phase-status
  CONTROL-01: ontology:concept/task-control
  RESOURCE-01: ontology:concept/resource-ownership
  DEPENDENCY-01: ontology:concept/work-dependency-graph
  REUSE-01: ontology:concept/ontology-reuse
  EVOLVE-01: ontology:concept/ontology-evolution
  ADOPT-01: ontology:concept/ontology-adoption
  DECOMP-01: ontology:concept/task-decomposition
design_spec:
  task_cycle: full_pdca
  fresh_agent_per_task: true
  same_agent_across_phases: true
  advance_policy: explicit_user_operation
  parent_process_monitoring: false
  runtime: host_native
  bundled_workflow_code: false
  project_data_root: PDCA_ROOT/records
  resource_model: central_cross_project
  skill_entry_count: 8
---

# PDCA：用户控制推进，独立任务执行

每个独立节点／场景／attempt由自己的真实、可交互Agent完成Plan→Do→Check→Act；同任务保持原会话。用户确认每阶段目标并显式启动，阶段内自主，结束保存产物后等待。宿主只创建／路由／提供资源；父Agent不监控、代答、补阶段或审批。

## 唯一控制原则

用户授权与验收符合分开：授权不使违例变PASS，PASS不授权下阶段。新任务、新场景、新attempt均需具体操作；候选就绪不自动派发。普通请求和PDCA_ROOT只定位，不自动启用。

四阶段沟通复用任务说明、计划、请求／真实响应和证据；不新增第五阶段或平行GoalContract。每次恢复先读项目状态与原始依据；状态索引和摘要不创造权威。

## 三场景是真实对象链

pdca-model交付项目本体源及工作实例；pdca-implement从固定模型产生目标实体并记录映射；pdca-verify核对需求、模型、产物与必要实际行为。每个场景内部仍有四阶段，不以四份文字假装执行。Markdown可承载本体，文件格式本身不是验收依据。

本体、任务、确认、证据和资源预约集中在PDCA_ROOT管理；TARGET_ROOT只写获准业务产物，不默认生成.pdca。规则文件与活动任务记录只读，记录及模型按拥有者授权写入。保留目标、AC／oracle、身份、版本和恢复边界；专业方法按需使用。历史3.x规则不再控制4.x，新版本不追认旧任务合法。

## 权威与读集

下列28项原有权威ID保留，具体文件由当前索引、Skill目录与Git工作树定位；本版本改写其适用语义。按事件读取，不通读全部。其他资产只有经显式采用才是任务参考；不因authority字段或旧索引命中自动成为4.x控制规则。

当前最短路径：八个Skill入口 → [共同恢复入口](../contracts/entry-recovery.md) → 集中task／confirmation → 当前阶段与当前scene的方法。阶段与场景是两个维度，加载或切换Skill不新建Agent、不自动授权。权限／恢复／模型细则在相关事件发生时读取。

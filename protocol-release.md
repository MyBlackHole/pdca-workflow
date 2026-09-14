---
schema: pdca.protocol-release/v4
protocol_revision: 4.0.0-rc.2
status: release_candidate
runtime_publication_proven: false
host_acceptance: NOT_RUN
advance_policy: explicit_user_operation
records_root: PDCA_ROOT/records
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
manifest_ref: release-manifest.md
active_entry: skills/pdca/SKILL.md
skill_index: skills/catalog.json
resource_scope: central_cross_project
legacy_policy: never_load_as_current_execution
---

# 4.0.0-rc.2 当前发布入口

每阶段由用户显式启动，阶段结束等待；本版为候选，真实宿主尚未验收。manifest_ref是机器核对的当前文件清单，不要求每个任务全文注入。项目绑定同时固定本文件与清单的实际摘要，清单不自哈希。当前清单为 JSON fenced block：files 固定可安装文件，active 固定任务采用文件；集中业务数据不纳入软件发布。

只采用清单内当前规则与模板；历史指针、legacy、旧示例及参考资料不是默认控制规则。参考本体按任务逐项固定采用。

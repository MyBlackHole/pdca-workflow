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
revision: 4.0.0-rc.4
dcterms_modified: '2026-09-27'
summary: PDCA：用户控制推进，独立任务执行
protocol_revision: 4.0.0-rc.4
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
  skill_entry_count: 9
---

# PDCA：用户控制推进，独立任务执行

每个独立节点／场景／attempt由自己的真实、可交互Agent完成Plan→Do→Check→Act；同任务保持原会话。用户显式启动各阶段：Plan/Do/Check 完成后保存产物并等待下一真实操作；Act 是当前 attempt 的终态处置，完成后同一授权下 terminalize/archive，不再等待“第五阶段”。宿主只创建／路由／提供资源；父Agent不监控、代答、补阶段或审批。

## 唯一控制原则

用户授权与验收符合分开：授权不使违例变PASS，PASS不授权下阶段。新任务、新场景、新attempt均需具体操作；候选就绪不自动派发。普通请求和PDCA_ROOT只定位，不自动启用。

四阶段沟通复用任务说明、计划、请求／真实响应和证据；不新增第五阶段或平行GoalContract。每次恢复先读项目状态与原始依据；状态索引和摘要不创造权威。

阶段控制链固定为：

`CONFIRM authorization fact → GATE ready/blocked → TRANSITION event receipt → STATE derived index`。

四层不可互相替代：confirmed 不等于 ready，ready 不等于 running，状态字段也不能反向创造授权。

## 三场景是真实对象链

pdca-model交付项目本体源及工作实例；pdca-implement从固定模型产生目标实体并记录映射；pdca-verify核对需求、模型、产物与必要实际行为。每个场景内部仍有四阶段，不以四份文字假装执行。Markdown可承载本体，文件格式本身不是验收依据。

本体、任务、确认、证据和资源预约集中在PDCA_ROOT管理；TARGET_ROOT只写获准业务产物，不默认生成.pdca。规则文件与活动任务记录只读，记录及模型按拥有者授权写入。保留目标、AC／oracle、身份、版本和恢复边界；专业方法按需使用。历史3.x规则不再控制4.x，新版本不追认旧任务合法。

## 权威与读集

下列 28 项原有权威 ID 保留，由 [INDEX](../INDEX.md) 定位；[LOAD-MAP](../LOAD-MAP.md) 定义 AI 按事件最小读取的方法。规则只维护在当前 authority、phase flow、SCENE-01 与明确引用的契约中；Skill 是发现/路由入口，不再复制一份 phase/scene 语义。不得通过 validator 或额外 manifest 再实现一遍。其他资产只有经 REUSE/ADOPT 固定版本后才是任务参考。

## Version domains

仓库中的版本字段属于不同语义域，不能相互比较或据此自动升级：

- `skills/catalog.json.version` 与各 Skill 的 `metadata.version`：**runtime Skill bundle version**，只描述入口包/发现面的发布版本；
- 本文件的 `protocol_revision`：**PDCA protocol revision**，描述当前协议线与整体控制语义；
- 各 ontology asset 的 `revision`：**asset revision**，只描述该 authority/知识资产自身的内容修订，可在同一 protocol 内独立变化。
- active `pdca.contract/v4` 与 record template 中的 `protocol_revision`：必须声明当前 protocol 语义版本；`/v4` 只是 schema major，不是 protocol rc 版本。

因此 `5.0.0-rc.2` 的 Skill bundle 与 `4.0.0-rc.x` 的 protocol/asset 并不表示“新旧规则谁覆盖谁”。
当前规则身份由 **Git HEAD + INDEX 定位 + 当前 task 固定 refs/adoption** 决定；active contract/template 跟随当前 protocol，只约束新写入/当前格式解释，不追写历史实例。已有任务不会因为任一版本字段变化而自动改绑、自动采用或获得新授权。需要跨版本恢复时仍按 RECOVERY-01/ADOPT-01 核对实际来源、适用性和用户决定。

当前最短路径：九个 Skill 入口 → [LOAD-MAP](../LOAD-MAP.md) → 按事件读取 project-workspace / entry-recovery / task-create authority；只有真正进入 phase 时才追加当前 phase flow + SCENE-01 对应场景。没有 task 的定位或 Assist 不为形式完整强行加载 task 历史；已有 task 的连续性也不能跳过 entry-recovery。阶段与场景是两个维度，加载或切换 Skill 不新建 Agent、不自动授权。

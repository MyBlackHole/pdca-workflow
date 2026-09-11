---
schema: pdca.asset/v2
id: ontology:concept/task-record-identity
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.0
summary: 任务身份、尝试与唯一记录
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/work-ontology-tree
  - ontology:concept/task-unit-test
  - ontology:concept/task-rework
---

# 任务身份、尝试与唯一记录

任务目录为records/<task-id>/，与records/works/<work-id>/工作树和清单分离。真实唯一task_id不能使用无锁扫描最大数加一；撞名不覆盖。

使用pdca.task/v3.2。字段的完整清单见当前模板；主要字段包括：task_id、work_id、tree_revision、node_id、scene、attempt、predecessor_task_id、rework_issue_ref、revision、title、phase、execution_state、writer、conversation_ref、baseline、test_suite_ref、dependencies、parent_node_id、last_transition、control_view_ref、last_control_event、terminal_reason、termination_ref、wait_policy_ref、pinned_graph、resource_reservation_refs、capability_check_refs、extensions。scene是唯一场景字段，不再双写ontology_role；parent_node_id是组成归属，不是parent_agent_id。

attempt由SCHED-01真实槽所有者从1单调分配，历史编号不复用；同一工作/树/节点/场景最多一个有效写入者；重试新task_id新Agent。writer派发前为空，交接后绑定真实ID/回执。conversation_ref必须来自真实宿主。恢复原任务不修改attempt。

Plan草稿允许空baseline与测试绑定；进入Do前完整固定。revision是任务快照版本，artifact_revision、suite_revision、run_id独立记录，不能相互冒充。

records/<task-id>/tests/保存suite快照、cases引用和runs；artifacts保存基线/实际产物/固定包；issues保存本任务发现，工作级issue清单由宿主单写者维护。模板中的空值不是通过记录。


protocol_revision在派发前从当前工作实际选择并固定的协议发布清单取得，禁止本文件另写一个固定版本常量。protocol_baseline_ref绑定该清单与字节；业务baseline可在Plan后形成。schema版本更换不能在旧任务内覆写。控制event序号、四条阶段sequence、业务operation_id、测试run_id各有独立作用域。

## 版本与任务定位

仓库分发的 [协议清单](../../protocol-release.md)用于定位版本，不是用户运行授权；派发前将所选版本及其规则闭包保存为可重读快照。任务 schema 可继续 pdca.task/v3.2，资产有自己的 revision，不能为了数字相同改写未变化规则或旧记录。

唯一主记录为 records/<task-id>/task.md；树/场景清单用 task_id 和固定引用定位，不另造第二份可写 task.md。准备记录尚无真实 task_id/Agent 时保持未知，不宣称已派发或完成。attempt、writer、capability/reuse/交付记录必须来自同一真实尝试链；不凭改编号修复来源冲突。

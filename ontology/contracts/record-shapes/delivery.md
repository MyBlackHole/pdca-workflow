---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.3
authority: normative
status: active
---

# 本任务实际交付：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
---
schema: pdca.delivery/v4
protocol_revision: 4.0.0-rc.3
task_id: null
attempt: null
work_id: null
node_id: null
scene: null
definition_refs: []
artifact_refs: []
projection_map_refs: []
test_run_refs: []
check_ref: null
act_decision_ref: null
task_execution: null
subject_conformance: unknown
delivery_usable: false
scene_coverage:
  pdca-model: not_run
  pdca-implement: not_run
  pdca-verify: not_run
limitations: []
---

# 本任务实际交付

delivery 是 task/Act 的最终汇总索引，不重新计算 evidence 或 verdict。

- `test_run_refs` 只指真实 TEST observation；
- `check_ref` 指向 conclusion/VERDICT 聚合结果；
- `task_execution/subject_conformance` 从真实 task/conclusion 事实引用，不在此重判；
- `delivery_usable` 来自已完成的具体 Act 处置及 limitation，不因“用户认可”自动 true；
- `scene_coverage` 只按实际 scene task/records 填，未运行保持 not_run。

modeling/implementation/verification 的具体交付仍列真实 ontology/artifact/mapping/evidence refs，不用文件列表冒充符合性。

交付说明应如实披露 AI 参与的生成/审查范围，并把 AI 形成的 claim/reasoning 与工具、运行行为、外部来源产生的 observation/evidence 区分。该 provenance 说明不会提升 evidence status，也不产生 Git 提交、发布、采用或其他写入授权。
```

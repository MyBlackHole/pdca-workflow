---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 固定计划与验收基线：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
---
schema: pdca.baseline/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
goal_ref: null
plan_ref: null
input_refs: []
definition_refs: []
resource_scope: []
acceptance_criteria: []
test_suite_ref: null
---

# 固定计划与验收基线

work_product、required_actions、constraints、testable_signal。AC包含可检验预期与失败边界；SCENE必需模型／映射不可通过删AC豁免。

固定原需求、来源版本、模型、工具／环境及允许写域。每个ref记录实际sha256；内容改变建立新版本。批准对象引用其摘要，本文件不自哈希、不预填PASS。
```

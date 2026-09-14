---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 三向符合性：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
---
schema: pdca.conformance-review/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
requirement_refs: []
definition_refs: []
subject_refs: []
projection_map_ref: null
findings: []
result: not_run
---

# 三向符合性

原需求→模型：每项义务有对象／约束或明确缺口。
模型→投影：每项采用约束映射到目标位置，目标的实质主张无无依据增加。
产物→行为：实际运行覆盖适用预期及反例，未运行保持not_run。

每行给requirement/object/constraint/target/observation/verdict，保留反证。哈希、链接和文件数量不能代替这些核对。
```

---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 能力核验：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
---
schema: pdca.capability-check/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
environment_ref: null
scope: environment_or_invocation
required_capabilities: []
evidence_refs: []
result: not_run
limitations: []
---

# 能力核验

列真实宿主／工具／配置、输入继承、交互、恢复、写域、消息来源的适用性。环境核验可按版本复用，本次实际调用不能略过。

只填写已观察内容；未跑为not_run。脚本静态通过不升级真实隔离或阶段执行状态。
```

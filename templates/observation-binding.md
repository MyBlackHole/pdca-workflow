---
schema: pdca.observation-binding/v1
state: draft
binding_id: null
revision: null
task_id: null
artifact_ref: null
artifact_digest: null
window: null
required_claims: []
tools: []
controls: []
coverage_gaps: []
raw_evidence_refs: []
result: null
protocol_revision: 3.4.10
---

# 观测能力绑定

每条claim列明对象/调用窗口、实际工具与版本、事件来源、覆盖边界、断言、允许的夹具动作、已知正确和错误控制、实际结果、清理。返回结果正确但观测缺失不能pass。线程/子进程/异步范围必须显式决定，未覆盖不得自证。

控制运行与业务运行分开；实际证据未取得时字段保持空/unknown，不复制教学样本。完整例子见[范围观测](../examples/range-task/observation-binding.md)。

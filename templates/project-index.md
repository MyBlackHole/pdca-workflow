---
schema: pdca.project-index/v1
protocol_revision: 3.4.10
extension_revision: cross-project.2
project_id: null
workspace_bindings: []
work_refs: []
task_refs: []
---

# 项目资料索引草稿

保存为 PDCA_ROOT/records/projects/<project-id>/index.md。各项使用具名 ID、固定引用和摘要，另列该 workspace 对应的 TARGET_ROOT。由已有宿主/索引单写者维护，只用于定位；不是发布、批准对象，也不能替代固定 work/tree/task。

同一项目不同 checkout 使用不同 workspace_id；task_id 和 work_id 在整个 PDCA 项目内唯一。孩子只更新自己的正式记录；不能让全部 Agent 同写本索引。历史绑定与任务原字节保留，失效状态只追加事实或更新索引定位。

用户只配置PDCA_ROOT。project_id/workspace_id是内部索引：先按完整身份匹配旧绑定，否则按PX-ID生成；禁止仅凭名称/短ID覆盖已有绑定。

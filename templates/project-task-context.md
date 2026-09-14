---
schema: pdca.project-task-context/v4
protocol_revision: 4.0.0-rc.2
task_id: null
attempt: null
project_id: null
workspace_id: null
target_root: null
pdca_root: null
records_root: null
ontology_root: null
protocol_baseline_ref: null
protocol_baseline_digest: null
manifest_ref: null
manifest_digest: null
reference_library_roots: []
record_dir: null
record_writes: []
target_writes: []
---

# 项目／任务上下文

集中保存为PDCA_ROOT/records/projects/<project_id>/workspaces/<workspace_id>/project-context.md；项目级task_id/attempt留null，任务固定其副本和摘要。pdca_root是持久集中根，records_root=PDCA_ROOT/records，ontology_root=PDCA_ROOT/ontology/projects/<project_id>；工作模型按work/revision隔离。不要在TARGET_ROOT创建流程数据目录。

PDCA_ROOT统一保存规则、本体与过程资料；protocol_baseline_ref及manifest_ref指向PDCA_ROOT/records/protocol内的固定快照，不将快照位置误作资源根。记录真实绝对路径和稳定项目／工作区身份。多个Git worktree分别登记，共享设备／库表仍进同一资源冲突范围。不要保存含密钥的整个环境。reference_library_roots只登记原参考库位置，不默认加载或授权所有内容；每任务逐项固定采用，历史执行规则不可回引。

写域列具体文件／子树，不能默认整个项目。路径规范化检查符号链接；无法访问阻断，不换根。不自动提交／覆盖／清理用户文件。

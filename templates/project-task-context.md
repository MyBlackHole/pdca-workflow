---
schema: pdca.project-task-context/v4
protocol_revision: 4.0.0-rc.1
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

项目副本保存为TARGET_ROOT/.pdca/project-context.md，project级task_id/attempt留null；任务可固定其摘要并增加自身路径。records_root默认TARGET_ROOT/.pdca，ontology_root默认其ontology目录；已有本体位置需明确采用。

PDCA_ROOT是规则包或只读固定快照，不是业务记录根。记录真实绝对路径、项目身份与版本；不要保存含密钥的整个环境。规则路径可能改变时采用项目内固定快照，哈希核验后再使用。reference_library_roots只登记原参考库位置，不默认加载或授权所有内容；每任务逐项固定采用，历史执行规则不可回引。

写域列具体文件／子树，不能默认整个项目。路径规范化检查符号链接；无法访问阻断，不换根。不自动提交／覆盖／清理用户文件。

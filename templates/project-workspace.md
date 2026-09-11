---
schema: pdca.project-workspace/v2
protocol_revision: 3.4.10
extension_revision: cross-project.2
binding_id: null
binding_revision: null
project_id: null
workspace_id: null
pdca_root: null
target_root: null
root_mode: null
target_kind: null
target_identity: {}
protocol_baseline_ref: null
protocol_baseline_digest: null
adopted_contract_ref: ontology/contracts/project-workspace.md
adopted_contract_digest: null
---

# 项目/workspace 绑定草稿

保存于 PDCA_ROOT/records/projects/<project-id>/workspaces/<workspace-id>/binding-r<revision>.md。所有空值只表示草稿；冻结前实际核验并计算摘要，引用者保存该摘要，本文件不自引用。

pdca_root/target_root由入口推导，不要求用户填写：target_root=入口真实cwd，pdca_root=非空环境配置的解析值或同一cwd。root_mode为shared（两根相同）或split（不同且互不包含）。project_id/workspace_id/binding_id 使用 `[A-Za-z0-9][A-Za-z0-9._-]*`，不能是 . 或 ..。target_kind 为 git_worktree 或 directory。

Git 的 target_identity 包含 toplevel、git_dir、common_dir（全部真实绝对路径）；普通目录包含 root。Git toplevel可为target_root的祖先，不自动扩大目标写域。project_id/workspace_id按已有精确绑定复用或PX-ID内部生成。这里只固定仓库/目录身份；每个任务当前 HEAD、branch、初始修改与依赖内容在 project-context 中固定，绑定不是永不过期的干净源码证明。

protocol_baseline_ref 为 PDCA 根内的固定协议文件路径。adopted_contract_ref 定位本次采用的[双目录契约](../ontology/contracts/project-workspace.md)，两者均使用实际 SHA-256。批准来源与真实能力在已有 CAP/RESOURCE/CONFIRM 记录中保留；binding 本身不代用户授权。

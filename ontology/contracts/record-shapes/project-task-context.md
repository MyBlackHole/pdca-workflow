---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.2
authority: normative
status: active
---

# 项目／任务上下文：记录格式

本契约定义该记录的 schema、字段与填写约束；以下完整 Markdown 示例是规范格式。字段中的 null、空列表及未验证状态表示尚未取得事实，不构成授权、执行成功或资源取得证明。按实际证据填写，保留原始来源与未知。

## 示例

```markdown
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
rules_git_head: null
rules_git_status: null
reference_library_roots: []
record_dir: null
record_writes: []
target_writes: []
---

# 项目／任务上下文

集中保存为PDCA_ROOT/records/projects/<project_id>/workspaces/<workspace_id>/project-context.md；项目级task_id/attempt留null，任务固定其副本和摘要。pdca_root是持久集中根，records_root=PDCA_ROOT/records，ontology_root=PDCA_ROOT/ontology/projects/<project_id>；工作模型按work/revision隔离。不要在TARGET_ROOT创建流程数据目录。

PDCA_ROOT 是统一保存规则、本体与过程资料的集中 Git 工作副本。新增或修改本记录须先核对用户对具体记录路径的记录写入授权。每次获准写入绑定、任务或事件前，在 PDCA_ROOT 只读执行 git rev-parse HEAD 与 git status --porcelain，分别将结果写入 rules_git_head 与 rules_git_status；干净工作树的状态为空字符串，null 仅用于尚未填写的格式示例，命令失败或无有效 HEAD 时停止，不保存为已验证绑定。状态查询可设 GIT_OPTIONAL_LOCKS=0 避免索引刷新。

Git HEAD/状态仅为写入前的追溯事实，不是不可变快照；不复制规则，不自动 checkout 历史提交。Git 提交授权与记录写入授权独立，只有用户另行明确要求提交具体范围后才执行相应 git add/commit。旧记录原字节与引用不自动改写，原依据缺失或规则冲突时停止。

记录真实绝对路径和稳定项目／工作区身份。多个 Git worktree 分别登记，共享设备／库表仍进同一资源冲突范围。不要保存含密钥的整个环境。reference_library_roots 只登记原参考库位置，不默认加载或授权所有内容；每任务逐项固定采用，历史执行规则不可回引。

写域列具体文件／子树，不能默认整个项目。路径规范化检查符号链接；无法访问阻断，不换根。不自动提交／覆盖／清理用户文件。
```

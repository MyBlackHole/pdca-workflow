---
schema: pdca.project-task-context/v2
protocol_revision: 3.4.10
extension_revision: cross-project.2
context_id: null
project_id: null
workspace_id: null
work_id: null
task_id: null
attempt: null
binding_ref: null
binding_digest: null
protocol_baseline_ref: null
protocol_baseline_digest: null
entry_context: {}
record_dir: null
work_record_dir: null
target_state: {}
input_snapshot_ref: null
input_snapshot_digest: null
record_writes: []
target_writes: []
---

# 当前 attempt 的双目录上下文草稿

保存为 PDCA_ROOT/records/<task-id>/project-context.md，内容固定后由外层 baseline/task 引用摘要。binding_ref、protocol_baseline_ref、input_snapshot_ref 都是显式 PDCA 根内路径，不相对当前命令目录解析。record_dir 必须为 records/<task-id>，work_record_dir 必须为 records/works/<work-id>；后者可只读，不自动授权写入。

entry_context固定entry_cwd、pdca_root_source（environment/entry_cwd）、pdca_root_input（只保存PDCA_ROOT原值，未设置为null，空值保留空字符串）、effective_pdca_root、effective_target_root、root_mode。首次Plan前观察；入口cwd必须等于target_root，不取之后的工具cwd。后继/派发携带并核验相同固定根，不重新根据自己的环境猜测。没有取得入口事实时保持草稿，不能默认补值制造已观察。

shared模式target_writes不得覆盖records或Git元数据，产品与资料按角色区分；不能授权整个根。Git target_state 固定 head（完整对象号）、branch（允许 detached/null）、git_dir 和 common_dir。directory 模式固定 kind=directory，不填写 Git 字段。input_snapshot 是 PDCA 内不可变清单，记录目标成员 origin/path、实际字节 SHA-256、保留位置和范围依据；不能只保留摘要而丢弃唯一旧副本。初始 tracked/未跟踪变化通过现有 subject-snapshot 的 members 固定相关原始状态/差异记录。

record_writes 为本 task 内明确相对 PDCA 的写路径或子树；不默认允许写整个 records 或 work 索引。target_writes 每项为 `{path: src, role: source}` 等具体路径；role 只接受 source/test_code/build_output/product_documentation，后者需原目标明确要求。无目标写入的建模/审查可以使用空 target_writes。路径是字面子树或文件，不是 shell glob。

同一 context 通过已有字段接入（示意值不是实算摘要）：

```yaml
# task.md 的已有 extensions 字段；ref 是相对 task.md 的通常引用。
extensions:
  project_workspace:
    context_ref: project-context.md
    context_digest: <实际SHA256>

# baseline 的已有 resource_scope：两类真实资源条目，不扩大原模板顶层字段。
resource_scope:
  - backend: filesystem
    namespace: <PDCA真实身份>
    scope: <该任务的记录子树>
    access: write
    project_context_ref: <相对baseline的context路径>
    project_context_digest: <同一实际SHA256>
  - backend: filesystem
    namespace: <目标worktree真实身份>
    scope: <逐项业务读写路径>
    access: <read或write>
    project_context_ref: <同上>
    project_context_digest: <同上>
```

baseline.constraints 正文说明资料/源码分离、初始修改保留、命令 cwd 与写域，并固定同一 context。派发的 capability-check 必须覆盖两个目录与各自权限；run.environment_ref 保存同一 context 和实际执行环境。路径和示意 scope 仍需转换为真实 RESOURCE 规范化对象，不把上述字符串当排他证明。

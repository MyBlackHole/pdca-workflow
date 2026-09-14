---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.3
authority: normative
status: active
---

# 每次正式消息／阶段／恢复的共同入口

本页是恢复与分流方法，不创建授权。只读取当前任务所需内容，勿通读整个资源库。

1. **根与项目。** 从用户指定或既有会话的集中 `records/projects/<project>/workspaces/<workspace>/project-context.md` 只读定位一个绑定，核对项目/工作区身份及真实 `target_root`、`pdca_root`、`records_root`。既有任务绑定优先于 cwd/环境变量；与 Skill 真实路径所在 Git 根冲突时停止，不能转到 TARGET_ROOT/.pdca。新增或修改绑定须按[项目契约](project-workspace.md)先取得记录写入授权；多个绑定或多个候选任务时询问，不选最新。
2. **原任务。** 读取自己的 task、dispatch 原生身份、最后完整事件、run 与待请求。阶段 Skill 收到调用但当前会话不是该执行者时，只路由真实用户操作至原实例并停止本地执行；不可路由就阻断，不重新 spawn、不由父 Agent 代做。
3. **Git 依据。** 在集中根只读执行 `GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD` 与 `GIT_OPTIONAL_LOCKS=0 git status --porcelain`，禁用可选索引写入，核对当前 HEAD/工作树状态与记录的 `rules_git_head`/`rules_git_status`；每次获准写入绑定、任务或事件前重新采集并保存。命令失败或无有效 HEAD 时停止。这些字段只作追溯，不是不可变规则快照，不复制规则或自动 checkout；发现原任务依据缺失、规则变动影响既有授权或冲突时报告并停止，不自动重写原任务。Git 提交授权独立于记录写入授权，不自动提交、拉取、切换分支、暂存、还原或覆盖。
4. **本次授权。** 核对 request/原始用户 response/消费、task/attempt/phase/run/subject 和撤销；加载 Skill、状态 running、上阶段 PASS 均不代替授权。重复回应不启动新 run；目标或输入变动先重新沟通。
5. **资源。** 按 [RESOURCE](../concept/resource-ownership.md)核对集中预约与真实后端作用域。记录和模型写入也有拥有者，不能把集中根当全局可写区。结果未知保留占用，只对账原操作。

| 事件 | 下一方法 | 停止条件 |
|---|---|---|
| 新工作明确创建 | [TASK](../concept/pdca-task.md)、[CAP](../concept/capability-protocol.md)、[派发](agent-dispatch.md) | 新 Agent 展示 Plan 目标后等待，不把创建授权当阶段批准 |
| 启动一个阶段 | [CONFIRM](../concept/pdca-ai-friendly-confirmation.md)、[GATE](../concept/pdca-gate.md)、对应阶段 Skill | 任何不匹配、能力不足或撤权则阻断 |
| 阶段完成 | 保存真实产物与完成事件，报告下一目标 | 保持最后实际阶段，awaiting_confirmation；不自动切换 |
| 恢复／压缩／重启 | [RECOVERY](../concept/pdca-recovery.md) | 原身份、状态、输入与资源不能恢复则停止 |
| 停止／取消 | [CONTROL](../concept/task-control.md)及 RESOURCE | 优先止损和结清；不需要父 Agent 循环监工 |

阶段动作、场景方法与只读辅助在 [Skill 索引](../../skills/README.md)。读场景的方法段不会再次创建任务。相同规则已读可复用；变化的 Git 状态、授权和实际资源必须重核。没有自动重载的宿主需显式调用入口，不能以文件存在承诺永不遗忘。

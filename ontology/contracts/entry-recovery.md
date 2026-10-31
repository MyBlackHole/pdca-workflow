---
schema: pdca.contract/v4
protocol_revision: 4.0.0-rc.5
authority: normative
status: active
---

# 每次正式消息／阶段／恢复的共同入口

本页是恢复与分流方法，不创建授权。按 [LOAD-MAP](../LOAD-MAP.md) 只读取当前任务与当前事件需要的规则；参考知识必须按 REUSE/ADOPT 固定版本后才进入任务输入。勿通读整个资源库。

进入绑定定位前，先按 [project-workspace](project-workspace.md) 检查身份来源。当前对话没有 `$pdca` 已核验的唯一 ID 对、当前 task 固定的唯一 ID 对，且用户本轮未明确给出唯一 `project_id`/`workspace_id` 时，立即停止并请求该 ID 对或请用户先调用 `$pdca`。项目名、工作名或 candidate 版本不足以推导 workspace。用户要求只读扫描、搜索或直接授权发现绑定，都不豁免该读取前置条件。不得先读取 `records/` 或任何父目录来发现、验证或补全绑定。身份门禁未通过时，只能输出短答：请求精确 `project_id/workspace_id`，仅续做既有 task 时请求 `task_id`，可选提示先调用 `$pdca` 核验，并说明未读 `records/`、未启动 phase；不得追加解释、根/路径事实、`TARGET_ROOT`/task 名称/记录写权限要求、records 枚举指引、业务需求发现、假设/AC/产品选项、phase 方法预告或后续步骤。

继续/恢复请求若包含多个候选 `task_id`，或用户表示无法确认原任务，必须先请求用户提供一个唯一、精确的 `task_id`。在用户明确选择前，不读取候选 task/dispatch/event 来比较或消歧，不按更新时间选择，也不通过 glob、目录枚举或猜测路径在 `records/` 中寻找候选。绑定层的 `task_id: null` 只表示该绑定未固定任务，不授权扩大搜索范围，也不能单独证明其他候选不存在。取得唯一 task ID 后，才按以下步骤读取 recovery 所需记录。

1. **根与项目。** 从用户指定或既有会话的集中 `records/projects/<project>/workspaces/<workspace>/project-context.md` 只读定位一个绑定；读取前必须按[项目契约](project-workspace.md)验证 ID 是安全单一路径组件，并对精确路径链检查规范化根和符号链接，不搜索或枚举目录。核对项目/工作区身份及真实 `target_root`、`pdca_root`、`records_root`。继续或恢复既有 task 时，task 固定的 project/workspace 身份与 `target_root` 用于定位该 task；其 `pdca_root` 和显式 `PDCA_ROOT`（若设置）仍必须规范化后与当前 Skill 入口根一致，cwd 不用于推断集中根。根冲突或无法核实时立即停止，不对候选根或 `records/` 做后续诊断，也不能转到 `TARGET_ROOT/.pdca`；后续处置遵循[项目契约](project-workspace.md)。新增或修改绑定须按[项目契约](project-workspace.md)先取得记录写入授权；多个绑定或多个候选任务时询问，不选最新。
2. **原任务。** 读取自己的 task、dispatch 原生身份、最后完整事件、run 与待请求。阶段 Skill 收到调用但当前会话不是该执行者时，只路由真实用户操作至原实例并停止本地执行；不可路由就阻断，不重新 spawn、不由父 Agent 代做。
   本步的原身份与事件连续性核对只适用于继续或恢复已定位的既有 task。没有 matching task 时，不得以无法证明不存在的原 task 连续性为阻断理由：明确的新工作请求按下表“新工作明确创建”路径处理；状态或恢复请求则报告没有 matching task，不自动创建。
3. **Git 依据。** 按 [project-workspace](project-workspace.md) 的只读 Git 快照与写记录前追溯规则，核对当前 HEAD/工作树状态和记录的 `rules_git_head`/`rules_git_status`。采集失败、原任务依据缺失，或规则变化影响既有授权/适用性时停止并报告；恢复不自动重写 task、切换历史版本或取得 Git 修改权限。
4. **待决对象。** 只定位当前 request/response/decision、task/attempt/phase/run/subject 与撤权事实；不要在 recovery 中重新解释授权。需要启动 phase 时由 CONFIRM-01 产生/核对 authorization fact，再由 GATE-01 判断当前是否 ready。
5. **未决事实索引。** 只收集 current control、reservation/operation、dependency refs，不在共同入口里重新解释它们。恢复/启动时分别交给 CONTROL-01、RESOURCE-01、DEPENDENCY-01；unknown operation 仍只对账原 operation。

| 事件 | 下一方法 | 停止条件 |
|---|---|---|
| 新工作明确创建 | 按 [LOAD-MAP](../LOAD-MAP.md) 的“新建正式任务”读取 TASK / CONTEXT / CAP / CONFIRM，再执行[派发](agent-dispatch.md) | 新 Agent 展示 Plan 目标后等待，不把创建授权当阶段批准 |
| 启动一个阶段 | 按 [LOAD-MAP](../LOAD-MAP.md) 的 phase_start 顺序执行 CONFIRM → GATE → TRANSITION → STATE，再进入对应阶段 Skill | confirmed 但 Gate 不 ready、事件写入不完整或状态投影无法回链时均不开始业务方法 |
| 阶段完成 | 按 LOAD-MAP 的 completion 顺序保存真实结果 → phase_completed → STATE 投影；Act 终态再 archived | 不自动产生下一 phase 授权或切换 phase |
| 恢复／压缩／重启 | RECOVERY-01 先判定原 task/attempt/Agent 连续性，再把 control/resource/dependency 未决事实路由给各自 authority | 原身份、事件链或关键固定 refs 无法证明连续时保持 blocked，不 spawn 替代实例 |
| 停止／取消／撤权 | CONTROL-01 决定停止约束；RESOURCE-01 根据真实 operation/ownership 事实完成 revoking → released/retained | 不因会话结束、超时或 completed 自动宣称资源已释放 |

阶段动作、场景方法与只读辅助在 [Skill 索引](../../skills/README.md)。读场景的方法段不会再次创建任务。相同规则已读可复用；变化的 Git 状态、授权和实际资源必须重核。没有自动重载的宿主需显式调用入口，不能以文件存在承诺永不遗忘。

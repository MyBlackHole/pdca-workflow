# 原生 Agent 调用语义：按需参考，不是兼容认证

仅在为实际宿主选择创建/继续方式时读取。本页不是adapter、工具Registry或新权威；TASK/CAP/RECOVERY优先。源码/官方文档查阅日期：2026-09-14；本机宿主运行验收均为 **NOT_RUN**。现场工具schema、版本、权限和初始化配置必须匹配，否则记unknown并重新核对，不按名字猜API。

## 先固定适用条件

在现有 capability-check 记录宿主/工具版本（或源码commit/blob）、模型、权限、工作区、预加载规则/记忆、实际创建/继续动作及原生回执映射。只核验实际使用的宿主，不要求加载全部产品。以下是候选语义，不是可盲目复制的完整调用命令。

| 宿主与查阅范围 | 新任务 | 原任务继续 | 特别检查 |
|---|---|---|---|
| Codex MultiAgentV2，源码commit `6f39a47bb3b04de4c804187bfbf55edc56939aab` | 所查spawn参数中显式 `fork_turns: "none"` 不走父历史fork；省略/空值默认 `all`；该V2拒绝旧 `fork_context` | 使用现场提供的原实例后续消息/继续接口，不再次spawn。保留返回路由句柄与原生thread映射 | 该快照返回task_name/nickname，并非所有宿主都直接返回thread ID；类型、名称和实例不同。V1/V2不可混用。参数不控制主动粘贴的历史 |
| Claude Code 官方subagents/skills文档，2026-09-14读到的页面 | 普通非conversation-fork子Agent拥有新上下文；Skill的 `context: fork` 文档说明不携带当前历史，与fork当前conversation不同 | 选择当前文档/工具支持可恢复的类型，并用原生标识继续；不能给四阶段分别执行新建入口 | 公共规则/预加载skills/记忆仍可能进入；检查实际初始化。前后台参数只控制等待，不证明隔离；一次性类型不足以承担完整任务 |
| OpenCode `dev` 的task.ts，Git blob `d8ca640cfba9a52d97e5180fda0ffa719910592b` | 不传task_id的分支新建child session，再向该session提交prompt | task_id指定旧session；本次实际返回session须与期望一致 | 所查代码捕获旧session查找失败后可能新建；这种返回不能叫恢复成功。parentID关联不等于复制父会话；还要检查prompt/公共输入 |

不会自动安装、更新工具或关闭权限保护。宿主只能更名、不能控制历史或继续原实例时，正式执行阻断；主Agent内联完成不算等价能力。上下文独立与写权隔离分别按CAP/RESOURCE核实。

## 已核对来源

- [Codex固定源码：V2参数解析](https://github.com/openai/codex/blob/6f39a47bb3b04de4c804187bfbf55edc56939aab/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs)（约283–348行）。
- [Claude Code：subagents](https://code.claude.com/docs/en/sub-agents)及[Skills的fork语义](https://code.claude.com/docs/en/skills)。动态页面不是固定实现；版本升级需核验。
- [OpenCode task.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/tool/task.ts)（约42–202行，查阅时Git blob如上；分支会变化）。

来源描述运行机制，不证明当前主机已正确调用。创建参数/初始化材料和本次回执必须另行保存；不得把此页或测试夹具复制成隔离证据。

# OpenCode Mini v2：真实操作与证据采集

本页是测试操作说明，不替代 CAP-01、CONFIRM-01 或正式场景验收。2026-10-22 的实测版本为
OpenCode 2.1.2，模型为 `openai/gpt-6-astra`；其他版本按现场 schema 核验。

## 启动与配置

1. 沿用已批准的 fixture、project/workspace 绑定及独立 tmux 会话，不另建业务绑定。
2. 核对 CLI 与实际 server 版本。Mini 连接指定 server 时，生效配置由 server 加载。
3. 修改模型时合并现有配置，保留 instructions、skills、permissions 和临时目录设置。
   v2 原生字段为 `permissions`、`shell`、`subagent`、`snapshots`；配置解释以现场结果为准。
4. API key 使用已有私有文件引用，不放进 prompt 或测试证据。不要直接打印完整配置 API 响应：
   服务可能已经展开文件引用。只提取需要的非敏感字段，先判断响应是对象还是数组。
5. 临时目录、缓存及输出固定在工作区；若工具仍可能写 `/tmp` 且不能改路径，则不执行。
   使用 zsh 时还要配置并验证 `TMPPREFIX`（包含文件名前缀），仅设 `TMPDIR` 不足以约束
   here-document 的临时文件。先运行无重定向的参数检查，再批准需要临时文件的命令。
   设置原生 session environment 后还要用新发起的 shell 命令验证；本次曾观察到已经等待批准的
   命令仍返回旧的 `TMPPREFIX=None`，配置写入成功不能替代执行环境证据。
   操作员侧辅助脚本也须单独设置这些环境变量；Mini 的环境不会自动传给外部驱动 shell。
   驱动提示文件优先直接写文件，避免外层未受控的 here-document。当前 fixture 提供
   `control/operator-env.sh` 供辅助命令显式继承本地临时目录。
6. Mini 显示输入提示后再用 tmux 发送文本和 Enter。启动命令返回不表示界面已接收输入；
   未观察到原生 user/inbox 消息时，不能把发送动作计为已提交。
   若文字仍停在输入框，先核对原生会话没有对应输入或活动执行，再补按 Enter；
   不重复粘贴整段 prompt。提交成功后保存输入回执，避免重复创建或重复阶段操作。

## 先核实原生接口

通过已配置的本机认证读取 server 的 `/openapi.json`，核对路径、operationId、参数和返回值。
不要用其他大版本的文档或一个 404 推断能力不存在。

| OpenCode 2.1.2 实测接口 | 证据用途 |
|---|---|
| `GET /api/session/{sessionID}` | 原生身份、父子关系、模型与 outcome |
| `GET /api/session/{sessionID}/message` | user/assistant 消息 ID、内容、时间和分页 |
| `GET /api/session/{sessionID}/context` | 核验可观察的初始输入和续接内容 |
| `POST /api/session/{sessionID}/compact`，JSON `{}` | 原生上下文压缩；本次从现场 OpenAPI 核验，属于宿主操作，不是业务 phase 批准 |
| `GET /api/event` | 实时事件、关联 sessionID、事件 ID 和顺序；断开期间事件可能丢失 |
| `POST /api/session/{sessionID}/interrupt?resume=false` | 中断运行中的实例；空闲时可能返回 interrupted=false |

业务 prompt 仍通过 tmux Mini 输入。原生 API 用于观察和操作宿主已有控制能力，不补造用户来源、
执行结果或 Agent 身份。测试操作员输入应保留其来源，不能冒充另一个真人的新批准。

## 有限、可判定的探针

- **fresh / continue**：新实例只接收固定探针；续接时不重复完整标记，核对原状态确实恢复。
- **直接通信**：连接该 child 的专用 Mini，关联本次输入、原生 message/inbox 与回复。
- **写域**：用当前模型实际暴露的原生编辑工具。GPT 本次提供 patch，限定 write 会造成假阻塞。
  分别验证允许路径的创建/读回和禁止路径的一次拒绝；拒绝后不换工具或路径重试。
- **入口读域**：检查规则文件、绑定文件和实际需要的精确目录。`directory/*` 不匹配目录自身；
  文件 canary 通过不证明任务入口所需的所有读取都可用。
  涉及写入时还需核验集中 `records/resources` 的目录及必要预约元数据读取，不能只验证当前
  workspace。测试 fixture 应明确初始化这项环境；读取预约元数据不授权读取其他任务历史，
  空目录也不证明取得资源。启动前的资源核验与写入前的再次核验应分别留证。
- **停止**：先确认目标实例的前台操作确实在运行，再调用当前版本的原生 interrupt。
  同时保留原生回执、执行中断事件和副作用停止证据。会话停止不能证明后台/远端资源已释放。
- **完成事件**：本次实测为 `session.execution.succeeded`。观测器等错事件名而超时，
  不等于执行失败；超时也不意味着任务已经取消。不得把上一轮 assistant 的成功回复当本轮结果。

## 固定与复用证据

能力记录固定版本、配置摘要、作用域、原生证据引用和限制。相关配置变化时创建新记录，
旧记录保留；只对受影响能力重验。提供按 claim 定位的简短索引，保留原始事件供核查，
避免每次 task creation 都把所有历史 transcript 注入模型。

阶段输入也应有小型原生回执：观察器收到匹配 session 和完整输入文字的
`session.inbox.enqueued` 后，保存原生 inbox/message ID、event ID、顺序与原文，
让执行实例引用精确文件及字段。不要只记录“本会话当前消息”，也不要为了定位一条输入
传入完整历史。观察器只保存宿主事实，不判断 CONFIRM 授权、不认证另一位真人；
历史记录保持原字节，后取到的来源证据作为补充。

发送前检查提示是否误含不可见格式字符。本次 `U+200B` 被 Mini 从单词中移到文本末尾，
导致完整文本匹配失败、回执未保存；不能据此断言输入未送达，更不能直接重发创建请求。
应核对已保存的原生 event 与文字差异，将实际接收原文另存为明确标注的补充回执，
再续接同一请求。观察器不应静默清洗原文后声称逐字匹配；当前驱动会在发送前拒绝这类字符。

某次创建遇到拒绝后，原入口停止。操作员修复获准环境、取得新证据后，重新进入原创建事务；
不得重复消费授权、偷偷更换 attempt 或把原未执行的 task 说成已经运行。

## 阻塞式新建会话的交接顺序

本次原生 subagent 调用会等待 child 的首轮结果，父端在返回前不能把实际 sessionID 填回 task。
因此首轮应核对固定输入并返回可观察的绑定事实；尚待父端落盘的身份不是 phase 启动依据。
父端保存真实调用、回执与身份后，如仍缺少绑定证据，就只续接原实例完成只读核对，再对账同一
创建事务。accepted 后才展示/保存待批准 Plan 对象，不把 Plan 产物当作 accepted 的前置条件。

另需分别表达任务允许边界与本次操作授权。产品候选已有明确边界时，不应仅因尚未启动 Do 就
把 assignment 的产品写域清空。记录可预先限定到具名 task/attempt 的命名空间，各 phase 再
单独固定具体产物；保留原交接和历史版本，不靠未来 Plan 静默扩大空边界。

环境能力通过只说明能进行相应操作。H11 仍需真实 Model→Implement→Verify 产物、行为与反例证据。
不以 canary、模型自述或文档检查替代本体符合性验收。

官方参考：[v2 API](https://opencode.ai/v2/docs/api)、
[v2 配置](https://opencode.ai/v2/docs/config)、
[v2 权限](https://opencode.ai/v2/docs/permissions)。

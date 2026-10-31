# OpenCode user-message provenance boundary

日期：2026-09-27

本记录继续收紧 OpenCode v1.18.32 的 CAP-01 边界：已经证明 session 可持久化、可显式续接并可由宿主 export 两条 user-role 消息，但 **OpenCode 自身的 persisted UserMessage 不提供真人来源/入口路由 provenance**。因此 `role: "user"` 不能单独证明“这条消息由实际用户直接发给该实例”。

这不是 OpenCode 不可用的结论，而是当前证据能证明什么、不能证明什么的界限。

## 对应运行时证据

基于 PR #46 合并前最终 Actions run `36324060053` 的 artifact：

- OpenCode: `v1.18.32`
- model: `opencode/mimo-v2.6-flash-free`
- continued session: `ses_f1cd6db6fffe4NSGvIZjAp2een`
- `same_session: true`
- `prior_state_recovered: true`
- `repository_tools_not_used: true`
- `user_turn_count: 2`
- `second_user_reinjects_runtime_token: false`
- `second_assistant_recovers_runtime_token: true`

宿主 export 的两条 user message 的 `info` 字段实际都只有：

```text
agent
id
model
role
sessionID
summary
time
```

例如第一条 user message 的信息包含：

```text
role      = user
agent     = build
sessionID = ses_f1cd6db6fffe4NSGvIZjAp2een
model     = opencode/mimo-v2.6-flash-free
time      = <created timestamp>
```

它没有保存可把该消息绑定到“真人直接输入”的 sender / actor / ingress / transport / channel / UI receipt。

## v1.18.32 schema 交叉核对

OpenCode 源码 commit：

`b471c2b4495747353af768fbf2e0790c9d820ce2`

其 `packages/opencode/package.json` 标明版本 `1.18.32`。

同一 commit 的 `packages/schema/src/v1/session.ts` 中，`UserMessage` schema 定义的宿主字段为：

```text
id
sessionID
role = "user"
time.created
format?
summary?
agent
model
system?
tools?
```

这里同样没有外部发送者身份、真人来源、调用入口或传输路由字段。

因此 runtime export 与版本源码相互一致：

```text
role=user
  !=
proven-human-origin
```

## CAP-01 影响

CAP-01 的 `communicate` 要求是：

> 用户消息能到达该实例，来源和路由可核查；父 Agent 转述不能冒充用户。

当前 OpenCode CI/CLI 证据已经能证明：

```text
prompt submitted
  -> persisted as user-role message
  -> bound to expected sessionID
  -> assistant response persisted
  -> same session can continue
```

但不能从 OpenCode session store 本身证明：

```text
this prompt
  -> originated from a specific real user action
  -> entered through the intended interactive route
  -> was not injected by CI/API/parent automation
```

所以在正式 task 创建前，若实际接入路径没有额外的原生 receipt/audit/event 能把真实用户动作绑定到 message/session，`communicate` 的“来源可核查”部分必须保持 `unknown`，不能因为 export 里写了 `role=user` 就升级为 PASS。

## 现场验收怎么处理

正式现场实验不需要新增 adapter 或第二套协议。继续使用现有 CAP-01 / capability-check：

1. 先记录实际接入路径，而不是只写“OpenCode”：
   - 本地交互 CLI；
   - TUI/桌面端；
   - server/API；
   - 其他宿主集成。
2. 采集该路径真实提供的 input/receipt/event。
3. 证明一次实际用户动作与接收它的 session/message 之间存在可核验绑定。
4. 再用 session/export 证明同一 message/session 被持久化并能继续。
5. 如果接入路径没有可核验的来源绑定，就把 limitation 写入 capability-check，并在正式 dispatch 前停止。

屏幕上出现一句话、Agent 自述“这是用户发的”、`role=user`、一个 session ID 或父 Agent 转述都不能补齐这项证据。

## 对 H10 / H18 的影响

本发现不会回退已经取得的 session-continuation/transcript 证据，但它说明为什么这些证据仍不能单独完成 H10/H18：

- H10 还需要正式 task/attempt、原实例绑定、未决请求以及真实用户继续动作的对账；
- H18 还需要用户对具名 child creation 的真实授权、TASK/CONTEXT/CAP/CONFIRM/dispatch receipt，以及 child 自己展示 Plan 后等待；
- CI 生成的 user-role 消息不能被重新解释成这些真实用户操作。

因此 H1-H18 状态继续保持 `NOT_RUN`。

## 结论

截至 2026-09-27，OpenCode v1.18.32 已具备很强的 session identity / persistence / continuation 可观察性，但 **该版本的 session transcript 不携带足以单独证明真人消息来源的 provenance**。

下一次正式现场验收的关键问题已经从“OpenCode 能不能续接会话”收敛为：

> 实际使用的 OpenCode 接入路径，能否提供独立证据把真人操作绑定到对应 session/message？

只有这个问题在现场得到肯定证据后，CAP-01 的 `communicate` 才能从当前的环境级部分证据继续向正式 task creation 前提推进。

针对 OpenCode v1.18.32 的交互 TUI，后续现场路径已经收敛为
[OpenCode 交互 TUI 消息来源现场探针](../../tests/opencode-interactive-provenance.md)：
由真人提交一次性 challenge，独立记录 TUI 输入动作，再与该版本实际
`submit -> session.create(必要时) -> session.prompt` 路由和 host-side export 对账。
该探针仍需现场执行，不能由文档或 CI 替代。

后续源码核对还确认：v1.18.32 当前 TUI 的 `client.session.prompt()` 仍走 legacy
`POST /session/{sessionID}/message`；真正带 durable admission receipt 的
`client.v2.session.prompt()` 是另一条 `POST /api/session/{sessionID}/prompt` 路径。
OpenCode 自身测试明确要求 legacy prompt 不产生任何 `session.next.*` event。
因此当前 TUI 不能用 `session.next.prompt.admitted` 代替真人输入证据；见
[OpenCode TUI admission-event boundary](2026-09-28-opencode-tui-admission-boundary.md)。

继续核对 TUI hook 后也没有找到可替代真人输入证据的原生 outbound receipt：
`session_prompt.onSubmit` 是无参数回调且在 prompt 清空后调用；
`tui.command.execute` / `tui.prompt.append` 是 server/HTTP -> TUI 的入站控制事件。
因此现场 probe 仍采用“独立 TTY input evidence + 当前版本 submit route + host export”三方对账。
Linux/util-linux 的具体无秘密 input-logging 步骤已经写入
[OpenCode 交互 TUI 消息来源现场探针](../../tests/opencode-interactive-provenance.md)。

进一步核对 TUI 的 `session.export` 后，现场对账不再需要从近期 session 排序猜 ID：
v1.18.32 的 `formatTranscript()` 会把完整 `Session ID` 写入当前 TUI 的 Markdown export。
因此 probe 在收到 challenge ACK 后只执行内置 `/export`（不是第二条业务消息），
再用该文件中的完整 ID 调用 `opencode export <exact-id>` 获取 host-side JSON。
TUI probe 同时覆盖 `VISUAL=true EDITOR=true`，因为 v1.18.32 的 `openEditor()` 按
`VISUAL || EDITOR` 选择外部编辑器；只覆盖 `EDITOR` 不能保证无交互。

## 2026-10-20：v2.0.32 路由与导出更新

本机现装 OpenCode 为 `v2.0.32`。复核上游 tag `v2.0.32`，commit 为
`843a6c514e606b436a7fe713422ace0a93ad3d61`。此前正文中的 legacy route、没有
`session.next.*` 事件、文件名和 `VISUAL` 处理结论均只适用于 v1.18.32，不能拿来解释当前 TUI。

v2.0.32 当前 TUI 提交路径为：

```text
Prompt.submitInner() 读取 input.plainText
  -> 无 session 时 data.session.create(...)
  -> data.session.prompt({ sessionID, text, ... })
  -> POST /api/session/{sessionID}/prompt
  -> durable inbox admission / enqueued echo
```

来源：上游固定版本的
[`prompt/index.tsx`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/tui/src/component/prompt/index.tsx)、
[`solid/data.ts`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/client/src/solid/data.ts)、
[`generated/client.ts`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/client/src/promise/generated/client.ts)
和 [`session-message.ts`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/schema/src/session-message.ts)。
`SessionMessage.User` schema 有 id、可选 metadata、创建时间、text/files/agents/skills 与 `type=user`，但没有专用外部 actor/ingress/TTY receipt 字段；当前 TUI prompt caller 不传 metadata。插件仍可能写入通用 metadata，但除非来源有独立可信约束，它也不能证明真人身份。新的 durable inbox admission 能支持“prompt 已被接收”的核验，不证明提交者身份。

v2.0.32 TUI 的 `/export` 会读取当前 session ID 并调用 `client.api.session.export()`，Markdown formatter 写入完整 `Session ID`。保存流程现在打开选项对话框，并把 Markdown 写入 `node:os.tmpdir()` 下的随机 `session-<uuid>.md`，而非 v1.18.32 的默认 `session-<id-prefix>.md` 路径；POSIX 上可在启动 TUI 前设置 `TMPDIR` 将其重定向到工作区测试目录。现场 probe 必须核验结果对话框给出的精确路径确实位于该目录，再复制到私有证据目录。实现见上游固定版本的
[`routes/session/index.tsx`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/tui/src/routes/session/index.tsx)。

本机 v2.0.32 synthetic TUI continuation probe 曾由 Agent 注入两条输入，并成功导出 transcript。这只验证了当前 TUI 会话续接和导出操作；没有证明真人来源，不能把 CAP-01 `communicate` 升为 PASS。现场步骤已更新至
[OpenCode 交互 TUI 消息来源现场探针](../../tests/opencode-interactive-provenance.md)。

同日又在专用 tmux session 中重新打开该 synthetic TUI session，执行 `/export` 并选择 Markdown / save to file：结果对话框给出临时路径，文件在继承 `umask 077` 后为 mode `0600`，正文含完整 session ID 与 synthetic challenge。随后用 v2.0.32 的 `opencode session export <session-id>` 读取 host JSON；核验结果为 session ID 匹配、2 条 user、2 条 assistant、恰好 1 条 user 含该 challenge。TUI export 与 JSON 分别保存在 `/tmp/pdca-v2032-export-doc-check-20261020/tui-session.md`、`/tmp/pdca-session-export-v2032.json`，原始 TUI export 也保存在 `/tmp/session-6ee2933b-c0a3-4499-9e4c-a6323b863916.md`；相关文件均限制为当前用户可读。challenge SHA-256：`ed63a696d37ea8be0a1e912e103ee4b8eefd9241599ec314cc81ebfdc95f4051`。

该次操作通过 tmux 自动化完成，输入本来就是 synthetic；它验证 `/export` 的保存路径、权限和新 CLI host export 的 session/message 对账步骤，**不**是物理真人输入，也不改变 probe `NOT_RUN`、CAP-01 `communicate` `unknown` 或 H1-H18 `NOT_RUN`。

## 2026-10-21：v2.1.1 工作区路径与 umask 实测

在本机 OpenCode v2.1.1 的专用 tmux 会话中，对已有 synthetic session 只执行 `/export`，没有提交新的业务 prompt。先将 `TMPDIR` 指向工作区 `tests/` 下的私有目录；TUI 实际保存到该目录中的 `session-<uuid>.md`，没有写到系统临时目录。首次启动未设置 `umask 077` 时，新文件为 `0644`；按现场步骤重跑并在启动前设置 `umask 077` 后，新文件为 `0600`。后一次导出文件为 32,557 字节，路径及模式在清理前核验；TUI 退出且确认没有进程占用后，已删除本轮导出和 Bun 临时缓存。

这次 Agent 通过 tmux 操作、复用 synthetic session 的实测只验证 v2.1.1 的 `TMPDIR` 路径和文件权限，不验证 export 正文与 host JSON 的对账，也不证明真人来源；probe、CAP-01 `communicate` 与 H1-H18 状态均不变。

# OpenCode 交互 TUI 消息来源现场探针

**状态：未执行（NOT_RUN）。**

本探针只验证 CAP-01 的 `communicate` 中最难的一项：

> 一次实际用户动作，是否能被可靠地绑定到 OpenCode 中接收它的 session / user message。

它不是正式 PDCA task，不创建 task/attempt/assignment/dispatch，不启动 Plan，也不把任何 H 项升级为 PASS。
实际 authority 仍来自 [CAP-01](../ontology/concept/capability-protocol.md) 与
[host-acceptance](host-acceptance.md)。

## 1. 为什么需要这个探针

已有维护级运行证据已经证明 OpenCode v1.18.32 可以：

- 发现并加载 `pdca` Skill；
- 创建 fresh session；
- 通过 `--session` 续接同一 session；
- 在 `session list` 中持久化该 session；
- 通过 `opencode export <session-id>` 导出 `info/messages`；
- 保留两条 user-role 消息、native Skill tool assistant message 与 final assistant response；
- 在第二条 user 没有重新注入 runtime token 的情况下，从原 session 历史恢复 token。

但 v1.18.32 的 persisted UserMessage 没有 sender/actor/ingress/transport provenance。
因此：

```text
export 里的 role=user
  !=
这条消息已证明由真人在交互 TUI 直接提交
```

本探针补的正是这条连接。

维护级来源边界见：

- [OpenCode user-message provenance boundary](../docs/reviews/2026-09-27-opencode-user-message-provenance.md)
- [OpenCode persisted session transcript](../docs/reviews/2026-09-27-opencode-session-transcript.md)

## 2. v1.18.32 的 TUI 路由事实

本探针依赖的版本级源码依据是 OpenCode commit：

`b471c2b4495747353af768fbf2e0790c9d820ce2`

其 `packages/opencode/package.json` 标记版本为 `1.18.32`。

同一 revision 的：

`packages/tui/src/component/prompt/index.tsx`

在普通文本 prompt 的 submit 路径中：

1. 从当前交互 prompt 读取 `store.prompt.input` / editor text；
2. 如果还没有 session，则调用 `sdk.client.session.create(...)`；
3. 得到或复用当前 `sessionID`；
4. 调用：

```text
sdk.client.session.prompt({
  sessionID,
  agent,
  model,
  parts: [
    ...,
    { type: "text", text: inputText },
    ...
  ]
})
```

5. 清空当前 prompt 并触发 UI 的 `onSubmit`。

这说明实际 TUI 的正常提交路由确实是：

```text
interactive prompt input
  -> TUI submit()
  -> current/new sessionID
  -> sdk.client.session.prompt(...)
  -> persisted user message
```

但 submit 处没有保存“真人 actor”字段；因此仍需要独立记录真人输入动作，再与 host export 对账。

### 2.1 现有 TUI hook 不能替代真人来源证据

OpenCode v1.18.32 还暴露了几个看似相关、但不足以充当提交 receipt 的接口：

- `session_prompt.onSubmit` / `PromptProps.onSubmit` 是**无参数回调**；
- Prompt 的实现是在已经清空当前 prompt state 之后才调用 `props.onSubmit?.()`，因此该回调本身没有本次提交的 text/messageID；
- `tui.command.execute` 是 server/HTTP 发布给 TUI 的**入站控制事件**，TUI 收到后执行指定 command；它不是用户按下 submit 时自动发出的出站审计事件；
- `tui.prompt.append` 也是把文本追加到 TUI prompt 的入站事件，不是用户输入记录。

因此本探针不安装 plugin/adaptor 去“补” provenance，也不把这些接口改写成真人提交回执。当前版本仍需要一个与 OpenCode session store 独立的真实 TTY 输入证据。


### 2.2 不要把 V2 admission event 套到当前 TUI

OpenCode v1.18.32 的生成客户端同时包含 legacy Session 与真正 V2 Session 两套 API：

```text
当前 TUI 使用:
client.session.prompt()
  -> POST /session/{sessionID}/message

真正 V2 durable admission:
client.v2.session.prompt()
  -> POST /api/session/{sessionID}/prompt
  -> admittedSeq / session.next.prompt.admitted
```

OpenCode 自身测试还明确验证：

```text
legacy prompt emits message events without session.next events
```

因此本探针**不得**把 `session.next.prompt.admitted`、`admittedSeq` 或 V2 prompt receipt
当成 v1.18.32 当前交互 TUI 的提交证据。详细来源见
[OpenCode v1.18.32 TUI admission-event boundary](../docs/reviews/2026-09-28-opencode-tui-admission-boundary.md)。

如果未来 TUI 真正切到 `client.v2.session.prompt()`，必须按新版本/新配置重新取证，不能沿用本结论。

## 3. 探针前提

仅在以下条件同时满足时执行：

- 使用真实交互 TUI，不使用 `opencode run`；
- OpenCode 版本明确记录；
- TARGET_ROOT 是无生产数据的试验目录；
- 本轮不授权产品代码、网络发布、业务设备或生产数据写入；
- 用户明确批准一次**无业务写入的能力探针**；
- 没有父 Agent、CI、REST API、SDK、shell pipe 或 stdin 自动注入 prompt；
- challenge 在提交前不写入仓库、ontology、Skill、prompt 文件或环境变量。

如果实际使用的是桌面端、server/API 或其他接入路径，不套用本 TUI 结论；为该路径单独采证。

## 4. 一次性 challenge

在 OpenCode TUI 之外生成一个无敏感含义、一次性的随机 challenge，例如：

```text
PDCA-HUMAN-PROBE-<128-bit random hex>
```

challenge 的要求：

- 本次 probe 唯一；
- 生成后由操作员看到；
- 不提前写入 TARGET_ROOT / PDCA_ROOT；
- 不作为 OpenCode 启动参数；
- 不通过 API 或脚本发送给 OpenCode；
- 公共摘要只需保存 digest；原值只保存在获准的私有探针材料中。

生成 challenge 本身不是 PDCA 授权，也不能预先包含“开始 Plan/Do/Check/Act”等未来批准语句。

## 5. 实际用户动作

### 5.1 启动前记录

在真实终端记录：

- 当前时间；
- `tty`；
- TARGET_ROOT 绝对路径；
- `opencode --version`；
- OpenCode 启动方式；
- 当前 relevant config / memory / instruction 设置；
- 当前没有自动 prompt 注入机制的事实。

然后**人工启动交互式 `opencode` TUI**。

不要使用：

```text
opencode run ...
echo ... | opencode ...
REST /session/:id/message
REST /session/:id/prompt_async
SDK session.prompt(...)
父 Agent 转述
CI 模拟 role=user
```

这些路径可以创建 user-role 消息，但不能证明本探针要求的真人 TUI 来源。

### 5.2 独立记录 TUI 输入

操作员需要保留一个与 OpenCode session store 独立的、时间相邻的 TUI 输入证据。

可接受形式取决于现场环境，例如：

- 终端自身的会话录制；
- OS/终端审计；
- 由操作员保留的原始屏幕/输入录制；
- 其他能够显示“该 challenge 是在这个交互 TTY 的 OpenCode prompt 中由用户提交”的证据。

该材料只用于本次无敏感 probe。不要在存在密码、token 或业务秘密的终端开启全量输入记录。

**不能只用 OpenCode export 代替这一步**，因为 export 自身没有 human-origin provenance。

#### Linux / util-linux 推荐做法

如果现场 Linux 的 util-linux `script` 支持 `--log-in`，可以在一个**专门用于本探针、不会出现密码/token/业务秘密**的终端中保存独立输入日志。

先确认当前 `script` 支持 input logging：

```sh
script --help | grep -F -- '--log-in'
```

没有该选项时不要退化成普通 output-only `script` 并宣称已记录用户输入；改用终端/OS 的独立录制方式。

建议在 TARGET_ROOT / PDCA_ROOT **之外**建立仅当前用户可读的临时证据目录：

```sh
probe_dir="$(mktemp -d)"
chmod 700 "$probe_dir"

challenge="PDCA-HUMAN-PROBE-$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
printf '%s\n' "$challenge" >"$probe_dir/challenge.txt"
printf '%s' "$challenge" | sha256sum >"$probe_dir/challenge.sha256"

{
    date --iso-8601=seconds
    tty
    pwd -P
    opencode --version
} >"$probe_dir/preflight.txt"

printf 'Probe directory: %s\nChallenge: %s\n' "$probe_dir" "$challenge"
```

然后从这个专用终端启动交互 TUI，并同时记录输入、输出和 timing：

```sh
script -q -e \
    --log-in "$probe_dir/input.log" \
    --log-out "$probe_dir/output.log" \
    --log-timing "$probe_dir/timing.log" \
    -c 'opencode'
```

`--log-in` 会记录该伪终端会话中的**全部输入**，包括终端关闭 echo 时输入的内容。因此：

- 这次录制只能用于无秘密 probe；
- TUI 若出现登录、密码、token、sudo 或其他敏感输入提示，立即退出，不在该录制会话中输入凭据；
- 不把 `input.log` / `output.log` 提交到公共 Git；
- probe 完成后按本次 evidence retention 约定保留或安全删除原始日志。

退出 TUI 后，先在私有证据目录验证 exact challenge 确实出现在独立 input log：

```sh
LC_ALL=C grep -aF -- "$challenge" "$probe_dir/input.log"
```

该命中只证明 challenge 经过这个录制的 TTY 输入流；最终仍需与 OpenCode host-side export 的 session/message/time 做后续对账。

### 5.3 用户手工提交

用户在 TUI prompt 中手工键入或人工粘贴：

```text
PDCA provenance probe only.
Challenge: <exact challenge>
Return exactly: ACK:<exact challenge>
Do not modify files. Do not start any PDCA phase.
```

然后由用户实际触发 TUI 的 submit。

这条消息不是 task creation，也不是 phase_start。

收到 assistant 回应后停止，不自动发送第二条业务消息。

## 6. Host-side 对账

在不修改 session 的情况下，使用 OpenCode 自身的只读能力：

```sh
opencode session list --max-count 10 --format json
opencode export <candidate-session-id>
```

如果同时存在多个近期 session，只能通过本次唯一 challenge 与时间窗口定位；
不得凭“最新 session”猜测。

在 export 中必须找到唯一对应 user message，并记录：

- `info.id`；
- `info.sessionID`；
- `info.time.created`；
- `info.agent`；
- `info.model`；
- user text part 中的 exact challenge；
- 后续 assistant message/part；
- session 的创建/更新时间；
- challenge digest。

原始 export 保存在获准的私有证据位置；公共 PR 不提交不必要的完整 transcript。

## 7. 三方交叉核验

本探针不是依赖某一个信号，而是核对三个相互独立的层次：

### A. 真人动作证据

证明：

```text
real operator
  -> interactive OpenCode TUI prompt
  -> submitted exact challenge
```

### B. TUI 路由证据

按当前版本实际实现确认：

```text
TUI submit
  -> session.create if needed
  -> client.session.prompt(sessionID, parts)
  -> legacy POST /session/{sessionID}/message
```

源码事实不能单独证明本次真人输入，但可以解释输入从 TUI 到 session 的真实 route。

### C. Host persistence 证据

证明：

```text
same exact challenge
  -> one persisted user message
  -> expected sessionID/messageID/time
  -> assistant response in same session
```

只有 A+B+C 能相互对上，才有资格把这次 `communicate` 来源/路由证据提交给现场 Check。

## 8. 必须核对的反证

至少主动排除：

- challenge 在提交前已经存在于仓库文件；
- challenge 出现在环境变量、prompt file 或启动参数；
- 使用了 `opencode run`；
- 使用了 REST/SDK 自动提交；
- 父 Agent 代发；
- 录制材料与 export 的 challenge 不一致；
- 录制时间与 exported user message 时间无法合理对应；
- 同一 challenge 出现在多个 session；
- session ID 是根据“最新”猜出来，而不是 challenge 对账；
- TUI 版本与用于解释 route 的源码版本不一致或无法说明；
- 用户只看到 assistant 回答，却没有输入动作的独立证据；
- 只记录 TUI output、没有独立 input stream，却声称已证明真人输入；
- input recorder 会话中出现密码/token 等敏感输入，导致证据本身不适合保留或发布；
- 把 `session_prompt.onSubmit`、`tui.command.execute`、`tui.prompt.append` 当成当前用户提交的 provenance receipt；
- 把 `session.next.prompt.admitted` 或 V2 `admittedSeq` 当成当前 v1.18.32 TUI 的 receipt。

任一关键点无法排除，结果保持 `unknown`。

## 9. 结果记录

本探针完成后使用已有
[capability-check](../ontology/contracts/record-shapes/capability-check.md)
保存证据引用，不新增 schema。

如果此时 project/workspace 绑定已经按用户授权持久化，环境级结果写入同一绑定目录的
`capability-checks/<record-ref>.md`；如果尚未绑定，只保留获准的私有 probe 原始材料并保持结果未持久化，
先回到 [host-smoke](host-smoke.md) 的绑定步骤。不得为了保存本探针自行创建 `records/capabilities/`
或根据 TARGET_ROOT / cwd 猜 project/workspace。

建议记录的语义是：

```text
scope:
  OpenCode <version>
  interactive TUI
  exact relevant config

communicate:
  human_input_observed: pass | unknown
  route_to_session_supported_by_version_source: pass | unknown
  persisted_user_message_match: pass | unknown
  session_binding: pass | unknown
  limitation: ...

result:
  pass | unknown | blocked
```

这些只是 capability evidence；不是 task dispatch receipt。

## 10. 通过后仍不能自动做什么

即使本探针得到充分证据，也只说明当前 OpenCode TUI/配置下的 `communicate` 来源与路由具备可核验性。

它**不会自动授权**：

- 创建 root task；
- 创建 child task；
- 启动 Plan；
- 启动 Do/Check/Act；
- 固定 ontology/tree/node；
- 修改业务文件；
- 将 H10/H18 整项标记 PASS。

下一步仍必须回到 [host-smoke](host-smoke.md)，由用户针对实际具名对象逐次授权。

## 11. 当前状态

本文只是可执行探针说明。

截至本文创建时：

```text
interactive TUI provenance probe = NOT_RUN
CAP-01 communicate human-origin = still not established by this document
H1-H18 = unchanged
```

不要把文档存在、源码审查或之前的 CI transcript probe 改写成“真人 TUI 已验证”。

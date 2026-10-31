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

另一次 v2.0.32 维护级 TUI 续接与导出只使用了 Agent 注入的输入，没有真人键入证据，不能算作本探针执行。

v1.18.32 与 v2.0.32 的 TUI 提交 API 已不同，但两版的 user-message 记录都不能单独证明真人来源：v1.18.32 的 UserMessage 没有 sender/actor/ingress/transport provenance；v2.0.32 的 User schema 也没有专用的来源字段，且当前 TUI prompt 路径不传来源 metadata。
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

## 2. 按版本核对 TUI 提交路由

### 2.1 OpenCode v1.18.32

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

### 2.2 OpenCode v2.0.32

本机已安装版本为 `opencode v2.0.32`。对应源码 tag 指向 commit：

`843a6c514e606b436a7fe713422ace0a93ad3d61`

`packages/tui/package.json` 标记版本为 `2.0.32`。该 revision 的 TUI submit 路径位于
[`prompt/index.tsx`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/tui/src/component/prompt/index.tsx)，数据层与 endpoint 分别见
[`solid/data.ts`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/client/src/solid/data.ts) 和
[`generated/client.ts`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/client/src/promise/generated/client.ts)：

1. `submitInner()` 同步读取 prompt editor 的 `input.plainText`；
2. 没有当前 session 时调用 `data.session.create(...)`，否则沿用当前 session ID；
3. 普通 prompt 经 `data.session.prompt({ sessionID, text, ... })` 发送；
4. client 将该调用发送到 `POST /api/session/{sessionID}/prompt`，由 durable inbox 处理。

该版本的 `PromptProps.onSubmit` 仍是无参数回调，而且在 composer 清空后调用。`SessionMessage.User`
的固定字段是 id、可选 metadata、创建时间、text/files/agents/skills 和 `type=user`；没有专用真人 actor、ingress 或 TTY receipt 字段。当前 TUI 的 `data.session.prompt()` 调用没有传入 metadata；即使插件提供通用 metadata，也不能单独证明真人身份或 TTY 来源。

因此 v2.0.32 的路径可核对 prompt 到 session 的 admission 与持久化，不能单独证明 prompt 是真人在 TUI 输入。

### 2.3 现有 TUI hook 不能替代真人来源证据

OpenCode v1.18.32 还暴露了几个看似相关、但不足以充当提交 receipt 的接口：

- `session_prompt.onSubmit` / `PromptProps.onSubmit` 是**无参数回调**；
- Prompt 的实现是在已经清空当前 prompt state 之后才调用 `props.onSubmit?.()`，因此该回调本身没有本次提交的 text/messageID；
- `tui.command.execute` 是 server/HTTP 发布给 TUI 的**入站控制事件**，TUI 收到后执行指定 command；它不是用户按下 submit 时自动发出的出站审计事件；
- `tui.prompt.append` 也是把文本追加到 TUI prompt 的入站事件，不是用户输入记录。

v2.0.32 的 `PromptProps.onSubmit` 也没有参数，并在 prompt state 清空后触发；它同样不能提供本次 text、message ID 或真人身份。因此本探针不安装 plugin/adaptor 去“补” provenance，也不把这些接口改写成真人提交回执。当前版本仍需要一个与 OpenCode session store 独立的真实 TTY 输入证据。


### 2.4 Admission receipt 仍不是真人来源证据

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
当成 v1.18.32 当前交互 TUI 的提交证据。v2.0.32 当前 TUI 已使用 `/api/session/{sessionID}/prompt` 的 durable inbox admission 路径；相应 admission 事件最多证明一条 prompt 被接收，仍不能证明是谁在 TUI 输入。详细来源见
[OpenCode v1.18.32 TUI admission-event boundary](../docs/reviews/2026-09-28-opencode-tui-admission-boundary.md)。

版本、配置或 TUI route 改变时，必须按当前源码重新取证，不能沿用旧版本的路由结论。

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

然后由操作员**在该终端人工启动交互式 `opencode` TUI**。本探针要求真人在操作终端直接键入或手工粘贴 challenge 并触发 submit；父 Agent 使用 `tmux send-keys`、脚本或其他自动化方式注入 challenge，只能作为 TUI 路由模拟，不能把 A 项真人动作证据标记为通过。

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

- 能同时识别操作员、目标 TTY 与键入/手工粘贴及 submit 动作的同期观察记录或录制；
- 能把登录用户和该 TTY 输入事件绑定起来的 OS/终端审计；
- 其他能够支持“这名操作员在这个交互 TTY 的 OpenCode prompt 中提交了该 challenge”的证据。

只显示 TUI 输出或只记录 PTY 输入字节的材料，不识别实际输入者，不能单独把 human-origin 标为通过。`script --log-in` 可作为输入字节的补充记录，不能替代操作者来源证据。

该材料只用于本次无敏感 probe。不要在存在密码、token 或业务秘密的终端开启全量输入记录。

**不能只用 OpenCode export 代替这一步**，因为 export 自身没有 human-origin provenance。

#### Linux / util-linux 推荐做法

如果现场 Linux 的 util-linux `script` 支持 `--log-in`，可以在一个**专门用于本探针、不会出现密码/token/业务秘密**的终端中保存独立输入日志。

先确认当前 `script` 支持 input logging：

```sh
script --help | grep -F -- '--log-in'
```

没有该选项时不要退化成普通 output-only `script` 并宣称已记录用户输入；改用终端/OS 的独立录制方式。

在当前工作区已有的 `tests/` 输出目录中创建仅当前用户可读的临时证据目录。v2.0.32 的 TUI 导出实现调用 `node:os.tmpdir()`；在 POSIX 上该 API 尊重 `TMPDIR`，因此必须在启动 TUI 前将它指向工作区内的专用目录。若工作区的 `tests/` 实际解析到 `/tmp`，停止探针，不改用系统临时目录。

```sh
set -eu
umask 077
pdca_root="$(git rev-parse --show-toplevel)"
test_output_dir="$(realpath -e "$pdca_root/tests")"
case "$test_output_dir" in
    /tmp|/tmp/*)
        printf 'tests output directory resolves under /tmp; refusing to run: %s\n' "$test_output_dir" >&2
        exit 1
        ;;
esac
probe_dir="$(mktemp -d "$test_output_dir/opencode-provenance.XXXXXXXX")"
chmod 700 "$probe_dir"
mkdir -m 700 "$probe_dir/tmp"
export TMPDIR="$(realpath -e "$probe_dir/tmp")"
case "$TMPDIR" in
    /tmp|/tmp/*)
        printf 'TMPDIR resolves under /tmp; refusing to run: %s\n' "$TMPDIR" >&2
        exit 1
        ;;
esac

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
cd "$probe_dir"

script -q -e \
    --log-in "$probe_dir/input.log" \
    --log-out "$probe_dir/output.log" \
    --log-timing "$probe_dir/timing.log" \
    -c 'VISUAL=true EDITOR=true opencode'
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
`script --log-in` 不认证输入来源，tmux/程序注入也会成为 PTY 输入字节。只有操作员亲自操作且该动作有独立观察或记录时，A 项才可能通过；仅有 `input.log` 与 transcript 时，真人来源仍为 `unknown`。

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

收到 assistant 回应后，**不要发送第二条业务消息**。接着在同一个 TUI 中执行内置：

```text
/export
```

按实际版本完成导出：

- **v1.18.32：**选择保存并保留 `session-<id-prefix>.md` 文件名。为避免外部编辑器，启动命令覆盖 `VISUAL=true EDITOR=true`；该版本 `openEditor()` 按 `VISUAL || EDITOR` 选择编辑器。导出文件应落在私有 `probe_dir`。
- **v2.0.32：**`/export` 打开导出选项。选择 Markdown 和 **save to file**，不要选择 copy。OpenCode 在固定源码中使用 `node:os.tmpdir()` 构造导出路径，因此 TUI 应把文件写到启动前设置的 `$TMPDIR`。结果对话框显示实际路径；确认它位于 `$probe_dir/tmp/`，记录该精确路径，退出 TUI 后按下节复制到私有 `probe_dir`。若实际路径不在该目录，停止，不读取、复制或清理该文件。启动前设置的 `umask 077` 会限制本次 TUI 创建文件的权限。

v2.0.32 的 TUI Markdown formatter 与保存路径实现见上游固定版本的
[`routes/session/index.tsx`](https://github.com/anomalyco/opencode/blob/843a6c514e606b436a7fe713422ace0a93ad3d61/packages/tui/src/routes/session/index.tsx)。

两版的 TUI Markdown transcript formatter 都会在导出正文首部写入：

```text
**Session ID:** <完整 session id>
```

所以这个 TUI 原生导出可把“当前正在操作的会话”绑定到完整 session ID，
无需退出后按“最近会话”猜测候选。

完成 `/export` 后退出 TUI。

## 6. Host-side 精确对账

退出 TUI 后，先把 TUI Markdown export 放入私有 probe 目录，统一命名为 `tui-session.md`：

- v1.18.32：将该版本保存在 `probe_dir` 中的 `session-*.md` 文件移入/复制为该路径；
- v2.0.32：使用导出结果对话框显示的**精确路径**作为 `tui_export_source`，并先确认其规范化路径仍在 `$probe_dir/tmp/`，再执行：

```sh
set -eu
tui_export_source="$probe_dir/tmp/session-<uuid>.md" # 替换为 TUI 结果对话框显示的精确路径
tui_export_source="$(realpath -e "$tui_export_source")"
case "$tui_export_source" in
    "$probe_dir"/tmp/session-*.md) ;;
    *) printf 'TUI export is outside the workspace TMPDIR; stopping: %s\n' "$tui_export_source" >&2; exit 1 ;;
esac
cp -- "$tui_export_source" "$probe_dir/tui-session.md"
chmod 600 "$probe_dir/tui-session.md"
```

确认没有其他 TUI export 被误认为本次结果，并核对该文件包含本次 challenge。随后按固定文件名读取：

```sh
tui_export="$probe_dir/tui-session.md"
[ -f "$tui_export" ] || {
    printf 'Missing saved TUI session export: %s\n' "$tui_export" >&2
    false
}

session_id="$(
    sed -n 's/^\*\*Session ID:\*\* //p' "$tui_export" | head -n 1
)"
case "$session_id" in
    ses_*) ;;
    *)
        printf 'Invalid or missing Session ID in %s\n' "$tui_export" >&2
        false
        ;;
esac

LC_ALL=C grep -aF -- "$challenge" "$tui_export"
printf 'Exact TUI session: %s\n' "$session_id"
```

这里的 `session_id` 来自**当前 TUI 自己导出的 transcript**，不是从 session list 的排序推测。

再用同一个完整 ID 读取 OpenCode host-side JSON：

```sh
opencode session list --max-count 10 --format json >"$probe_dir/session-list.json"
LC_ALL=C grep -aF -- "$session_id" "$probe_dir/session-list.json"

case "$(opencode --version)" in
    *v1.18.32*) opencode export "$session_id" >"$probe_dir/session.json" ;;
    *v2.0.32*) opencode session export "$session_id" >"$probe_dir/session.json" ;;
    *) printf 'Unverified OpenCode export command for %s\n' "$(opencode --version)" >&2; false ;;
esac
LC_ALL=C grep -aF -- "$challenge" "$probe_dir/session.json"
```

如果 session list 的窗口不足以包含该 ID，不因此换成另一个“最新 session”；
按当前版本执行的 exact-ID host export 与 TUI export 仍是主要对账对象，并把 list limitation 记录下来。

在 host export 中必须确认 `export.info.id == session_id`，并找到唯一对应的 user message。
逐版本记录 message identity 与内容：

- **v1.18.32：**user message 的 `info.id`、`info.sessionID`、`info.time.created`、`info.agent`、`info.model`、`info.role=user` 及对应 text part；
- **v2.0.32：**user message 的 `id`、`type=user`、`time.created` 和 `text`。此版本 message 没有单独的 `sessionID` 字段，通过外层 `export.info.id` 将整个 `messages` 集合绑定到 session；
- 两版都记录后续 assistant message/part、外层 session 创建/更新时间和 challenge digest。

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

独立记录必须支持操作员确实亲自在 TUI 提交 challenge。PTY input log 本身只证明字节到达 TUI 所在的终端，不识别键盘操作人与 `tmux send-keys` / 其他注入者；无法独立核实操作者时，A 保持 `unknown`。

### B. TUI 路由证据

按当前版本实际实现确认：

```text
v1.18.32:
  TUI submit
  -> session.create if needed
  -> client.session.prompt(sessionID, parts)
  -> POST /session/{sessionID}/message

v2.0.32:
  TUI submitInner()
  -> data.session.create if needed
  -> data.session.prompt({ sessionID, text, ... })
  -> POST /api/session/{sessionID}/prompt
  -> durable inbox admission
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
- session ID 是根据“最新”猜出来，而不是当前 TUI `/export` 正文中的完整 ID；
- TUI 导出没有保存、保存到了业务目录，或同一 probe 目录出现多个无法唯一归属的 `session-*.md`；
- TUI 版本与用于解释 route 的源码版本不一致或无法说明；
- 用户只看到 assistant 回答，却没有输入动作的独立证据；
- 只记录 TUI output、没有独立 input stream，却声称已证明真人输入；
- input recorder 会话中出现密码/token 等敏感输入，导致证据本身不适合保留或发布；
- 把 `session_prompt.onSubmit`、`tui.command.execute`、`tui.prompt.append` 当成当前用户提交的 provenance receipt；
- 对 v1.18.32，把 `session.next.prompt.admitted` 或 V2 `admittedSeq` 当成当前 legacy TUI 的 receipt；对 v2.0.32，把 durable inbox admission 当成真人来源证明。

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

截至 2026-10-20：

```text
interactive TUI provenance probe = NOT_RUN
CAP-01 communicate human-origin = still not established by this document
H1-H18 = unchanged
```

不要把文档存在、源码审查或之前的 CI transcript probe 改写成“真人 TUI 已验证”。

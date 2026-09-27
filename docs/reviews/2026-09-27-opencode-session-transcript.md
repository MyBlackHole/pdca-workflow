# OpenCode persisted session transcript review

日期：2026-09-27

这是 OpenCode v1.18.32 的 **pre-host-acceptance runtime evidence**。目标是把“模型在第二轮说它记得第一轮”升级为宿主侧持久化 session / transcript 证据；它仍不创建正式 PDCA task，也不把 H10/H18 升级为 PASS。

## Runtime evidence

- GitHub Actions run: `36323676205`
- job: `108632229723`
- OpenCode: `v1.18.32`
- model: `opencode/mimo-v2.6-flash-free`
- continued session: `ses_f1cdcb49dffeC2rmdLe2kLkgSK`
- runtime token SHA-256: `d67d878a4df051917709353a072b8fea534a80fc0ec0aa68980677ef3760b013`
- transcript step success marker:
  `OpenCode persisted the continued session as an ordered two-turn user/assistant transcript`

同一 run 中，前置 `Probe explicit OpenCode session continuation` 也再次满足：

```text
same_session: true
prior_state_recovered: true
repository_tools_not_used: true
```

## Host-side checks

continuation 完成后，不再询问模型“你是不是同一会话”，而是直接调用 OpenCode CLI：

```text
opencode session list --max-count 20 --format json
opencode export <continued-session-id>
```

CI 对 host-side JSON 做以下硬断言：

1. session list 中存在前一轮取得的真实 session ID；
2. export 顶层结构是 `info + messages`；
3. `export.info.id` 精确等于 continued session ID；
4. export 中恰好出现两条 user turn；
5. 第一条 user turn 包含只在运行时生成的 opaque token；
6. 第二条 user turn不包含该 token，因此 continuation prompt 没有重新注入答案；
7. 第二条 user turn 之后的 final assistant 精确恢复 token 与 continuation state；
8. 第一条与第二条 user turn 之间允许 OpenCode 为原生 tool call 产生 assistant 消息，不把 tool 消息误当成新的用户回合。

## Observed native message sequence

本次真实 export 的 role sequence 为：

```text
user
assistant    # native skill tool step
assistant    # first final answer
user
assistant    # continued final answer
```

结构化 summary：

```text
session_list_contains_session: true
export_contains_session_id: true
export_top_level_keys: [info, messages]
ordered_two_turn_transcript: true
user_turn_count: 2
assistant_messages_between_turns: 2
assistant_messages_after_second_turn: 1
first_user_contains_runtime_token: true
second_user_reinjects_runtime_token: false
second_assistant_recovers_runtime_token: true
```

这也解释了为什么 transcript 不能简单强制相邻的
`user -> assistant -> user -> assistant`：OpenCode 会把 native `skill(pdca)` tool interaction 持久化为独立 assistant message。测试按真实 host schema 识别 user turn boundary，并选择每轮最后的 assistant text 作为 final response。

## Evidence chain now established

截至本轮，OpenCode 维护级 runtime evidence 已覆盖：

```text
install.sh
  -> global Skill discovery
  -> native skill(pdca) load
  -> fresh session identity
  -> ontology semantic recovery
  -> minimum child-context recovery without repository reads
  -> explicit --session continuation
  -> same native session identity
  -> prior in-session state recovery
  -> session list persistence
  -> host-side exported ordered transcript
  -> proof that turn 2 did not receive the runtime token again
```

因此“第二轮恢复第一轮状态”不再只由模型最终回答支撑；OpenCode 自己的 session store/export 同时记录了两条真实 user turn 和对应 assistant/tool/final 消息。

## Acceptance boundary

这仍然不是正式 H10/H18：

- CI 发出的两条 prompt 不是用户对一个正式 PDCA task 的真实 `phase_start`；
- 没有 TASK-01 task/attempt 与 fixed assignment/baseline/context refs；
- 没有真实用户消息来源、UI/transport routing receipt；
- 没有任务级 suspend/control、未决 request、资源与写域对账；
- 没有 Modeling Act-fixed model root/tree/node；
- 没有 DECOMP-produced fixed child seed；
- 没有 TASK/CONTEXT/CAP/CONFIRM/agent-dispatch 创建的 child；
- 没有 child 展示自己的 Plan 目标并等待用户。

所以 `tests/host-acceptance.md` 的 H1-H18 保持原状态。该结果可作为未来 CAP-01 / RECOVERY-01 现场核验的环境级证据，但不能代替 task-level invocation receipt。

## CI policy

该 transcript probe 依赖前面的 public free-model continuation，因此保持 `continue-on-error`；公共端点失败时不能否定稳定 CLI compatibility。

当 continuation 成功时，不能仅以 Actions step 的绿色状态宣称 transcript PASS，因为 `continue-on-error` 会掩盖命令退出码。维护审查必须核对结构化 summary 或日志中的明确 success marker。

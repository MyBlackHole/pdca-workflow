# OpenCode v1.18.32 TUI admission-event boundary

日期：2026-09-28

本记录回答一个具体问题：

> 能否用 `session.next.prompt.admitted` 作为 OpenCode v1.18.32 交互 TUI 中“用户刚刚提交了这条 prompt”的原生 durable receipt？

结论：**不能。**

该事件属于真正的 V2 Session prompt 路径；当前 v1.18.32 TUI 的普通 prompt 仍走 legacy Session message endpoint。

## 版本与源码依据

检查的 OpenCode revision：

`b471c2b4495747353af768fbf2e0790c9d820ce2`

其 `packages/opencode/package.json` 标记版本：

`1.18.32`

## TUI 实际调用

`packages/tui/src/component/prompt/index.tsx` 使用：

`@opencode-ai/sdk/v2`

并在普通文本 submit 中调用：

```text
sdk.client.session.prompt({
  sessionID,
  ...
  parts: [
    { type: "text", text: inputText },
    ...
  ]
})
```

虽然 package 名包含 `sdk/v2`，但这里的 `client.session` 并不是 V2 durable Session API。

生成客户端 `packages/sdk/js/src/v2/gen/sdk.gen.ts` 中：

```text
OpencodeClient.session
  -> Session2
```

而 `Session2.prompt()` 实际请求：

```text
POST /session/{sessionID}/message
```

这是 legacy message route。

## 真正的 V2 prompt 是另一命名空间

同一生成客户端还有：

```text
OpencodeClient.v2
  -> V2

V2.session
  -> Session3
```

`Session3.prompt()` 才请求：

```text
POST /api/session/{sessionID}/prompt
```

其语义明确是：

> Durably admit one session input...

该 API 返回包含 `admittedSeq` 的 Session input admission receipt，并对应
`session.next.prompt.admitted` durable event。

所以不能因为 TUI import 了 `@opencode-ai/sdk/v2` 就推导“TUI prompt 走 V2 durable admission”。

## OpenCode 自身测试的直接反证

同一 revision 的：

`packages/opencode/test/session/prompt.test.ts`

包含测试：

```text
legacy prompt emits message events without session.next events
```

测试要求 legacy prompt：

- 有普通 message update/part update 事件；
- 但：

```text
seen.filter(type => type.startsWith("session.next.")) == []
```

这直接否定了把当前 legacy TUI prompt 与
`session.next.prompt.admitted`
绑定起来的做法。

## V1/V2 bridge 也不能补成 admission receipt

V2 设计文档说明，V1-to-V2 shadow bridge 面向已经可见的 V1 prompt 时，处理的是
`Prompted` 语义，而不是把原始 V1 提交重新解释成一个可供客户端依赖的
`PromptAdmitted` receipt。

因此：

```text
legacy TUI user message persisted
  !=
V2 PromptAdmitted observed for that submission
```

## 对 PDCA 现场探针的影响

[OpenCode 交互 TUI 消息来源现场探针](../../tests/opencode-interactive-provenance.md)
不能依赖：

- `session.next.prompt.admitted`；
- `admittedSeq`；
- V2 `/api/session/:sessionID/prompt` receipt；

来证明当前 v1.18.32 TUI 的真人提交。

当前仍应使用三层交叉证据：

```text
A. 真人 TUI 输入动作的独立证据
B. v1.18.32 TUI submit -> legacy session.prompt/message route 源码依据
C. host-side session/export 中 exact challenge 的持久化 user message
```

如果未来 OpenCode TUI 切换到真正的 `client.v2.session.prompt()`，
可以重新评估 durable admission receipt 是否能够替代部分外部 route 证据；
不能把未来/其他接入路径的能力倒推到 v1.18.32 当前 TUI。

## Acceptance boundary

该发现只收紧取证方式：

- 不执行真人 TUI probe；
- 不改变 CAP-01；
- 不创建 task；
- 不产生 phase authorization；
- 不改变 H1-H18 的 `NOT_RUN` 状态。

它防止后续验收错误地使用一个当前 TUI 实际不会产生的 V2 event 来宣称 `communicate` 已通过。

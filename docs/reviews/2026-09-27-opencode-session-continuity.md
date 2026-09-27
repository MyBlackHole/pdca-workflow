# OpenCode explicit session-continuity runtime review

日期：2026-09-27

这是 CAP-01 / RECOVERY-01 相关的 **pre-host-acceptance runtime evidence**。它验证 OpenCode CLI 的指定 session 续接原语，但不创建正式 PDCA task，不模拟用户授权，也不把 H10/H18 升级为 PASS。

## Runtime evidence

- OpenCode: `v1.18.32`
- GitHub Actions run: `36322454175`
- job: `108628778609`
- step: `Probe explicit OpenCode session continuation`
- model: `opencode/mimo-v2.6-flash-free`
- first/continued session: `ses_f1cf20554ffeHXsYmYk1pbUR1w`
- runtime token SHA-256: `3914f97e8d30e9a2a0b36f4aa46fd5b17304678c7987317a1dd1511fdbaf030b`

工作流整体与该步骤均为 `success`。

## Probe shape

第一轮通过普通 `opencode run` 创建 fresh session。测试在 Actions job 内临时生成随机 opaque token；该 token 不存在于仓库提交中，也不从 ontology/Skill 文件读取。

第一轮要求模型：

1. 通过 OpenCode native `skill` tool 加载 `pdca`；
2. 不修改文件、不读取/搜索仓库；
3. 保留 runtime token；
4. 返回状态 `waiting_for_followup`。

CI 从 JSON event stream 取得唯一真实 session ID，并验证第一轮最终状态与 runtime token 一致。

第二轮没有再次把 token 放进 prompt，而是执行：

```text
opencode run --session <first-session-id> ...
```

第二轮要求从同一会话历史恢复 token 与前一状态，并返回 `continued_original_session`。

## Hard assertions

成功结果同时满足：

```text
same_session: true
prior_state_recovered: true
repository_tools_not_used: true
```

具体断言包括：

- 第二轮所有 event 中的 `sessionID` 必须仍等于第一轮真实 ID；
- 第二轮必须精确恢复只出现在第一轮消息中的 runtime token；
- 第二轮必须恢复 `waiting_for_followup`；
- read/glob/grep/bash 等 repository/file/search 访问都会使 probe 失败；
- summary 只持久化 token digest，不需要把 token 本身作为长期证据。

因此，这比“两个 fresh run 有不同 session ID”多证明了一层：

```text
fresh session creation
  -> persisted OpenCode session
  -> explicit --session continuation
  -> same native session identity
  -> prior in-session state recoverable
```

## What this improves

此前证据已经覆盖：

- OpenCode 能发现并加载九个 PDCA runtime Skills；
- public model 能真实调用 `skill(pdca)`；
- 两个 fresh session 可从 ontology core 恢复等价语义；
- minimum child context 可以在不读取仓库的情况下恢复同一 child semantics。

本轮补上 **指定原 session 的真实 continuation primitive**，因此后续正式宿主验收不再需要把“OpenCode CLI 是否存在可工作的 session continuation”作为完全未知能力。

## What this does not prove

它仍不是正式 PDCA recovery / H10 / H18：

- 两轮消息由 CI probe 驱动，不是实际用户对正式 task 的逐次 `phase_start`；
- 没有 TASK-01 task/attempt；
- 没有 fixed assignment / baseline / context refs；
- 没有核验真实用户消息来源和 communicate routing；
- 没有正式 suspend/control、未决请求、资源或写域对账；
- 没有 Modeling Act-fixed model root/tree/node；
- 没有 DECOMP child seed、agent-dispatch receipt 或 child Plan wait；
- 没有 host-level hidden memory / instruction inheritance inspection。

所以 `tests/host-acceptance.md` 的 H1-H18 保持原状态；本结果只能作为未来现场 CAP-01 / continuation 核验的环境级候选证据。

## CI policy

session-continuity probe 使用公共免费模型，因此和现有 model probes 一样保持 `continue-on-error`。公共免费端点暂时不可用时不能据此否定稳定的 CLI Skill compatibility；但一旦 probe 成功，其 session identity、state recovery 与 tool-boundary assertion 必须全部满足。

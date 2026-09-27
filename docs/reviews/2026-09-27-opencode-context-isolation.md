# OpenCode minimum child-context isolation review

日期：2026-09-27

这是 CONTEXT-01 的维护级 pre-H18 runtime evidence，不是正式 task assignment、Modeling Act fixation 或 H18 PASS。

## Runtime evidence

- OpenCode: `v1.18.32`
- GitHub Actions run: `36320667769`
- job: `108623745345`
- model run 1: `opencode/mimo-v2.6-flash-free`
- model run 2: `opencode/mimo-v2.6-flash-free`
- session 1: `ses_f1d0eff01ffeZo16Bu6E37dTnU`
- session 2: `ses_f1d0ea01dffelvoeU757jIZu6q`

两个 session ID 不同，且都没有使用 `--continue` 或复用既有 session。

## Test target

目标不是再次恢复整棵 bounded-counter work projection，而是验证 CONTEXT-01 的核心边界：

> 一个 child initial context 应足以执行当前责任，同时默认不携带 parent/sibling 完整活动历史或无关 ontology branch。

测试对象是 bounded-counter 的 label child candidate：

`NODE-LABEL / INST-LABEL`

candidate 本身仍 `fixed_by_modeling_act: false`，所以这里只验证 context selection semantics，不把它升级成正式 task。

## Minimum context supplied

测试输入只包含：

- current node identity / responsibility / I/O / AC-oracle anchor；
- `DEF-LABEL` / `INST-LABEL`；
- direct parent identity `INST-SYSTEM` 与 `REL-COMP-SYSTEM-LABEL` boundary；
- producer endpoint identity `INST-COUNTER`；
- `REL-CONSUMES-LEGAL-READING` 与 `legal_count_value` interface；
- `C-LABEL` / `C-LABEL-INPUT`；
- `REQ-LABEL-001` / `REQ-COMP-001`；
- dependency `not_fixed / ready=false` limitation。

没有把整个 model root、整个 TREE、counter node contract 或父任务历史传给 child。

## Explicit exclusions

测试输入明确排除：

- `DEF-COUNTER` full definition；
- counter increment semantics / `C-INC`；
- counter reset semantics / `C-RESET`；
- `C-INIT` / `C-READ` implementation details；
- `NODE-COUNTER` full work-node contract；
- sibling task conversation/history；
- parent Plan/Do/Check/Act activity history；
- unrelated ontology branches；
- implementation artifacts；
- behavior evidence。

模型被明确要求不能用常识或假设补齐这些缺失内容。

## Native Skill usage

两次运行都必须先通过 OpenCode native `skill` tool 加载 `pdca`。

CI 在 JSON event stream 中验证 Skill tool call，缺少 `pdca` Skill use 即失败。

两个运行均通过。

## Required semantic output

每个 session 必须恢复：

```text
current node       = NODE-LABEL
work instance      = INST-LABEL
input interface    = legal_count_value
producer endpoint  = INST-COUNTER
constraints        = {C-LABEL, C-LABEL-INPUT}
requirements       = {REQ-LABEL-001, REQ-COMP-001}
dependency ready   = false
```

同时必须把以下状态保持为：

```text
counter increment semantics = not_in_context
counter reset semantics     = not_in_context
parent activity history     = not_in_context
sibling full context        = not_in_context
```

## Result

两个独立 session 的 normalized output 完全一致：

```json
{
  "current_node": "NODE-LABEL",
  "work_instance": "INST-LABEL",
  "input_interface": "legal_count_value",
  "producer_endpoint": "INST-COUNTER",
  "constraints": ["C-LABEL", "C-LABEL-INPUT"],
  "requirements": ["REQ-COMP-001", "REQ-LABEL-001"],
  "dependency_ready": false,
  "excluded": {
    "counter_increment_semantics": "not_in_context",
    "counter_reset_semantics": "not_in_context",
    "parent_activity_history": "not_in_context",
    "sibling_full_context": "not_in_context"
  }
}
```

workflow 同时记录：

```text
same_semantics: true
different_sessions: true
excluded_context_respected: true
```

并输出：

`two fresh OpenCode sessions respected the same minimum label-child context`

## Why this matters

此前 fresh-session recovery 已经证明：

```text
ontology core
  -> equivalent TREE / dependency / responsibility semantics
```

本轮进一步证明，在这个 synthetic bounded-counter case 中，不必把整个 ontology/model/parent history 交给 child：

```text
current node
+ direct parent boundary
+ necessary relation endpoint
+ required dependency interface
+ current constraints/requirements
  -> sufficient child semantics
```

同时被排除的 counter internals 与 parent/sibling activity history 没有被模型补造成当前事实。

这直接支持 CONTEXT-01 的设计：

> relation 存在不等于读取另一端全部内容；只取完成当前语义所需的端点定义或固定交付。

## What this does not prove

仍然缺少正式 H18 所要求的生命周期事实：

- user-authorized formal root Modeling task；
- Modeling Plan/Do/Check/Act receipts；
- Act-fixed payload digest / tree revision / node IDs；
- DECOMP-produced fixed task seed；
- TASK/CONTEXT/CAP/CONFIRM/dispatch-created child task；
- real assignment record proving exactly what host initialized；
- hidden host memory/instruction inheritance inspection；
- parent/child activity-history isolation at native host transport level。

因此本结果是 **pre-H18 minimum-context runtime evidence**，不是 H18 acceptance。

H1–H18 状态保持不变。

## CI policy

该 probe 使用公共免费模型，因此保持 non-blocking；免费 endpoint 的暂时不可用不能使稳定 CLI compatibility gate 失败。

当 probe 成功时，其结构化 assertion 是强约束：模型必须使用 `pdca` Skill、恢复当前 child semantics、保持 dependency `ready=false`，并明确尊重 excluded-context contract。

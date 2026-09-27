---
schema: pdca.asset/v2
id: ontology:concept/pdca-gate
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: GATE-01：判断一个固定 phase_start 此刻能否开始
---

# GATE-01：Phase start 资格判断

GATE-01 只回答：**这个已经被用户授权的固定 phase_start，在当前真实状态下是否可以开始。**
它不产生用户授权、不写 transition，也不直接修改 task 状态。

## 通用 Gate

对单个 task/attempt/phase/run/subject 同时核对：

1. **identity**：task、attempt、scene、原 Agent/conversation 与目标 run 匹配；
2. **authorization**：存在 CONFIRM-01 产生的、匹配当前固定对象且未撤销的 positive decision；
3. **predecessor**：TRANSITION-01 的完整事件链满足该 phase 的前置顺序；
4. **freshness**：subject、固定输入、baseline/dependency/version 未发生使原授权失效的变化；
5. **control**：没有已生效的 cancel/revoke/stopping 条件；
6. **resources/capability**：本 phase 实际需要的写域、资源、工具和宿主能力当前可用。

任何一项 unknown / 不满足，都只阻断本次 phase_start；不能自动换目标、放宽 oracle、重建 Agent 或产生新授权。

## Phase 特有前提

| phase | 附加前提 |
|---|---|
| Plan | task 已创建并绑定原 Agent；固定目标/seed/范围足以开始计划，不要求 Plan 已有产物 |
| Do | 对应 Plan run 已完成；当前 Plan/baseline、AC/oracle 和获准写域与 request 一致 |
| Check | 对应 Do run 已完成；待审最终产物/版本、固定 AC/oracle 与证据对象一致 |
| Act | 当前 Check 结果与被处置产物一致；用户授权的处置/发布/知识范围明确 |

Check 后返工不是 TRANSITION 的隐式自动边。目标/oracle/Agent 未变化且 REWORK-01 条件成立时，
新的用户 Do phase_start 可以再次经过本 Gate；发生需要新 attempt 的变化时，旧 attempt 不通过。

## 结果

Gate 只有两类语义结果：

- **ready**：当前固定 phase_start 可以写 `phase_started`；
- **blocked**：列出不满足/unknown 的前提，保持现有事件和授权历史不变。

ready 不是 running。只有 TRANSITION-01 成功记录匹配的 `phase_started` 后，
STATE-01 才能把 task 投影为 running。

阶段内已经授权范围中的普通工具步骤不逐项重新过 phase Gate；
目标、oracle、写域、固定对象或新的不可逆副作用发生实质变化时，回到 CONFIRM/GATE。

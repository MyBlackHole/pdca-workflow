---
schema: pdca.asset/v2
id: ontology:concept/task-rework
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: REWORK-01：判断 Check 后是同 attempt 新 Do，还是必须新 attempt/task
---

# REWORK-01：Check 后返工资格

REWORK-01 只回答：**当前 Check 之后，修复是否仍可在同一 task/attempt/Agent 中通过新的 Do run 完成。**
它不启动 Do、不创建新 attempt/task，也不修改 Check 结论。

## Same-attempt rework

只有下列固定语义仍成立时，才可以把修复作为同一 attempt 的新 Do candidate：

- task / scene / node / ontology identity 不变；
- 原 Agent/conversation 仍可继续；
- Plan 的目标、non-goals、baseline、required actions 与 AC/oracle 不变；
- 修复仍落在原 Plan 已固定的可变对象/写域/资源边界内；
- dependency/model version 没有要求替换当前 fixed input；
- 当前 attempt 尚未 archived/completed。

满足时：

1. 保留原 Check fail/unknown 与旧 Do run；
2. 形成具名 rework Do candidate，不改写原 verdict；
3. 用户必须针对新的 Do run 重新给出 phase_start；
4. GATE-01 重新检查 freshness/control/resource/capability；
5. 新 Do 完成后必须重新 Check；旧 Check/证据不能覆盖新 subject。

**同-attempt rework 不先进入 Act。** Act 是当前 attempt 的终态处置；如果先完成 Act/archived，就不能再回到同一 attempt 的 Do。

## Must start a new attempt/task

出现以下任一类变化时，同-attempt rework 不成立：

- 目标、non-goals、AC/oracle 或 Plan baseline 需要实质改变；
- node/ontology/definition revision 需要替换当前 fixed identity/input；
- 需要新的 Agent；
- 修复超出原 write/resource boundary；
- 当前 attempt 已 terminal；
- verification 发现的是被审 implementation/model 的独立后续工作，而不是当前 verify task 自身可修对象。

这时 REWORK 只产生“需要新 attempt/task”的候选说明。
旧 attempt 如何停止/归档按 CONTROL/Act/TASK 处理；新 attempt/task 的创建仍由 TASK-01 / CONFIRM-01 / agent-dispatch 完成。

## Phase 内调试

Do run 内、原目标和边界未变的必要调试/重试属于当前 Do 自主执行，不是 Check 后 rework。
保留失败 observation 与 stopping budget；unknown side effect 按 RESOURCE/operation 对账，不用“返工”掩盖重复副作用。

---
name: pdca-act
description: 用户明确批准现有 PDCA 任务的 Act 终态处置时使用。不用于同 attempt 返工，也不启动下一场景。
metadata:
  version: 5.0.0-rc.2
---

# Act：执行终态处置并封存当前 attempt

## 进入 Act

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。当前会话不是原任务执行者时，
只路由真实用户操作回原 Agent；不可路由就阻断。

如果 Check 后用户选择的是 **同-attempt rework**，先按 REWORK-01 判断资格；成立时应进入新的 Do request，
**不要进入 Act**。Act 只处理当前 attempt 的终态处置。

真正进入 Act 时，按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的 phase_start 链核对当前 Check predecessor、
固定处置 subject/version、用户授权范围及资源条件，并写入 `phase_started(act)`。
读取[Act 方法](../../ontology/process/flow-act.md)与 [SCENE-01](../../ontology/process/work-scenarios.md) 当前 scene 章节；
学习、发布、资源等额外规则只在本次处置真实涉及时按需读取。

## 本阶段动作

只执行用户此次明确批准的终态动作，例如接受/限制性接受交付、fail/unknown 归档、
获准 artifact/model 发布、资源结清，或明确授权的 learning/shared reference 写入。

“同意”“可以”不能扩大成额外知识写入、共享发布、项目 context 更新或未来任务创建。
如 Check 结论建议后续新 attempt/task，只在当前归档中保存候选说明；Act 不创建或调度它。

保留 Check 的真实 conformance：风险接受、失败归档和发布都不能把 fail/unknown 改成 PASS。
`delivery_usable` 由本次实际处置/限制决定；未知副作用先按 RESOURCE/operation 对账。

## 完成与停止

固定最终 delivery、模型/mapping/implementation refs、处置/发布 evidence、资源结果和 scene coverage 后，
按 LOAD-MAP 的 completion 链写 `phase_completed(act)`；同一授权下完成 terminalization，写 `archived`，
STATE 投影 completed/archive。

完成后停止。当前 attempt 不再回 Do；任何新 attempt、task、scene 或共享知识的后续采用都需要各自新的用户操作。

---
schema: pdca.asset/v2
id: ontology:concept/work-tree-scheduling
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-27'
summary: SCHED-01：从 fixed task seeds 与 dependency ready 形成创建候选
---

# SCHED-01：Task creation candidate ordering

SCHED-01 只回答：**哪些已经存在的 fixed task seed 此刻可被提示给用户创建，以及候选之间有什么顺序约束。**
它不调度 phase、rework、新 attempt、资源取得，也不自动 spawn。

## 输入

只消费已有事实：

- DECOMP-01 已形成的 fixed task seed；
- TREE-01 的 composition；
- DEPENDENCY-01 的 ready/stale；
- SCENE-01 的 scene obligation；
- 当前已存在 task 的 terminal/未创建事实。

SCHED 不重新验证 deliverable/version，不读取依赖 task 完整活动历史，也不创建新的 node/seed。

## 输出

输出少量具名 creation candidates，可说明：

- candidate task/scene；
- 依赖为什么 ready 或仍 blocked；
- composition/scene 顺序依据；
- 需要用户执行的 work_action。

多个已定义 candidate 可以作为一个**候选批次**展示，但批次本身不是授权。
真正创建仍由用户明确 work_action → TASK/CONTEXT/CAP/CONFIRM → agent-dispatch。

## 边界

- “ready”“父/子完成”“还有容量”都不触发自动 spawn；
- phase 是否可启动只由 CONFIRM/GATE 决定；
- Check 后是否同-attempt rework 只由 REWORK-01 判断；
- 新 attempt 是 TASK/REWORK/CONFIRM 的生命周期问题，不是 scheduler 决策；
- RESOURCE-01 决定真实共享资源资格；SCHED 不为了并行度改变资源保证；
- task A 等待用户不阻止无冲突且已获准的 task B，但父 Agent 不轮询监工或催报进度。

SCHED 是候选排序/呈现规则，不是长期运行的调度器。

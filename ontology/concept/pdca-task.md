---
schema: pdca.asset/v2
id: ontology:concept/pdca-task
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-27'
summary: TASK-01：任务是固定本体工作节点在一个场景中的独立执行实例
---

# TASK-01：任务的语义身份与生命周期

Task 不是任意 prompt，也不是执行步骤的容器。除唯一 root modeling bootstrap 外，
正式 task 是**一个固定 ontology/work node 在一个 scene、一个 attempt 中的独立执行实例**。

## 语义身份

普通 task 的核心身份由固定的：

- project/work；
- ontology revision / tree revision / node；
- scene；
- attempt

共同确定。节点 responsibility、I/O、constraints、AC/oracle 及依赖必须能回到该固定模型身份。
精确持久化字段只以 [task record](../contracts/record-shapes/task.md) 为准；本页不再复制 schema 字段表。

同一个 node 的 model / implement / verify 是不同 scene task，但保持同一语义节点。
后续 scene 不得静默重定义 node responsibility，也不能把不同 ontology revision 当作同一输入。

## 唯一 bootstrap 例外

首次 root modeling 尚无 ontology node/revision，因此允许唯一 root modeling bootstrap task：

- 固定用户确认的 root goal seed；
- node / ontology revision 等尚未形成的字段保持真实 null/空；
- 不以占位 node/revision 冒充模型；
- bootstrap 只负责建立第一个 root node/revision，不能据此创建 child/implement/verify task。

root modeling Act 固定首个 node/revision 后，后续正式 task 全部回到普通 ontology-backed 规则。

## Task 与执行者

每个正式 task/attempt 绑定一个真实、可交互的执行 Agent；同一 attempt 的 Plan→Do→Check→Act
保持该原 Agent。新进程或压缩可以恢复原实例，但不能用新 spawn 冒充恢复。

需要更换执行者时，先安全结束原 attempt，再由用户明确创建新 attempt。
宿主是否具备这种能力只由 CAP-01 判断；如何原生创建只由 agent-dispatch 处理。

## 创建、上下文与阶段

- task 是否创建：按 CONFIRM-01 的具名 work action，由用户决定；
- task 初始上下文：按 CONTEXT-01 选择 minimum sufficient context；
- task 原生创建：按 agent-dispatch；
- task 恢复：按 RECOVERY-01 / entry-recovery；
- phase 启动与推进：按 CONFIRM-01 / GATE-01 / TRANSITION-01。

创建 task 不启动 Plan；task ready、依赖 ready 或上阶段 PASS 也不产生未来 phase 授权。
任务执行中若发现新的 ontology responsibility，只能先形成 EVOLVE/TREE/NODE candidate；经 Modeling Check/Act 固定为正式 node 后，才由 DECOMP-01 形成后续 task seed candidate。任何 task 都不能把草稿责任直接变成后代任务。

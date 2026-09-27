---
schema: pdca.asset/v2
id: ontology:concept/pdca-recovery
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-27'
summary: RECOVERY-01：恢复原 task/attempt/Agent 连续性，不重演业务规则
---

# RECOVERY-01：恢复连续性

RECOVERY-01 只回答：**当前是否还能继续原 task / attempt / Agent，以及恢复后应该把哪些未决事实交给哪条现有规则。**
它不重新解释用户授权，不重新判断资源 ownership，不重算 dependency ready，也不创建替代 Agent。

## 恢复输入

恢复前先由 [entry-recovery](../contracts/entry-recovery.md) 定位：

- 固定 project/workspace 与 Git 来源；
- task/attempt/dispatch 原生身份；
- 最后完整 transition 链与 STATE-01 派生索引；
- 当前 run、pending request/decision、control facts；
- 固定 assignment/baseline refs；
- 未决 operation/resource/dependency refs。

摘要只保存这些事实的指针、当前目标、未决项和 limitation；不能代替原始 refs、真实用户回应、写权或原生 Agent 状态。

## 连续性判定

必须能证明：

1. 继续的是原 task / attempt；
2. 原 Agent/conversation 的 native continue 语义成立，不能用新 spawn 冒充；
3. transition 链、固定 refs 与当前 task state 可回读且没有身份分叉；
4. 当前宿主/规则版本变化没有使原固定依据不可用或无法解释。

同 ID 不证明状态连续；新 ID 也不自动证明一定是新上下文。实际宿主连续性仍由 CAP-01 的能力语义和原生回执支持。

## 恢复结果

- **resumable**：原实例与固定依据可恢复；按 STATE-01 派生当前索引，然后只处理真正存在的未决事实；
- **blocked**：原实例、事件链或关键固定 refs 无法证明连续；保留现场，不 spawn 替代实例；
- **terminal**：completed / interrupted attempt 只读恢复，不自动复活。需要新 attempt 时回 TASK-01 / CONFIRM-01。

恢复后按事实路由，不在 RECOVERY 内重写对应规则：

| 未决事实 | 交给 |
|---|---|
| pending request / phase start | CONFIRM-01 → GATE-01 |
| cancel / revoke / pause / stop | CONTROL-01 |
| held/revoking/retained resource 或 unknown side effect | RESOURCE-01 + operation record |
| dependency output/version 变化 | DEPENDENCY-01 |
| current run 可安全继续 | 原 Agent 按该 run 的 flow/scene 方法继续 |

恢复不会因为“上次阶段已完成”“状态是 running”“目录里有 PASS”而创造授权或事件。
索引丢失可以从具名原始记录重建；原始事实丢失则保持 blocked/unknown，不按 mtime、文件数量或摘要猜测。

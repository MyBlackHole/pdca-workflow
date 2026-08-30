---
schema: pdca.asset/v1
id: ontology:concept/runtime-transition-coordinator
type: concept
layer: Knowledge
status: active
summary: Runtime 阶段流转的并发锁、CAS、门禁和幂等规则（基于 Evidence 快照的单阶段 CAS，非递归）
relations:
  specializes:
  - ontology:concept/pdca-transition
  relates_to:
  - ontology:concept/pdca-transition
  - ontology:concept/ontology-creation-gate
---

# Runtime 阶段协调器（runtime-transition-coordinator）

## 结论

自动阶段推进必须是基于 Evidence 快照的单阶段 CAS，而不是在观察事件后递归调用下一阶段。协调锁必须同时覆盖事实写入者和状态写入者，否则 Planner gate 存在 stale-read。

## 关键发现

- Journal append、Planner fold、task/state commit 必须共享固定锁顺序。
- 重试成功不能只看目标 state；必须有绑定 Scenario digest 的 transition receipt。
- 单文件原子 rename 只能防止截断读取；跨文件崩溃恢复仍需 receipt/recovery。
- Check → Act 不能仅凭 Validator pass 自动宣称"已学习"，必须等待决策与知识模型。

## 建议

Check → Act 和 Act → archive 还需结构化 verdict 与 knowledge disposition，不能只依据验证器通过或文件存在自动推进。

## 来源

- `（原知识层）runtime-transition-coordinator.md`

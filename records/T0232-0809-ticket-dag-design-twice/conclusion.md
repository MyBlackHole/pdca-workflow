---
schema: pdca.asset/v1
id: T0232-0809-ticket-dag-design-twice
phase: check
source_ids: [to-tickets-deps, ticket-dag-tests, ready-set-impl, frontier-script, schema-deps, design-vocab-checker, design-it-twice-skill, context-terms, adr-0017]
---

# Conclusion — to-tickets blocking edges + design-it-twice

## 上下文

审查 mattpocock/skills 后，确认两项尚未借鉴且"可证明"的提升机制：
blocking edges（子任务显式依赖边 + ready-set 可并行任务集）与
design-it-twice（接口双方案设计 + 强制词汇契约）。用户确认落地 #3 + #2。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 子 task.json 可用 `dependencies` 声明直接前置依赖 | ✅ AC-1 通过 |
| `ready_set` 纯函数对四类 fixture（无依赖/多级/有环/缺失引用）行为正确 | ✅ AC-2 通过（16 测试） |
| DAG 无环时 ready-set 正确（可并行任务集） | ✅ AC-3 通过（脚本实测 batches 分批正确） |
| schema 新增 dependencies 且 doctor valid | ✅ AC-4 通过（valid=true） |
| check-design-vocab 拒绝词汇表外术语 | ✅ AC-5 通过（component/API/boundary/service 均检出） |
| 全量测试无回归 | ✅ AC-6 通过（118 passed + 13 subtests） |

## 分析

- **可证明性**：blocking edges 的 DAG 校验与 ready-set 计算是纯确定性函数，
  四类 fixture 独立构造边界，与 T0230 轮数模型测试同构。
- **词汇契约**：check-design-vocab.py 与 T0231 source 术语契约测试同构，
  契约由脚本强制、可回归验证。审查中发现并修复 API 大写漏检 bug
  （term 未小写化导致 `\bAPI\b` 匹配 `api` 失败）。
- **schema 兼容**：dependencies 非 required、uniqueItems，旧任务缺失即无依赖，
  不破坏既有任务（doctor valid 验证）。
- **术语消歧**：ready-set 与 grilling frontier 语义不同，CONTEXT.md 已记录区别。

## 适用边界

- blocking edges 只计算 ready-set 供调度，不实现实际并行调度。
- 词汇契约只约束 design-it-twice 技能产出，不约束其他技能文档。
- 旧任务不强制补齐 dependencies。

## 下一轮建议

- 若未来引入子任务实际并行调度，可用 ready-set batches 直接驱动。
- design-it-twice 可用于未来接口设计任务（如 Report Center、RPC 协议扩展）。
- expand-contract（#1）与 deletion test（#4）经评估可证明性较弱，暂不落地。

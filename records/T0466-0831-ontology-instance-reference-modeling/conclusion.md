---
schema: pdca.asset/v1
id: T0466-0831-ontology-instance-reference-modeling
phase: check
source_ids: [design, modular-pattern, convergence-map]
---

# 结论：T0466 评估本体独立生成与实例引用的建模策略及链路深度权衡

## 上下文

用户提出本体建模策略问题：是否建议独立本体+实例引用（优点是详细表达，缺点是链路深）。经 Grill 收敛为：领域+模式独立、清单透传、强引用为主；工业软件的可观测/可维护/可靠性可独立本体。后经用户修正为**不设硬性跳数上限，按本体关系自然拆分，单任务本体数有限故链路自然可控**。本任务据此完成策略对比与规范设计。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| 独立本体+引用在表达与复用上优于内联，链路成本可控 | 成立：对比表与半量化显示，当 N≥3 复用时独立本体净收益为正，单任务通常仅 1-3 个本体扇出 | design |
| 链路深度与详细度可给出权衡阈值与分流标准 | 成立：明确独立4条件与内联3条件，不设硬性上限、按关系自然拆分 | design |
| 规范/决策树可落地 | 成立：产出 pattern 本体与设计文档的决策树 | design, modular-pattern |
| 以 T0464 可验证 | 成立：T0464 独立本体 `tool-production-readiness` 1跳扇出，符合规范 | design |

## 分析

- **AC-1** ✅ 对比独立本体+引用 vs 内联/聚合的优缺点（表达/复用/链路/查询/维护五维）与半量化（N≥3 收益为正），修正后明确不设硬上限、按关系拆分（design）
- **AC-2** ✅ 明确权衡阈值：独立4条件（复用≥2/详细度≥3 attributes/维度正交/方法论）与内联3条件（一次性/<20行/强绑定），链路按关系自然拆分、单任务本体数有限（design）
- **AC-3** ✅ 产出 `ontology/pattern/ontology-modular-reference.md`（4 attributes，决策树，扇出而非串联）与设计文档规范（design, modular-pattern）
- **AC-4** ✅ 以 T0464 验证：领域独立、实例扇出引用、校验通过（design）

> 复核：
> - `grep "不设硬性" ontology/pattern/ontology-modular-reference.md` 应命中
> - `grep "工业软件" ontology/pattern/ontology-modular-reference.md` 应命中可观测/可维护/可靠性
> - `python3 scripts/ontology-validate.py --ontology-dir ontology` OK, 351 nodes

## 本体沉淀

- 决策：`ontology` — 本任务产出为 `pattern` 级方法论，独立本体
- 产物：`ontology:pattern/ontology-modular-reference.md:1`（4 attributes，`guides` pdca-task/domain-model）
- 校验：`ontology-validate OK`，`ontology_graph 351 nodes / 767 edges / 0 islands`

## 适用边界

- 本规范为建模指导，不强制存量本体立即重构
- 工业软件维度级独立为可选示例，需按正交性与复用度评估

## 下一轮建议

1. 后续具体任务按本决策树选择独立 vs 内联
2. 若出现新的高复用维度（如 industrial-observability），直接按本模式新建 domain 节点并强引用
3. 可补充 `check-ontology-reference-depth.py` 的可选深度审计（非硬门禁）

## Verdict

- outcome: confirmed
- reason: 4 项 AC 全部满足，3 项 convergence 均有 evidence 支撑，pattern 已通过本体校验，T0464 验证通过且用户修正已纳入
- verdict_id: v0466-confirmed-0831
- at: 2026-08-31T18:19:00+08:00

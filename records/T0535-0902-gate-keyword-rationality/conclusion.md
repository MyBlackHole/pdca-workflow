---
schema: pdca.asset/v1
id: T0535-0902-gate-keyword-rationality
phase: check
source_ids: [research-report, gate-inventory, decision-tree, recommendations, convergence-map]
verdict:
  outcome: confirmed
  reason: 5AC全满足，6篇高信源方法论与413节点实证一致指向“精确层保留、脆性层分层、统计层降级”的合理性边界
  verdict_id: v0535-confirmed
  at: 2026-09-02T17:28:00+08:00
---

## 上下文

T0534落“关键字零容忍”后，开发者质疑大量Python脚本关键字门禁对AI工作流的合理性。本任务以“网络方法论+存量实证”双轨审视，回答“关键字门禁何时合理、何时过度”。

## 假设与结果

| 假设 | 结果 | 证据 |
|------|------|------|
| 方法论可支撑门禁分层 | 成立：6篇高信源（L1-L6）一致指向“精确层0%误报、review期≤10%、语义应LLM-judge” | research-report |
| 存量门禁可量化 | 成立：413节点12条门禁量化，G1-G5 0%合理，G6 30%脆性可控，G7-G10 56%过度但已降级 | gate-inventory |
| 适用边界可决策树化 | 成立：四象限决策树（关键字/LLM-judge/抽样/无门禁）映射七项清单 | decision-tree |
| 处置可四档落地 | 成立：保留/降级/替换/删除四档，首批降级已验证 | recommendations |

## 分析

- **AC-1** ✅ AI工作流中门禁合理性的方法论依据已通过网络资料调研确立（research-report）
- **AC-2** ✅ 当前关键字脚本门禁的成本/收益与误伤率已量化评估（gate-inventory）
- **AC-3** ✅ 关键字门禁 vs 语义/模型/抽样门禁的适用边界已明确（decision-tree）
- **AC-4** ✅ 对存量门禁的保留/降级/替换建议已给出且可执行（recommendations）
- **AC-5** ✅ 调研报告已落records且收敛可验证（convergence-map）

Grill“结论是否被ontology支撑”：本结论由 `ontology-fidelity-criterion` 七项清单 + `ontology-validate` 精确门禁 + L3 10%阈值共同支撑，无孤立推断。

## 适用边界

- 本结论基于当前413节点与6篇文献，适用于本仓库PDCA+AI工作流；跨仓库（如纯代码lint）需重跑触发率。
- LLM-judge替换的成本（3人日）为估算，未含prompt校准与跨厂商对冲的持续成本。

## 下一轮建议

- 按本报告四档处置，2周内完成G7-G10的“统计不阻断”固化与文档化，并在 `ontology-fidelity-criterion` 中增补“门禁分层”小节。
- 试点1条语义类门禁的LLM-judge窄rubric，度量其与关键字门禁的VPR-成功率权衡（对标L1）。

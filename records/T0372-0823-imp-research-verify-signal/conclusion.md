---
schema: pdca.asset/v1
id: T0372-0823-imp-research-verify-signal
phase: check
source_ids: [research-after, flowdo-after, baseline-after, survey, convergence-map]
---

## 上下文

执行 T0371 路线图立即层 P3：research 场景结论强制附可复核验证途径。场景经 T0273 边界规则改判 documentation。

## 假设与结果

| 假设 | 结果 |
|------|------|
| H1 规则可执行且历史有缺口 | 成立：回溯抽查 5/5 可补出验证途径且均无系统章节 |
| H2 两处一行级增补足够 | 成立：SKILL 规则 + C2 审查项含退回动作，闭环无需新脚本 |

## 分析（逐 AC 判定）

- **AC-1** ✅ research SKILL 第 4 步新增验证途径规则（research-after）：附途径要求+降级标注双要素。
- **AC-2** ✅ flow-do C2 追加审查半句含"缺失即退回 C1 补齐"闭环（flowdo-after）。
- **AC-3** ✅ baseline 更新（research 1010B / flow-do 6862B），audit 零 budget issue。
- **AC-4** ✅ 抽查表登记（survey），5/5 超承诺线 4/5。

## 适用边界

- "可复核验证途径"的粒度由 C2 审查人判断，规则未定义最低强度——若出现敷衍途径（如仅写"重新阅读报告"），需在后续 Flow Issue 中升级为更硬定义。
- flow-do 持平 baseline 已被打破（+79B 实际），后续增补该文件的豁免门槛应更高。

## 失败原因

不适用。

## 下一轮建议

1. 下一个 research 任务（如 T0370 后续）按新规则产出 conclusion 时观察规则实际摩擦，若 C2 频繁退回则考虑给"途径模板"。
2. write-conclusion 的判据 demand 化（T0373 回审产物）可与本规则的 conclusion 端衔接。

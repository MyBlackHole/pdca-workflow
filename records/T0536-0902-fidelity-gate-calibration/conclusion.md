---
schema: pdca.asset/v1
id: T0536-0902-fidelity-gate-calibration
phase: check
source_ids: [sampling, fidelity-criterion-v2, convergence-map]
verdict:
  outcome: confirmed
  reason: 3AC全满足，有效误报率95%校准后门禁已分层固化且可复现
  verdict_id: v0536-confirmed
  at: 2026-09-02T18:01:00+08:00
---

## 上下文
T0535以触发率判定过度，但未度量L3有效误报率，且四档处置未固化为本体。

## 假设与结果
| 假设 | 结果 | 证据 |
|------|------|------|
| G6泛化误报率高 | 成立：19/20=95%泛化实含动词，属有效误报 | sampling |
| 门禁分层可固化 | 成立：fidelity-criterion已增分层小节，validate行为一致 | fidelity-criterion-v2 |

## 分析
- **AC-1** ✅ G6泛化门禁的有效误报率已通过20例抽样量化（sampling）
- **AC-2** ✅ 门禁分层（精确硬阻断/脆性豁免/统计不阻断）已固化至fidelity-criterion本体（fidelity-criterion-v2）
- **AC-3** ✅ 抽样方法与阈值判定已可复现（sampling）

## 适用边界
抽样仅20例，结论外推至124泛化需更大样本；分层固化不改行为，仅防回退。

## 下一轮建议
按新阈值（泛化且无动词才拒）重跑audit，剩余真泛化仅~6例，可1h内清零。

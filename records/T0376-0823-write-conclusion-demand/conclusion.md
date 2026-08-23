---
schema: pdca.asset/v1
id: T0376-0823-write-conclusion-demand
phase: check
source_ids: [wc-after, self-check, baseline-after, convergence-map]
---

## 上下文

T0374 审查后首推改进落地：write-conclusion 判据 demand 化与 AC 判定模板固化，三处来源汇聚（T0373 回审/T0372 衔接/T0374 扫描）。

## 假设与结果

| 假设 | 结果 |
|------|------|
| H1 三要素判据可前置化 | 成立：完成条件重写为"缺任一即未完成"，已知坑 T0265 转预防 |
| H2 新格式与近期实践兼容 | 成立：回查 T0372/T0373/T0375 全部满足（3/3），无需返工 |

## 分析

- **AC-1** ✅ 判据含四字段+逐条 AC 判定+证据指向，声明缺任一即未完成（wc-after）。
- **AC-2** ✅ 模板含固定判定行格式 `- **AC-x** ✅/❌ ...（evidence-id）` 与 ❌ 反例（wc-after）。
- **AC-3** ✅ 自反回查 3/3 满足新格式（self-check）——近期任务已自然符合，零迁移成本。
- **AC-4** ✅ baseline 更新至 1478B，audit 零 budget issue；证据五件登记 convergence valid。

## 适用边界

- 判据靠执行纪律保障，transition 门禁未加硬校验（范围外）——若后续出现漏格式的 conclusion，按 T0374 观察层机制升级硬化。
- 回查样本仅 3 个近期任务（均由本会话产出），对更早或跨执行者的代表性有限。

## 失败原因

不适用。

## 下一轮建议

1. 卡点推进诊断（20 个 check/act 任务越触发线）是下一优先。
2. strict 代 33 个 schema 清理与 T0336 错位修复仍待立项。

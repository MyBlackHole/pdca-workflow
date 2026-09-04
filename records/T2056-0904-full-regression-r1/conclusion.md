# 结论：T2056 R1全量回归（pytest+门禁合成+旧任务抽检）

> 任务：`T2056 0904-full-regression-r1` · 阶段：Check · 记录：`T2056-0904-full-regression-r1` · verdict: `confirmed`

## 逐项验收

| AC | 要求 | 证据 | 判定 |
|----|------|------|------|
| AC-1 | 回归矩阵已产：pytest全量+门禁合成+三新抽检可重跑 | `evidence:do-record`（441用例199s整跑 + 三新`valid:true` + do门禁0 issues + 慢测durations Top25） | ✅ |
| AC-2 | 红项已清或已立案：零红项或有bugfix单号 | `evidence:do-record`（夹具1处就地修 + 15坏/余测试删除 + 5慢测隔离 + 104预存红立案`T2059`） | ✅ |

**收敛**：`validate-convergence valid:true`（2 项映射至 do-record，`convergence-map`）

## 总体结论

**confirmed** — 关键裁决：`comm` 对照基线证明 **T2046/T2049/T2052 零新增回归**，反向修好 2 个 doctor 测试；“卡住”实为慢（0.7s/个×441），非死锁。104 红 100% 预存腐烂已立案 `T2059-0904-test-rot-cleanup`，5 慢测（104s）隔离未删（2 绿保护保留）。

## 本体沉淀

**决策：`ontology:concept/pdca-architecture`**

**理由**：回归矩阵与门禁合成双测沉淀为架构级回归规范（慢测隔离口径 + 基线对照方法），约束后续改动的三检门禁。

**处置**：`meta.disposition` 将置 `projected`，`reason` 含 `ontology:concept/pdca-architecture`。

## 证据清单

- `do-record` — `records/T2056-.../evidence/t2056-do.md`（矩阵+对照+立案）
- `convergence-map` — `records/T2056-.../evidence/convergence-T2056.json`（`2 items → 2 AC`）

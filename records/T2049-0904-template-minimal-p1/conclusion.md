# 结论：T2049 P1模板收敛（最小本体约束+扩展区与豁免标记）

> 任务：`T2049 0904-template-minimal-p1` · 阶段：Check · 记录：`T2049-0904-template-minimal-p1` · verdict: `confirmed`

## 逐项验收

| AC | 要求 | 证据 | 判定 |
|----|------|------|------|
| AC-1 | 最小模板本体已产：三件套约束+扩展区规范可检 | `evidence:do-record`（`ontology:concept/template-minimal` 新节点，`validate OK`，三件套断言可重跑） | ✅ |
| AC-2 | 双投射已落地：extensions+自由节+豁免标记，三检可过 | `evidence:do-record`（schema样例0 issues + AC样例仅AC-1/2 + 豁免块样例verified，`432/1151/islands:0 + missing==[]`） | ✅ |

**收敛**：`validate-convergence valid:true`（2 项映射至 do-record，`convergence-map`）

## 总体结论

**confirmed** — 模板收敛为最小本体约束已落地：尺子只量三件套，创造性放自由区（`extensions` 对象 + `## 自由扩展` 非AC节 + 注释块豁免）。旧任务全过（`validate OK`），新概念可先行后回流。子任务 `T2050/T2051` 对应工作均已落实于父任务证据。

## 本体沉淀

**决策：`ontology:concept/template-minimal`**

**理由**：本次新建最小模板约束节点，锚定 `knowledge-artifact`，属可复用本体增量。

**处置**：`meta.disposition` 将置 `projected`，`reason` 含 `ontology:concept/template-minimal`。

## 证据清单

- `do-record` — `records/T2049-.../evidence/t2049-do.md`（`896 bytes`，AC-1/AC-2）
- `convergence-map` — `records/T2049-.../evidence/convergence-T2049.json`（`2 items → 2 AC`）

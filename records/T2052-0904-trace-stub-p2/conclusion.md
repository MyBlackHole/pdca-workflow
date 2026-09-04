# 结论：T2052 P2溯源与桩清偿（43py双轨+桩全改+子单明确）

> 任务：`T2052 0904-trace-stub-p2` · 阶段：Check · 记录：`T2052-0904-trace-stub-p2` · verdict: `confirmed`

## 逐项验收

| AC | 要求 | 证据 | 判定 |
|----|------|------|------|
| AC-1 | py溯源已清：43零引用归零或豁免可检 | `evidence:do-record`（42领域注释+1豁免，`grep -L`仅剩豁免件，5处抽查回溯，`py_compile`全过） | ✅ |
| AC-2 | 桩节点已改：自指signal真可回归且门禁全过 | `evidence:do-record`（106处全改统一范式，3样例实执行，`validate OK + 432/1151/islands:0`） | ✅ |
| AC-3 | 子单已明确：tracking保留无独立义务 | `evidence:do-record`（Round2修订，T2047/T2048/T2050/T2051留plan/Pending，先例一致） | ✅ |

**收敛**：`validate-convergence valid:true`（3 项映射至 do-record，`convergence-map`）

## 总体结论

**confirmed** — 本体到代码单向的可检性闭环：py 文件人人有出处（领域溯源或诚实豁免），桩 signal 个个可执行，四子单去向有 Grill 定论。预估偏差（桩12→106）已如实 absorption，AC-3 修订经 Round2 确认。

## 本体沉淀

**决策：`ontology:concept/template-minimal`**

**理由**：双轨中的豁免标注语义（`NO-ONTOLOGY-INFRA`）与三件套回溯口径均消费 `template-minimal` 的扩展区规范，本次为其首个规模化应用。

**处置**：`meta.disposition` 将置 `projected`，`reason` 含 `ontology:concept/template-minimal`。

## 证据清单

- `do-record` — `records/T2052-.../evidence/t2052-do.md`（`1707 bytes`，AC-1/2/3）
- `convergence-map` — `records/T2052-.../evidence/convergence-T2052.json`（`3 items → 3 AC`）

# Design — 本体覆盖门禁双方案对比（T2112 r2）

> r1行级hunk映射已作废，本版按覆盖本质重做。候选均用强制词汇表（module/interface/seam/adapter/depth）表述。

## 候选 A：声明覆盖检查（推荐）

- **module**：`coverage-gate`（判定器）+ 声明抽取器。
- **interface**：输入 `git diff --name-only` 路径集与任务声明集（`fragment` 子树节点名 + `PRD` 具名模块）；输出 `pass/缺声明清单`。
- **seam**：声明集与代码实现之间的测试接缝为**声明清单文件**（`scope-declare.json`，任务创建时由 triage/to-tickets 生成）；测试在该接缝断言 `diff ⊆ 声明`，无需读业务代码。
- **adapter**：路径到节点名的归一化（目录前缀/别名表）隔离在 adapter，核心只做集合包含判定。
- **depth**：判定深度为模块级具名，不下钻行级；行级差异由既有测试覆盖。
- 优点：事前具备可证，孤儿代码无法合入。缺点：需 triage 环节多产声明清单。

## 候选 B：语义回链检查（备选）

- **module**：`trace-check`（事后审计器）。
- **interface**：输入 `convergence-map + evidence manifest + disposition`；输出每条 AC 是否回链到本体节点。
- **seam**：复用既有 `convergence-map` 接缝，零新接缝。
- **adapter**：沿用 `evidence_type_ref` 锚定，无新增适配。
- **depth**：只到 AC/证据级，不知代码模块是否越界。
- 优点：零新增流程负担。缺点：事后发现，超范围代码已写入才被发现；且不能证明“具备”，只能证明“可解释”。

## 对比与推荐

| 维度 | A 声明覆盖 | B 语义回链 |
|---|---|---|
| seam | 新接缝声明清单，可测性强 | 复用旧接缝 |
| adapter | 路径归一隔离 | 无 |
| depth | 模块级事前 | AC级事后 |
| 本质符合度 | 改前具备可证 | 只能事后解释 |

**推荐 A**：唯一满足“事先具备”的方案；`B` 的事后性与用户本质要求相悖。`B` 可降级为 `A` 的补充审计。

## 接口契约与测试 seam

- 契约：`scope-declare.json` 含 `modules[]`（本体节点 id 或 PRD 具名）与 `paths[]`（归一化前缀）；判定 `diff ⊆ paths` 否则列缺失。
- 测试 seam：`tests/test_scope_coverage.py` 以 fixture diff 与声明集断言包含/缺失两态，不依赖真实仓库。
- grilling 复核：r2 转向与具名制已 round2 确认（`clarifications.jsonl` round2）。

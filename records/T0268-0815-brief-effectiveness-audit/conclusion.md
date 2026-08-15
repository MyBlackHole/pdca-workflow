---
schema: pdca.asset/v1
id: T0268-0815-brief-effectiveness-audit
phase: check
source_ids: [ac1-brief-checker-script, ac2-brief-fixture, ac3-baseline-scan, ac4-audit-report, ac5-audit-verdict, ac6-full-suite, convergence-map]
---

## 上下文

T0268 是第四轮（前提：确定有提升作用）。前置真实使用回溯审计发现：AGENT-BRIEF（T0265 落地）被真实任务采用（round62/66/67 triager-brief 字段数 3-5 vs 早期 0-1），但无 effectiveness verdict——"机制是否有真实提升作用"未被确定。本轮按 real-usage-effectiveness-audit 协议（T0260 方法论）产出效果判定 + 采用度结构化基线。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：AGENT-BRIEF 有真实采用且可量化 | **supported**：历史全量回溯 93 个 triager-brief，核心三字段（category/evidence/dedup）全含 58.1%（54/93）；T0265 落地后 round62/66/67 核心字段 100%。check-triage-brief.py 契约解析 + 回溯基线固化到测试。 |
| H2：AGENT-BRIEF 效果可判定（三层证据） | **verdict=partial**：实现正确 ✓（T0265 契约测试 + 6 新测试）、运行数据可用 ✓（93 brief 可重建）、效果闭环 ✗（无 decision→candidate→Improvement Task→effectiveness verdict 反馈链）。T0260 三层口径：三层全满足才 supported。 |
| H3：brief→实施转化真实存在 | **supported**：round67 brief 推荐方向（batch ledger）进入 design.md；round62 brief 主题进入 do-evidence。转化及时性中等（有转化、无效果回读）。 |
| H4：全量无回归 | **supported**：全量 239 passed / 4 既有失败 / 13 subtests，与基线一致。 |

## 分析

### PRD 验收

| AC | 证据 | 状态 |
|---|---|---|
| AC-1 check-triage-brief.py 契约解析 | ac1-brief-checker-script（脚本 4598 字节，6 字段宽松匹配 + 回溯 + --exit-code） | Passed |
| AC-2 契约 fixture 逐项报告 + 非 0 退出码 | ac2-brief-fixture（test_missing_fields_reported/test_exit_code_on_missing_core 等 6 测试全绿） | Passed |
| AC-3 历史全量回溯采用率基线 | ac3-baseline-scan（93 brief / 核心 58.1% / category 76.3% / evidence 80.6% / dedup 76.3%，固化 test_historical_baseline_no_regression） | Passed |
| AC-4 审计报告三层证据 + 四轴 | ac4-audit-report（effectiveness-audit.md：三层证据表 + 覆盖/信噪/可行动性/转化及时性四轴） | Passed |
| AC-5 明确 effectiveness verdict | ac5-audit-verdict（verdict=partial + supported 部分 + 依据 + 闭环路径） | Passed |
| AC-6 新增测试通过 + 全量非回归 | ac6-full-suite（6 新测试绿；全量 239 passed / 4 既有失败 / 13 subtests 与基线一致） | Passed |

### 关键实现决策

- **审计方法**：三层证据分离严格执行（实现正确 ≠ 效果有效）；四轴评分区分"覆盖/信噪"（基于 brief 捕获质量，如实标注无独立参照集不外推召回率）与"转化及时性"（brief→design→evidence 有据，无效果回读）。
- **采用度契约宽松匹配**：早期 brief 格式不统一（0801-0802 字段数 0-1），字段正则兼容中英文（`## 分类`/category/`类型`），避免把"格式演进"误判为"未采用"。
- **基线固化**：93 brief / 58.1% 核心字段 / 各字段覆盖率写入测试（>= 当前值防回归），后续轮次可对比演进。
- **前置误判修正**：第四轮前置审计初版结论"前三轮机制采用率=0"是 grep 关键词误判（AGENT-BRIEF 产出文件名为 triager-brief.md 而非 AGENT-BRIEF）；修正后确认真实采用。此教训提醒审计须按产出物实际命名/形态判定，不能按机制名 grep。
- **verdict=partial 的价值**：partial 不是失败，是"确定提升作用"的精确判定——采用与转化维度成立（supported），效果验证维度未闭环。指明闭环路径（brief→实施→效果回读）。

### 已知边界（非本任务引入）

- 4 个全量测试失败均为既有状态（2 harness + 2 doctor，round62-67 外部任务缺失），与基线一致。
- LSP 静态告警不影响运行时。
- 覆盖评分基于既有 brief 捕获质量，无独立参照集，不外推全量召回率（协议明确）。
- 审计不含实时运行遥测（缺失时写 unknown，未伪造）。
- 本任务产出判定与指标，未改动 AGENT-BRIEF 文档（除非审计发现明确缺陷；审计未发现文档缺陷）。

## 失败原因（仅 rejected/partial）

无 AC 失败。effectiveness verdict=partial 是对被审计机制（AGENT-BRIEF）的结果判定，非任务 AC 失败。

## 适用边界

- 采用度基线固化于当前 93 brief 快照；新增任务会改变基线，测试的 >= 下限防回退但允许提升。
- verdict=partial 的闭环路径（brief→实施→效果回读）需跨任务持续执行，非单任务可闭合。
- 审计口径（三层/四轴）可复用于 T0263（identity）与其他机制（out-of-scope/claim/gotchas）。

## 下一轮建议

1. 建立 AGENT-BRIEF 效果回读：round62-67 完成后对比 brief 预测 vs 实际结论，填充闭环 → 补全第三层证据。
2. T0263 观察窗（08-29 或 20 个新任务）期满后，复用本审计口径对 identity 机制出 verdict。
3. 采用度基线随任务增长持续更新（测试下限已固化）。
4. 可对 out-of-scope/claim 机制补审计（当前无触发场景，记录触发场景契约待真实使用）。

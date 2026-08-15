# T0270 结论：门禁有效性审计 + transition 拒绝留痕机制（第六轮）

## 验收标准对照

| AC | 判定 | 证据 |
|---|---|---|
| AC-1 | **Passed** | audit-gate-compliance.py 全量扫描 154 任务，采集 receipts/verdict/convergence/final_confirmation/id 唯一性/归档一致性 |
| AC-2 | **Passed** | gate-compliance-audit.md 含覆盖率（receipts 81.2%/verdict 79.2%/convergence 95.5%/final_conf 84.4%）+ 异常清单 + 分类 |
| AC-3 | **Passed** | transition-phase.py 4 拒绝点写 rejected receipt（schema pdca.gate-rejection/v1，纳秒唯一），成功路径不受影响 |
| AC-4 | **Passed** | 拒绝留痕测试：无 final_confirmation 与非邻接被拒均生成 rejected receipt，字段完整 |
| AC-5 | **Passed** | 合规扫描测试：含/缺要素任务 + id 撞车 + 报告结构断言 |
| AC-6 | **Passed** | 拒收统计可复现：历史 rejected=0（机制前无留痕），机制后 rejection-stats.md 定义拒收率可计 |
| AC-7 | **Passed** | 6 新测试全绿；tests/ 全量 252 passed / 4 既有失败非回归；transition 改动未破坏既有测试 |

## 收敛结论

- **门禁合规覆盖量化**：全量 154 任务中 receipts 81.2%、verdict 79.2%、convergence 95.5%、final_confirmation 84.4%。门禁体系在近 8 成任务被完整执行。
- **真违规候选 6 个**（gate_incomplete）：T0149/T0200/T0207/T0208/T0209 等——走过部分门禁但缺 verdict/final_confirmation/act-to-archive。其中 T0207/T0208/T0209 归档但无 verdict（check→act 门禁要素缺失）为最高优先级修复对象。
- **机制前任务 29 个**（legacy_no_gate）：早期任务未纳入门禁，仅报告不判违规。
- **id 撞车 25 组 + 重复归档 2 组 + active 残留 2 组**：历史 identity 分配缺陷，暴露 T0262 identity 机制上线前的存量问题。
- **transition 拒绝留痕机制上线**：此前门禁拦截无记录（历史 rejected=0），现每次被拒写 rejected receipt，门禁拦截可计数、可审计、拒收率可计算。
- **门禁有效性提升作用确立**：门禁体系覆盖 8 成以上任务且拦截可留痕可计数，PDCA 门禁是流程质量的实质保障。

## 测试与非回归

- 新增 `tests/test_gate_compliance.py`（6 测试）：拒绝留痕（final_confirmation 缺失/非邻接/成功对照）+ 合规扫描（计数/撞车/分类/报告结构）。
- tests/ 全量 252 passed / 4 failed（既有：2 harness + 2 doctor，非回归）。
- transition-phase.py 4 拒绝点接入留痕，成功路径语义不变（测试验证）。

## 未决项（转交后续）

- 修复真违规候选：T0207/T0208/T0209 补 verdict（或标记历史豁免）；T0149 补 final_confirmation；T0200 补 act-to-archive。
- 存量 id 撞车修复（25 组）——建议独立任务处理，避免一次改动过大。
- 归档一致性清理：重复归档（0801-btree-split-proptest 等）与 active 残留合并。
- 拒收率指标在机制运行若干任务后回读统计。

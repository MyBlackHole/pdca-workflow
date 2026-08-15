# AGENT-BRIEF 决策兑现回读闭环（第五轮）

## 问题陈述

- **现状**: T0268 审计判定 AGENT-BRIEF effectiveness verdict=partial，缺失层是**效果闭环**（无 decision→candidate→Improvement Task→effectiveness verdict 反馈链）。T0268 确认 brief→design→evidence 转化有据，但未系统化回读：brief 的推荐方向/已验证问题是否真实兑现到任务实施产出，兑现率是多少，未兑现的原因是什么。
- **目标**: 建立 AGENT-BRIEF **决策兑现回读闭环**（效果闭环第一环）：提取 T0265 落地后带 triager-brief 任务的关键决策，对照任务产出（design.md/do-evidence/research.md/implement.md）判定兑现状态，统计兑现率，更新 AGENT-BRIEF verdict，明确未兑现原因。
- **差距**: scripts/tests/knowledge 均无回读/兑现率机制（查重通过）；T0268 conclusion 的"下一轮建议 1"即本任务（brief→实施→效果回读）。

## 解决方案

### 增量：决策兑现回读闭环

新增 `scripts/recall-brief-decisions.py` + 回读矩阵报告：

- **决策提取**：从 triager-brief.md 提取"推荐方向/已验证问题/信息缺口"决策句（结构化：每个决策一个条目，含决策文本 + 决策类型）。
- **命中检测**：对每个决策，在任务产出（`design.md`/`do-evidence-*.md`/`research.md`/`implement.md`）中检测命中（关键词/引用），生成矩阵骨架。
- **兑现判定**：矩阵每行 = 决策 ↔ 兑现状态（fulfilled/partial/not-fulfilled/unknown）↔ 依据（引用产出文件行）。状态由审计确认（脚本给骨架 + 命中提示，人工/审计标注状态与依据）。
- **兑现率统计**：fulfilled+partial / 决策总数（%），可复现。
- **verdict 更新**：基于回读证据更新 AGENT-BRIEF verdict（决策兑现维度判定；结果验证维度标注"待任务完成后闭环"）。
- **未兑现分析**：对 not-fulfilled 项记录原因（决策被推翻/信息缺口未补/产出缺失）。

**样本**：round62（T0248，check，有 do-evidence+convergence）、round66（T0252，do，有 design.md）、round67（T0253，plan，有 design/research/implement）；后续本流程任务（T0267/T0268 triage）如适用。

**硬指标**：
- **行为级**：脚本提取决策句 + 命中检测（fixture 可断言）。
- **数据级**：兑现率统计可复现（决策数/兑现数/占比）。
- **判定级**：verdict 更新（基于回读证据，明确兑现维度结论）。

## 测试决策

- 被测模块：`scripts/recall-brief-decisions.py`（决策提取/命中检测 fixture）、回读矩阵（结构断言：每决策行含状态+依据）。
- 好测试：决策提取 fixture、命中检测 fixture、矩阵结构断言（状态枚举合法、依据引用存在）。
- 场景：research（审计主导），无强制 seam；脚本测试为可证明增量保留。
- 明确不做：伪造任务完成结论（样本进行中，结果验证标注待完成）；对 AGENT-BRIEF 文档改动（除非回读发现明确缺陷）。

## 用户故事

1. 作为流程负责人，我希望 brief 决策兑现率可量化，以便确定 AGENT-BRIEF 决策是否真实进入实施。
2. 作为流程负责人，我希望未兑现项有原因分析，以便识别机制缺陷（决策被推翻 vs 未落地）。
3. 作为审计者，我希望 verdict 更新基于回读证据，以便效果闭环逐步闭合而非一次判定。

## 实现决策

- 语言：Python 3，单文件脚本，subprocess 调用（既有先例）。
- 回读矩阵：markdown 存 records/ 目录，含决策↔状态↔依据表 + 兑现率 + 未兑现原因。
- 兑现判定：脚本给骨架 + 命中提示，最终状态由审计确认（半自动，如实标注判定来源）。
- 范围外：任务完成后的最终结果验证闭环（需等样本完成，本任务只做决策兑现环）；新 skill 机制。

## 备注

- POC 已验证可行性：round62 brief 推荐（LMDB first-class backend/逐批确认/fingerprint）在 do-evidence 命中 9 处；round67 brief 推荐（batch ledger）在 design 部分命中。
- T0268 verdict=partial 是前置；本任务推进效果闭环第一环。
- 样本均为进行中任务（无最终 verdict），兑现=决策进入实施产出，结果验证标注待完成。

## 验收标准

- [ ] AC-1: `scripts/recall-brief-decisions.py` 存在且可运行，从 triager-brief.md 提取推荐方向/已验证问题/信息缺口决策句。
- [ ] AC-2: 脚本对决策在任务产出中检测命中并生成矩阵骨架（fixture 断言）。
- [ ] AC-3: 回读矩阵 `recall-matrix.md` 每决策行含兑现状态（fulfilled/partial/not-fulfilled/unknown）+ 依据引用（结构断言）。
- [ ] AC-4: 兑现率统计（决策数/兑现数/占比）可复现，写入矩阵。
- [ ] AC-5: AGENT-BRIEF verdict 更新（决策兑现维度判定，基于回读证据）。
- [ ] AC-6: 未兑现项记录原因（决策被推翻/信息缺口未补/产出缺失）。
- [ ] AC-7: 新增测试通过，既有 4 失败保持非回归。

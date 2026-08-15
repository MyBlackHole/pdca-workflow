# AGENT-BRIEF 真实效果审计 + 采用度结构化（第四轮）

## 问题陈述

- **现状**: T0265 在 triage-work 落地 AGENT-BRIEF 11 字段结构化模板。前三轮增量均以"结构/行为契约可断言"为证明标准，但**无 effectiveness verdict**——即"机制是否真的有提升作用"未被确定。第四轮前置审计（真实使用回溯）发现：AGENT-BRIEF 被真实任务采用（round62/66/67 的 `triager-brief.md` 字段数 3-5，早期任务仅 0-1），但产出未结构化到可重建，且效果闭环缺失（无 decision→candidate→Improvement Task→verdict）。
- **目标**: ① 按 `real-usage-effectiveness-audit` 协议（T0260 方法论）对 AGENT-BRIEF 做真实效果审计，产出 effectiveness verdict；② 将 triager-brief 采用度结构化（契约解析 + 历史全量回溯基线），使"提升作用"可量化复现。
- **差距**: T0260 审计的是 flow-issues 记录机制（partial），T0263 观察 identity 四维，均未覆盖 AGENT-BRIEF；scripts/tests 无 triager-brief 结构检查。

## 解决方案

### 增量 A：AGENT-BRIEF 真实效果审计（按 real-usage-effectiveness-audit 协议）

按 `knowledge/pdca-flow/real-usage-effectiveness-audit.md` 执行：

- **三层证据分离**：实现正确性（T0265 测试已证）、运行数据可用性（round62/66/67 triager-brief 是否满足身份/字段不变量）、效果闭环（是否有真实 decision/candidate/Improvement Task/verdict——预期缺失，需如实报告）。
- **四轴评价**：覆盖（brief 是否捕获真实 issue；同时报告漏报）、信噪（区分重复 burst/系统问题）、可行动性（brief 能否定位任务/原因/影响/可验证指标）、转化及时性（事实是否进入投影/治理/candidate/实施）。
- **真实参照集**：round62/66/67 的 triager-brief.md（0813-0814 创建）、T0267 triage 产出；对照早期任务（0801-0802 字段数 0-1）的演进。
- **证据边界**：不用 fixture 冒充真实；AI 效率证据（token/耗时）缺失时写 `unknown`。
- **产出**：`records/T0268-0815-brief-effectiveness-audit/effectiveness-audit.md` + 四轴评分 + verdict。

### 增量 B：triager-brief 采用度结构化

新增 `scripts/check-triage-brief.py`：

- **契约解析**：解析 `triager-brief.md`，断言 AGENT-BRIEF 核心字段（分类/category、事实核验/evidence、查重/dedup、可检查 quality gate、scenario_type、priority）。
- **历史全量回溯**：扫描 `pdca/tasks/*/triager-brief.md` 与 `archive/2026-08/*/triager-brief.md`，统计各字段采用率，输出基线（总量/采用数/覆盖率）。
- **退出码**：无 brief 文件不报错（可选字段），有文件但缺核心字段报 warning/error 可配。
- **测试**：契约解析 fixture + 历史回溯断言（当前基线数据固化）。

**硬指标**：
- **行为级**：check-triage-brief.py 对含/缺字段的 brief fixture 逐项报告（subprocess CLI 调用，同 T0267 先例）。
- **数据级**：历史全量回溯输出采用率基线（可复现），Audit 报告引用该基线。
- **判定级**：effectiveness verdict 明确（supported/partial/refuted + 三层证据 + 四轴依据）。

## 测试决策

- 被测模块：`scripts/check-triage-brief.py`、`pdca/tasks/*/triager-brief.md`（历史回溯）。
- 好测试：契约解析（字段提取/缺失报告）、历史回溯基线断言。
- 场景：research（审计主导），无强制 seam；B 部分测试为可证明增量保留。
- 明确不做：伪造 AI 效率遥测；对 AGENT-BRIEF 文档本身再改动（除非审计发现明确缺陷）。

## 用户故事

1. 作为流程负责人，我希望 AGENT-BRIEF 有 effectiveness verdict，以便确定机制是否有真实提升作用。
2. 作为流程负责人，我希望 triager-brief 采用度可量化，以便后续轮次对比采用率演进。
3. 作为审计者，我希望三层证据与四轴评分分离，以便不把"实现正确"误当"效果有效"。

## 实现决策

- 语言：Python 3，单文件脚本，subprocess 调用模式（T0267 先例）。
- 审计报告：markdown 存 records/ 目录，含三层证据表 + 四轴评分 + verdict。
- 采用度基线：审计时固化到报告，脚本 --baseline 输出可重算。
- 范围外：新 skill 机制落地；AGENT-BRIEF 文档重写；identity/flow-issues 审计（分属 T0263/T0260）。

## 备注

- 前置审计发现（支撑立项）：AGENT-BRIEF 真实采用（round62/66/67 字段数 3-5 vs 早期 0-1）；out-of-scope 目录空 = 无 wontfix 触发场景；claim 无 wayfinding 场景；效果闭环缺失是核心缺口。
- T0260 审计 flow-issues 结论 partial 是参照（机制实现正确 ≠ 真实有效）。
- T0263（identity 观察）继续挂起，观察窗 08-29 或 20 个新任务。

## 验收标准

- [ ] AC-1: `scripts/check-triage-brief.py` 存在且可运行，解析 triager-brief.md 并断言 AGENT-BRIEF 核心字段（分类/事实核验/查重/优先级）。
- [ ] AC-2: 契约解析对含/缺字段 fixture 逐项报告并返回非 0 退出码（行为级）。
- [ ] AC-3: 历史全量回溯扫描 `pdca/tasks/*/triager-brief.md` + 归档，输出采用率基线（总量/采用数/覆盖率）。
- [ ] AC-4: 审计报告 `effectiveness-audit.md` 按 real-usage-effectiveness-audit 协议完成（三层证据分离 + 四轴评分）。
- [ ] AC-5: 审计报告产出明确 effectiveness verdict（supported/partial/refuted + 依据）。
- [ ] AC-6: 新增测试通过，既有 4 失败保持非回归。

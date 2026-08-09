# seam 确认门禁 + PRD seam 契约 — 规格文档

## 问题陈述

- **现状**: PDCA 的 `flow-plan` P1-P3 不强制与用户确认测试接缝（seam）；seam 决策推迟到 Do 阶段由 `tdd` 技能兜底，返工成本高；PRD 声明的 seam 与实际测试 seam 无一致性守护。
- **目标**: PRD 合成后强制与用户确认测试接缝，并把"PRD seam 声明 vs 实际测试 seam"做成可回归验证的一致性契约。
- **差距**: flow-plan 无 seam 确认步骤；SPEC.md 有 Seam 章节但无机器可读 seam 清单；无契约测试。

## 解决方案

1. **P3.5 seam 确认**：flow-plan 在 P3 PRD 合成后、P4 拆解前新增 P3.5 步骤，向用户展示 PRD 的 `### 声明的测试接缝` 清单，请求确认。
2. **seam 清单格式**：SPEC.md 的 `## Seam 分析` 章节下新增 `### 声明的测试接缝` 固定子节，每行 `- seam: <测试文件> -> <被测模块>`（机器可读）。
3. **契约测试**：`tests/test_seam_contract.py` 断言声明的测试文件存在、且其导入的被测模块与声明一致。

## Seam 分析

### 测试接缝
- 契约测试自身是纯函数：解析 spec 的 `- seam:` 行 → 检查测试文件存在 → 检查被测模块引用一致。
- 隔离：无外部依赖（文件系统 + 正则解析），无需 mock。

### 验收可测性
- 每项验收有明确 pass/fail。
- 边界：无 seam 行 spec（跳过）、seam 指向不存在的测试文件（失败）、seam 指向错误模块（失败）、正确 seam（通过）。

## 用户故事

1. 作为计划者，我想要 PRD 后确认测试接缝，以便拆解粒度正确、Do 阶段无返工。
2. 作为审查者，我想要 seam 契约测试，以便发现 PRD 声明与实际测试漂移。

## 实现决策

**架构决策已记入 ADR-0018**。要点：

- 新增/修改模块：
  - `flows/flow-plan/SKILL.md`：新增 P3.5 seam 确认步骤 + P6 门禁检查（PRD 含 `### 声明的测试接缝`）。
  - `templates/to-spec/SPEC.md`：新增 `### 声明的测试接缝` 子节格式说明。
  - 新增 `tests/test_seam_contract.py`：契约测试（解析 seam 行 → 断言文件+模块一致）。
- 数据模型：无（spec 文档格式约定）。
- 术语：`声明的测试接缝`（spec 中机器可读 seam 清单，记入 CONTEXT.md）。

## 测试决策

- 好的测试定义：仅测 seam 契约的可观察行为（解析 + 文件存在 + 模块一致），不测 skill 措辞。
- 被测模块：`tests/test_seam_contract.py` 的 seam 解析纯函数 + 契约断言。
- 先例：`tests/test_ticket_dag.py` 的纯函数 fixture 模式；T0231 source 契约、T0232 词汇契约。

## 验收标准

- [ ] AC-1: `flow-plan` 含 P3.5 seam 确认步骤（P3 后 P4 前）
- [ ] AC-2: `SPEC.md` 定义 `### 声明的测试接缝` 子节与 `- seam: <测试> -> <被测>` 行格式
- [ ] AC-3: 契约测试断言声明的 seam 测试文件存在
- [ ] AC-4: 契约测试断言测试文件引用的被测模块与声明一致
- [ ] AC-5: 无 `- seam:` 行的 spec 跳过（不追溯历史）
- [ ] AC-6: 全量测试无回归（现有 + 新增）

## 范围外

- 不追溯历史 spec（缺失 seam 行即跳过）。
- 不强制 research/documentation/design/review 场景。
- 不实现 Do 阶段 seam 实际测试（tdd 技能已有）。

## 备注

- 机制同构 T0231 source 术语契约、T0232 词汇契约：机器可读 + 契约测试守护。
- P6 门禁只检查子节存在，P3.5 负责向用户展示确认。

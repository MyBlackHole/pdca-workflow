# 可执行 convergence 证据验证器

## 问题陈述

- **现状**：现有 evidence gate 验证 manifest schema、文件边界、size 和 digest，但不检查 PRD AC 是否全覆盖，也不验证 `meta.convergence → AC → evidence ID` 支撑链。
- **目标**：在 Do→Check 转换前，以确定性代码拒绝缺失、悬空或不匹配的证据映射。
- **差距**：`verify-convergence` 目前依赖 AI 手工比对，结果不可重复且可能把“文件存在”误判为“结论有证据”。

## 解决方案

1. 保留 `task.meta.convergence` 作为 Plan 原始目标。
2. PRD 的 `## 验收标准` 下按 Markdown checkbox 顺序确定 `AC-1`、`AC-2`……。
3. Do 收尾生成结构化 convergence map，固定以 evidence ID 和 kind `convergence-map` 登记。
4. map 每项包含从 1 开始的 convergence index、与 task 完全相同的文本、至少一个 AC 和至少一个非 map evidence ID。
5. Do→Check 硬门禁同时验证：
   - 所有 PRD AC 被非 map evidence 覆盖；
   - 每条 convergence 恰好出现一次；
   - AC 和 evidence ID 均存在；
   - 每个引用 AC 至少由一个所列 evidence 的 manifest criteria 支持。
6. map 本身只描述关系，不计入 AC 覆盖或 convergence 支撑。
7. 提供独立 JSON 输出命令，便于 Check、CI 和故障定位复用。

## Seam 分析

### 测试接缝

- 核心 Seam：给定临时 task/PRD/record/evidence manifest/convergence map，返回稳定 `Issue` 列表。
- CLI Seam：给定 `--task-dir`，以 JSON 输出 valid 与 issues，并用退出码表达 pass/fail。
- 转换 Seam：现有 `transition-phase.py` 调用 `gate_issues`，不另建平行门禁实现。
- 全部使用临时文件系统夹具；无需网络、模型或新增依赖。

### 验收可测性

- 每种缺口使用单一故障夹具，断言稳定错误码。
- 同一个“现有 evidence gate 可接受”的夹具，加入新验证后必须被拒绝，形成前后配对证据。
- 有效任务必须通过核心函数、CLI 和 Do→Check 三层验证。

## 用户故事

1. 作为 Check 审查者，我希望每条收敛结论都能回链到明确 AC 和证据，以免 AI 凭文件存在宣称通过。
2. 作为任务执行者，我希望缺口返回稳定错误码，以便直接修复映射而不是重新解释整套流程。
3. 作为维护者，我希望验证逻辑只实现一次，并被 CLI 与阶段转换共同复用。

## 实现决策

- 新增 `pdca.convergence/v1` JSON Schema。
- 核心验证函数返回现有 `Issue` 类型，不引入第二套错误模型。
- Do→Check 调用核心 convergence 验证；已完成的历史转换不追溯重放。
- convergence map 必须先登记到 evidence manifest，利用现有 size/digest 保护其不可变性。
- 解析器只接受规范的 `## 验收标准` 与 checkbox，不增加旧格式或多语言兼容分支。
- 架构决策见 `ADR-0003`。

## 测试决策

稳定错误码至少包括：

- `ACCEPTANCE_CRITERIA_MISSING`
- `ACCEPTANCE_CRITERION_UNCOVERED`
- `CONVERGENCE_MAP_MISSING`
- `CONVERGENCE_MAP_INVALID`
- `CONVERGENCE_ITEM_MISSING`
- `CONVERGENCE_ITEM_DUPLICATE`
- `CONVERGENCE_ITEM_UNKNOWN`
- `CONVERGENCE_TEXT_MISMATCH`
- `CONVERGENCE_CRITERION_UNKNOWN`
- `CONVERGENCE_EVIDENCE_UNKNOWN`
- `CONVERGENCE_SUPPORT_MISSING`

## 验收标准

- [ ] 完整的 PRD、evidence 和 convergence map 通过核心函数与 CLI。
- [ ] PRD 无规范验收清单时返回 `ACCEPTANCE_CRITERIA_MISSING`。
- [ ] 任一 AC 仅被 convergence map 或完全未被证据覆盖时返回 `ACCEPTANCE_CRITERION_UNCOVERED`。
- [ ] map 缺失或未以固定 ID/kind 登记时返回 `CONVERGENCE_MAP_MISSING`。
- [ ] map JSON 无法解析或不满足 schema 时返回 `CONVERGENCE_MAP_INVALID`。
- [ ] task 中任一 convergence 缺项、重复或出现范围外 index 时，分别返回 `CONVERGENCE_ITEM_MISSING`、`CONVERGENCE_ITEM_DUPLICATE`、`CONVERGENCE_ITEM_UNKNOWN`。
- [ ] index 对应文本与 Plan 原文不一致时返回 `CONVERGENCE_TEXT_MISMATCH`。
- [ ] map 引用未知 AC 时返回 `CONVERGENCE_CRITERION_UNKNOWN`。
- [ ] map 引用未知或 map 自身 evidence ID 时返回 `CONVERGENCE_EVIDENCE_UNKNOWN`。
- [ ] 所列 evidence 的 criteria 不支持所列 AC 时返回 `CONVERGENCE_SUPPORT_MISSING`。
- [ ] Do→Check 阶段转换在上述任一错误存在时失败关闭。
- [ ] 配对夹具证明新验证器至少拒绝一种旧 evidence gate 会接受的错误。
- [ ] 全部既有单元测试和确定性夹具通过，且不新增第三方依赖。

## 范围外

- 清理 16 个旧格式活跃任务。
- research 来源链 validator。
- Agent trace、checkpoint、调用预算与 safe-output。
- 用 LLM 判断证据内容的语义充分性。
- 为非规范 PRD 或旧 convergence 数据增加兼容解析。

## 备注

- 该验证器提高的是证据链结构准确度，不声称提高真实模型任务成功率。
- 若实现只能检查字段存在、不能改变至少一种现有错误判定，则删除实现。

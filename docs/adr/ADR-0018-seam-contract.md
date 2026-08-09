# ADR-0018: seam 确认门禁与 PRD seam 契约

- 日期: 2026-08-09
- 状态: 已确认（plan 阶段固化决策方向）

## 背景

穷尽审查 mattpocock/skills 全部 37 个技能后，确认唯一剩余实质可证明提升：
`to-spec/SKILL.md` 步骤 2 要求"先 sketch 测试接缝 → 与用户确认 seam 匹配
预期 → 再写 spec"。

PDCA 现状差距：
- `templates/to-spec/SPEC.md` 有 `## Seam 分析` 章节，但 `flow-plan` P1-P3
  不强制与用户确认 seam。
- seam 决策推迟到 Do 阶段由 `skills/tdd/SKILL.md` 兜底确认，返工成本高。
- PRD 声明的 seam 与实际测试 seam 无一致性守护。

## 决策

- **seam 确认位置**：flow-plan 新增 **P3.5** 步骤（P3 PRD 合成后、P4 拆解前），
  向用户展示 PRD `### 声明的测试接缝` 清单，请求确认。
- **seam 清单格式**：SPEC.md 的 `## Seam 分析` 章节下新增固定子节
  `### 声明的测试接缝`，每行 `- seam: <测试文件路径> -> <被测模块路径>`
  （机器可读，同构 T0232 词汇契约）。
- **P6 门禁**：P6 终审校验 PRD 含 `### 声明的测试接缝` 子节（缺失即拒绝）。
- **契约测试**：新增 `tests/test_seam_contract.py`，断言声明的 seam 测试文件
  存在，且其导入/引用的被测模块与声明一致。
- **覆盖范围**：仅约束 development/bugfix 场景的 spec；research/documentation/
  design/review 无测试产物不强制。
- **追溯策略**：不追溯历史 spec，契约只守护新 spec；无 `- seam:` 行的 spec
  跳过（缺失即无声明 seam）。

## 备选方案与取舍

- **P3.5 后 vs P2 内 vs P6 终审**：seam 影响拆解粒度（P4），故放 P3 后 P4 前；
  P6 终审过晚，P2 过早（PRD 未成型）。
- **明确 seam 清单 vs 自由文本**：自由文本无法被确定性解析，违背"可证明"要求。
- **文件+模块一致 vs 仅文件存在**：文件存在只防目录漂移；模块一致才是
  "seam 对齐"本质（同构 T0231 source 术语、T0232 词汇契约）。
- **不追溯 vs 追溯**：历史 spec 缺 seam 信息，追溯成本高收益低；
  与 T0232 schema"旧任务不强制补齐"一致。

## 影响

- `flows/flow-plan/SKILL.md`：新增 P3.5 步骤 + P6 门禁检查。
- `templates/to-spec/SPEC.md`：新增 `### 声明的测试接缝` 子节格式说明。
- 新增 `tests/test_seam_contract.py`。
- `pdca/CONTEXT.md`：记录 `声明的测试接缝` 术语。

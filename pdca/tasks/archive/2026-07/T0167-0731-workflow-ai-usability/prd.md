# PRD — T0167 工作流 AI 可用性提升

## 0. 已确认决策（P2 Grill）

- B: guidance 为**可选字段**，旧 consumer（transition-phase / doctor / validate-workflow）向后兼容，仅输出增加字段
- C: --replace 采用**文件+manifest 双保留**：旧文件重命名 `<id>.superseded.<ts>`，旧 manifest 行加 `superseded_by`，新条目追加
- D: PRD 格式校验加在 **plan→do 门禁**（acceptance_criteria 可解析即通过），内容校验仍由 do→check convergence 负责

## 1. 问题陈述

今天执行 T0166（时间线加固）与 T0165 证据登记时，AI（本会话）暴露 4 个工作流摩擦点，全部是"机制迫使 AI 手写/猜测/绕过"而非能力不足：

| # | 摩擦点 | 现场实证 |
|---|--------|---------|
| A | AI 手写 clarifications.jsonl 时间戳 | T0166 登记 final_confirmation 时编造 at=20:25（真实 20:21），T0164 违规同根源 |
| B | 失败消息无修复指引 | ACCEPTANCE_CRITERIA_MISSING 仅"must contain Markdown checkboxes"，T0165 修复猜 2 轮 |
| C | evidence 登记后无法安全修正 | convergence-map 内容错误时被迫手工删 manifest 行重登，绕过不可变约束 |
| D | PRD 格式校验太晚 | T0165 用 `### AC-x` 格式，do 收尾才报错，返工成本最高 |

**目标**: 四项机制改进全部落地并有测试覆盖；每项改进附"对 AI 工作流的提升论证"（现状→痛点→改进→提升度量）。

## 2. 候选方案与初步 AI 工作流提升论证

### A. append-confirmation CLI
- **方案**: 新脚本 `scripts/append-confirmation.py`：`--task-dir --source final_confirmation|check_confirmation|direction_confirm --response confirmed --summary "..."`，自动填真实 `now`（datetime.now(timezone.utc) 转本地 +08:00 ISO），按 `schemas/clarification.schema.json` 校验后追加 clarifications.jsonl；校验失败不写文件
- **现状**: AI 手写 JSONL 行（含 ISO 时间）
- **痛点**: 时间格式错误、编造时间戳（今天 2 次实证）、JSON 转义错误
- **改进**: 时间戳由脚本生成，杜绝编造；schema 校验前置，失败即报
- **提升度量**: AI 登记确认零时间戳错误；与 T0166 的 FINAL_CONFIRMATION_AFTER_TRANSITION 门禁配合，从根源消除违规

### B. Issue guidance 字段
- **方案**: `pdca_core.py` 的 Issue dataclass 增加 `guidance: str | None = None`（可选，向后兼容）；为高频检查点补充修复指引：ACCEPTANCE_CRITERIA_MISSING、SCHEMA_INVALID、CONVERGENCE_SUPPORT_MISSING、FINAL_CONFIRMATION_AFTER_TRANSITION、RECEIPT_STATE_MISMATCH；CLI 输出（transition-phase / doctor / validate-workflow）统一含 guidance
- **现状**: Issue 只有 code/path/message（描述性），无"怎么修"
- **痛点**: AI 收到拒绝后猜修复方式（T0165 PRD 格式猜 2 轮）
- **改进**: 每条错误带可执行步骤（如"在 PRD 添加 `## 验收标准` 段，每项 `- [ ] AC-x: ...`"）
- **提升度量**: 收到拒绝到修复成功的往返次数降低（本次基线 2 轮）

### C. evidence 安全替换
- **方案**: `register-evidence.py` 增加 `--replace <id>`：旧文件重命名 `<id>.superseded.<ts>`，旧 manifest 行加 `superseded_by` 标记（新 id），新条目登记；全程 CLI，失败回滚不写 manifest
- **现状**: 重复 id/文件名被拒，AI 被迫手工删 manifest 行（今天实证）
- **痛点**: 手工编辑不可变记录，违反 ADR-0004 原则，有损坏风险
- **改进**: 替换全程 CLI 原子化，旧条目保留审计链
- **提升度量**: AI 不再手工编辑 manifest；替换操作幂等可重试

### D. PRD 验收标准早期校验
- **方案**: plan→do 转换门禁（transition-phase.py）增加 PRD 验收标准格式校验（复用 `acceptance_criteria` 解析，解析失败返回 `PRD_ACCEPTANCE_FORMAT_INVALID` 拒绝转换）
- **现状**: 格式错误到 do 收尾 validate-convergence 才暴露
- **痛点**: 返工发生在最晚点（T0165 实证）
- **改进**: Plan 阶段失败，成本最低
- **提升度量**: PRD 格式错误在 plan→do 即拦截，do 阶段零 PRD 格式返工

## 验收标准

- [ ] AC-1: `append-confirmation.py` 可追加三类 confirmation（final_confirmation / check_confirmation / direction_confirm），时间戳自动生成且非未来时间
- [ ] AC-2: 高频检查点（≥5 处）Issue 输出含 guidance；旧消费方无回归
- [ ] AC-3: `register-evidence.py --replace` 原子替换：旧文件 .superseded、旧行 superseded_by、新条目追加；失败不污染 manifest
- [ ] AC-4: plan→do 门禁拒绝 `### AC-x` 标题式 PRD（构造用例返回 PRD_ACCEPTANCE_FORMAT_INVALID）
- [ ] AC-5: 现有测试无回归（≥70 passed）；新增测试覆盖 A/B/C/D
- [ ] AC-6: PRD 中每项改进均有 AI 工作流提升论证（现状→痛点→改进→提升度量）

## 4. 实施拆解

- **T4-A**（script+test）: append-confirmation.py + 3 用例
- **T4-B**（core+test）: Issue.guidance 字段 + 5 处检查点补 guidance + 2 用例
- **T4-C**（script+test）: register-evidence --replace + 3 用例
- **T4-D**（gate+test）: plan→do PRD 格式门禁 + 2 用例
- **T4-E**（verify）: 全量回归 + 文档同步（SKILLS-INDEX / register-evidence 技能 / flow-plan 提及门禁）

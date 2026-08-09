# PRD — 增强 diagnosing-bugs 技能（D1-D6）

## 背景

T0242 系统化审查 mattpocock/skills，深挖确认本地 `skills/diagnosing-bugs/SKILL.md`
（55 行，Phase1-6 骨架完整）相对原文缺失 6 处细节（D1-D6），其中 D1（安全）
与 D3（门禁）价值最高。本任务按 D1>D3>D2>D4>D5>D6 优先级补齐。

## 需求

### R1 Redact 安全章节（D1）
`skills/diagnosing-bugs/SKILL.md` 新增前置约束（Phase 1 之前）：
- 运行命令前先检查输入/输出/制品，用 `<REDACTED>` 替代敏感内容
- 凭据/密钥/内网地址留环境变量，不落盘、不写入日志
- 制品粘贴只引关键行，不整段输出
- 目的：调试输出不泄露凭据/header

### R2 无环显式停止门禁（D3）
Phase 2 增加显式门禁：
- 若无法建立通过/失败反馈环，列出已尝试的构造方式，向用户要环境/制品/
  临时插桩权限
- 无反馈环不得进入 Phase 3 假设阶段
- 目的：防止无环瞎猜

### R3 非确定性 bug 处理（D2）
Phase 2 增加非确定性 bug 指引：
- 目标从"干净复现"改为"提高复现率"：触发 100×、并行跑、收窄时序窗
- 1% flake 不可调试，50% 可调试（设复现率阈值）
- 目的：能力补齐

### R4 HITL 兜底脚本（D4）
Phase 1 第 10 项（HITL bash script）补充：提供 `hitl-loop.template.sh`
模板文件路径（人工点击时仍结构化驱动，每次交互记录结果）
- 目的：人工参与时仍保持循环结构化

### R5 post-mortem 架构移交（D5）
Phase 6 强化：
- 除"什么能阻止此 bug？"外，若答案涉及架构（无好 seam、耦合），
  明确转 `improve-codebase-architecture` 技能，不留在当前循环
- 目的：闭环，架构问题有后续动作

### R6 CONTEXT 前置 + 假设双向预测（D6）
- Phase 1 前：若仓库有 CONTEXT.md/ADR，先读以获取共享语言
- Phase 3：假设格式改为双向预测——"If X is the cause, changing Y will make
  the bug disappear / changing Z will make it worse"
- 目的：上下文对齐 + 假设可证伪性（反证分支）

### R7 测试
契约测试守护 D1-D6 落地点（机器可读断言），复用 `seam_contract` 模式：
- 断言 SKILL.md 含关键字符串：`REDACTED`、无环停止约束、`make it worse`、
  `hitl-loop.template.sh`、`improve-codebase-architecture`
- 现有测试全量回归通过

## 验收标准

- [ ] AC-1: SKILL.md 含 Redact 前置约束（R1）
- [ ] AC-2: SKILL.md 含无环显式停止门禁（R2）
- [ ] AC-3: SKILL.md 含非确定性 bug 指引（R3）
- [ ] AC-4: SKILL.md 含 HITL 模板路径（R4）
- [ ] AC-5: SKILL.md 含 post-mortem 架构移交（R5）
- [ ] AC-6: SKILL.md 含 CONTEXT 前置与假设双向预测（R6）
- [ ] AC-7: 契约测试守护上述落地点（R7）
- [ ] AC-8: 全量测试通过，内容预算豁免记录在案

## 收敛条件

- [ ] CC-1: 上述 AC 全部满足
- [ ] CC-2: 内容预算（SKILL.md 版本化 bytes baseline）增长豁免已按流程记录
- [ ] CC-3: D1-D6 均有机器可读断言守护（不靠人肉检查）

### 声明的测试接缝

- seam: tests/test_diagnosing_bugs_enhance.py -> skills/diagnosing-bugs/SKILL.md

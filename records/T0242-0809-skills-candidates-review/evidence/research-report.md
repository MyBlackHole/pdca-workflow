# Research Report — mattpocock/skills 新候选系统化审查

## 结论速览

| 候选 | 本地现状 | 差距 | 判定 |
|------|---------|------|------|
| diagnosing-bugs | 已存在（55 行，Phase1-6 骨架完整） | 缺 Redact/非确定性/HITL/post-mortem 细节 | **增强**（中等价值） |
| code-review 双轴 | 已实现且超越（双轴 + Fowler 坏味 + agent.spawn 并行） | 无实质差距 | **不落地**（已覆盖） |
| CI 基础设施 | 缺失（无 .github/） | T0241 doctor 兜底，缺自动触发 | **候选**（依赖平台） |
| handoff/wayfinder | 完整实现（地图+票+类型，比 mattpocock 更结构化） | 无实质差距 | **不落地**（已覆盖） |

## 逐候选分析

### 1. diagnosing-bugs — 建议：增强

**现状**：本地 skills/diagnosing-bugs/SKILL.md（55 行）已含全部 Phase 骨架：
Phase1 反馈环 10 种构造方式 + Tighten、Phase2 复现最小化、Phase3 3-5 个
可证伪假设、Phase4 插桩、Phase5 correct seam 回归、Phase6 cleanup。

**差距**（mattpocock 原文 170 行 vs 本地 55 行）：
1. **Redact 章节**：先脱敏命令/输出/制品，用 `<REDACTED>` 替代，凭据留环境变量。
   本地缺此安全约束。
2. **非确定性 bug 处理**：目标非干净复现而是提高复现率（触发 100×、并行、
   收窄时序窗），1% flake 不可调试、50% 可调试。本地未覆盖。
3. **无法建环的显式停止**：明确列出尝试过什么，向用户要环境/制品/临时插桩
   权限，不得在无环时进入假设阶段。本地缺此门禁。
4. **HITL 兜底脚本**（hitl-loop.template.sh）：人工点击时仍结构化驱动。本地缺。
5. **post-mortem 问题**："什么能阻止此 bug？"若答案涉及架构（无好 seam、
   耦合）则转 improve-codebase-architecture。本地 Phase6 仅列 cleanup 项。

**可证明收益假设**：H1 增加 Redact 约束 → 减少凭据泄露风险（可测：脚本检查
SKILL.md 含 Redact 指引）；H2 增加"无环显式停止" → 减少无反馈环猜测（可测：
契约测试断言 SKILL.md 含停止条件）。

**落地成本**：小（单文件扩充 + 契约测试）。

**门禁兼容**：新增内容不触碰门禁判定，安全。

### 2. code-review 双轴 — 建议：不落地（已覆盖）

**现状**：本地 skills/code-review/SKILL.md 完整实现双轴审查（标准轴 + 规范轴
独立），并**超越** mattpocock 描述：
- agent.spawn 可用时双执行器并行，否则主会话保持两轴独立（不污染）
- 标准轴携带 Fowler 坏味基线（12 种坏味全列出）
- 规范轴区分 spec 缺失/范围蔓延/实现错误
- 400 字约束 + 独立呈现 + 发现数聚合
- 另有 code-review-checklist（253 行，C/C++/Rust/Go/Python 清单）

**差距**：无实质差距。mattpocock 描述与此一致。

### 3. CI 基础设施 — 建议：候选（依赖平台）

**现状**：仓库无 .github/workflows/。T0241 已用 pdca-doctor 作自动门禁兜底
（无 CI 时每次体检触发 seam 校验），check-seam-contracts 可无缝接入 CI。

**可证明收益**：引入 GitHub Actions 后每次提交自动跑 pytest + doctor + seam。
但收益证明依赖 CI 平台可用性，当前环境无法验证。

**判定**：**候选**——工具链就绪（T0240/T0241 成果可复用），但需用户决定是否
引入 GitHub 托管；无 CI 环境时 doctor 兜底已覆盖核心门禁。

### 4. handoff/wayfinder — 建议：不落地（已覆盖）

**现状**：本地完整实现：
- wayfinder（36 行）+ wayfinding-chart + wayfinding-work：决策地图（MAP.md +
  tickets/）+ 4 种票类型（Research AFK/Prototype HITL/Grilling HITL/Task 混合）
  + 已有/无地图方向判断
- handoff + handoff-work：压缩会话为脱敏交接文档

**差距**：本地比 mattpocock 更结构化（票类型枚举 + 地图目录约定）。无实质差距。

## 综合判定

**唯一值得落地的增强是 diagnosing-bugs 的 5 处细节**（Redact/非确定性/显式
停止/HITL/post-mortem），可证明收益中等，成本小。其余三候选已覆盖或依赖外部
平台。

**与 T0233 预判一致**：mattpocock/skills 可证明空间经 T0230-T0233 已系统收割，
本次 4 新候选仅 1 处有增强空间，印证"后续新候选需重新审查"的价值。

## 适用边界

- diagnosing-bugs 增强若落地，需先走 Improvement Candidate → Improvement Task
  流程（本任务仅审查报告，不落地）。
- CI 候选落地依赖用户引入 GitHub 托管的决策。

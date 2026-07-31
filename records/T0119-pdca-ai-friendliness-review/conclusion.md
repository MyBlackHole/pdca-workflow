---
schema: pdca.asset/v1
id: T0119-pdca-ai-friendliness-review
phase: check
source_ids: [E-T0119-001, E-T0119-002]
---

## 上下文

PDCA 工作流设计为 AI Agent 执行协议，其流程本身对 AI 的友好度直接影响执行效率和质量。本次审查从 AI Agent 执行视角，按 7 个维度（入口引导、流程可导航、门禁自检、工具对齐、上下文效率、容错与恢复、人机分工清晰度）对 PDCA 流程进行了系统性审查。

审查覆盖：AGENTS.md → flows/ 四阶段 → skills/ 核心技能 + 辅助技能 → CONTEXT.md/SKILLS-INDEX/ADR/模板。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 流程整体对 AI 较为友好，存在局部改进空间 | ✅ 确认 — 综合评分 80.6%，入口引导和流程可导航表现优秀 |
| 容错与恢复是最大薄弱环节 | ✅ 确认 — 2.5/5，无回滚、无部分推进、subagent 失败无恢复路径 |
| 门禁条件可转自动化 | ✅ 确认 — 已创建 validate-gate.sh 校验脚本 |
| disable-model-invocation 是非标准语法 | ✅ 确认 — 4 个技能文件使用此标记 |

## 分析

### 优势（AI 友好）

1. **入口路由设计**：AGENTS.md 明确定义仓库用途和路径引用，AI 首步清晰
2. **flow-check 精简**：70 行闭环，与子技能解耦良好，是四阶段中最优设计
3. **register-evidence 工具对齐**：18 行的 bash 命令式技能，AI 零摩擦执行
4. **三明治对齐机制**：flow-plan 2b 方向确认 + 6 方案终审的设计精巧

### 劣势（需改进）

1. **容错与恢复（2.5/5）**：流程无回滚机制，阶段推进错误后无法回退
2. **门禁自检（3.6/5）**：门禁条件以自然语言描述，AI 自主校验存在误差风险
3. **工具对齐（3.55/5）**：部分步骤依赖 AI 自行判断，缺乏辅助脚本
4. **disable-model-invocation**：非标准 frontmatter，不同 AI 模型理解不一致
5. **flow-do 路径编号**：六路径各自从 1 开始编号，阅读和引用易混淆

### 改进落地

已落地改进：
- 新增 `scripts/validate-gate.sh` 脚本，实现四阶段门禁条件的自动化校验
- 更新 `advance-phase/SKILL.md`，在每阶段门禁说明后增加自动校验命令引用

## 失败原因

不适用（本次审查结论为 confirmed，非 rejected/partial）。

## 适用边界

- 本结论仅针对 PDCA 流程的 AI 友好度评估，不评估流程的功能完备性
- 审查基于模拟执行法，未在实际多模型环境中验证行为差异
- disable-model-invocation 的兼容性评估需在具体 AI 工具中实测

## 下一轮建议

1. **P0: 统一 disable-model-invocation** — 在 4 个技能文件中替换此非标准语法
2. **P1: flow-check rejected/partial 处理分支** — 补充 Act 阶段对非 confirmed 结论的处理逻辑
3. **P1: flow-do 路径编号重排** — 六路径改用 A-F 前缀
4. **P2: AGENTS.md 快速启动** — 增加 $PDCA_HOME fallback 说明和首次使用指南
5. **P2: README/AGENTS.md 职责梳理** — 减少入口文档功能重叠

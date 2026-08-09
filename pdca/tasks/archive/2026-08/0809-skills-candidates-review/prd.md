# PRD — mattpocock/skills 新候选系统化审查

## 背景

T0233 conclusion：mattpocock/skills 可证明空间经 T0230-T0233 四轮已系统收割，
后续新候选需重新审查其技能更新。用户要求对 mattpocock/skills README 中
4 个候选（diagnosing-bugs、code-review 双轴、CI 基础设施、handoff/wayfinder）
做系统化审查，判定各自落地/不落地/增强，产出审查报告供后续决策。

## 范围

- 候选：diagnosing-bugs、code-review 双轴、CI 基础设施、handoff/wayfinder
- 深挖 mattpocock 各候选 SKILL.md 原文，对比本地已有技能
- 评估标准：可证明收益优先（能否用测试/轮数/指标证明），其次落地成本与重复度
- 产出：审查报告（research-report.md），不落地任何代码

## 需求

### R1 逐候选深挖对比
对每个候选拉取 mattpocock SKILL.md 原文，与本地已有技能做差距对比。

### R2 可证明收益假设
每个候选列出可证明收益假设（用 T0230 方法论：假设→验证方式）。

### R3 审查报告
输出 research-report.md：每候选 {现状, 差距, 收益假设, 可证明性, 落地成本,
门禁兼容, 建议}。

## 验收标准

- [ ] AC-1: 4 个候选各有原文对比与差距分析
- [ ] AC-2: 每候选有可证明收益假设与验证方式
- [ ] AC-3: 每候选有落地/不落地/增强判定及依据
- [ ] AC-4: 报告含适用边界与门禁兼容性说明
- [ ] AC-5: 结论沉淀至 knowledge/

## 收敛条件

- [ ] CC-1: 上述 AC 全部满足

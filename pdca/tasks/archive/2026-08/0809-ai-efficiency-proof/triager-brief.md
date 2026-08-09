# Triage Brief — T0230 借鉴 mattpocock/skills 提效

## 分类

- category: `enhancement`
- scenario_type: `development`（含审查 + 修改）

## 验证结果

- 已抓取 github.com/mattpocock/skills README + writing-for-agents + codebase-design 全文。
- 确认核心提效概念：context pointer 措辞、leading words（预训练词锚定）、no-op 检测（不改变行为则删）、completion criteria（clarity + demand）、progressive disclosure、否定改肯定。
- 确认本仓库已有对应物：writing-great-skills、domain-modeling、grilling、tdd、audit-skill-content.py。

## 查重结果

| 记录 | 关系 |
|------|------|
| R0086-0727-compare-skills | 对比过 mattpocock，给出 5 条建议（P0 提取循环/ask-matt 等，多数已落地） |
| T0119 / T0120-T0123 | AI 适应性多维审查（已落地） |
| T0167-0731-workflow-ai-usability | CLI/guidance/evidence 四项机制（已落地） |
| R0138-skill-content-audit | 内容成本审计，flow-plan 降 35.76% |
| R-ai-fitness-review-001 | 八维度审查，SKILLS-INDEX 过期（Critical） |

**结论**：无重复任务。本次新增点是"对照 mattpocock 的 writing-for-agents 具体杠杆（leading words、no-op、completion criteria、context pointer）审查并落地可证明的修改"，此前未做过。

## 信息缺口（进入 Grill）

1. 修改范围边界。
2. "有证明"的操作化标准。
3. 是否新增技能。

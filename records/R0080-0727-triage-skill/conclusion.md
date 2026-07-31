---
schema: pdca.asset/v1
id: R0080-0727-triage-skill
phase: check
source_ids: [E01, E02]
---

## 上下文
在 Plan 阶段之前引入 triage 门禁。参考 mattpocock/skills 的 triage 状态机模式，适配无 issue tracker 的文件系统工作流。

## 假设与结果
- **假设**：四态分类（needs-triage→needs-info→ready-to-plan→wontfix）能覆盖常见输入场景 → **确认**
- **假设**：grill 联动能补齐信息缺口 → **确认**：步骤 4 明确引用 grill
- **假设**：查重能减少重复 task → **确认**：覆盖 tasks/ + knowledge/ + out-of-scope/

## 分析
一次通过。核心改动：skills/triage/SKILL.md + flow-plan 步骤 0 + knowledge/out-of-scope/

## 适用边界
- 当前无 issue tracker，任务目录即"tracker"
- wontfix 不通知任何人（无通知机制），仅写文件归档
- ready-to-plan 后 triage 的产出（triager-brief.md）可能包含 Plan 阶段需要的信息缺口

## 下一轮建议
1. 实现 wayfinder 技能（多 session 规划）
2. 用 triage + 完整 PDCA 跑一个真实业务任务
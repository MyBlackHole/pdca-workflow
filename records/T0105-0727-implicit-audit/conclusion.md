---
schema: pdca.asset/v1
id: T0105-0727-implicit-audit
layer: experience
summary: 审查 PDCA 隐含问题并修复 11 项
tags: [audit, numbering, invocation, ADR, check-gate]
---

# 结论: T0105 — 隐含问题审查

## 发现与修复

| 类别 | 项数 | 修复 |
|------|------|------|
| 步骤编号断裂 | 3 | Path A/C/F 编号统一 |
| 调用约定冲突 | 3 | triage/domain-modeling/handoff fail-soft 注释 |
| 产出物缺失 | 2 | ADR-0001 创建 + triager-brief 引用删除 |
| 门禁不平衡 | 2 | check 确认闸门 + advance-phase 基本校验 |
| 证据登记 | 1 | do→check 门禁验证 manifest 存在 |

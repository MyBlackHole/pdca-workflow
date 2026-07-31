---
schema: pdca.asset/v1
id: R0085-0727-grill-alignment
phase: check
source_ids: [evt-flow-plan, evt-grill]
---

## 上下文
用户反馈 Plan 阶段缺少 grill 后的目标对齐确认行为：AI 追问完直接进入 to-spec，没有显式向用户总结对齐结果。

## 假设与结果
- **假设**：需要增加对齐确认门禁，要求 Grill 走完决策树后必须向用户做对齐总结才能推进
- **结果**：✅ 已修复 — 两个改动点

## 分析

| 改动 | 文件 | 说明 |
|------|------|------|
| 2a + 2b 拆解 | flow-plan | 步骤 2 拆为 Grill 追问 + 对齐确认门禁，用户确认后才能进入 to-spec |
| 退出条件完善 | grill | 新增对齐总结格式和用户确认/修改的收敛逻辑 |
| 步骤 6 重命名 | flow-plan | "方案确认展示"→"方案终审"，明确是最终签字确认而非方向对齐 |

**设计说明**：
- 两个对齐点各有分工：2b = 方向确认（"方向对吗？"），6 = 终审（"方案完整吗？"）
- 用户不确认则回到 2a 继续追问，不会带着分歧进入 to-spec

## 适用边界
- 仅影响 Plan 阶段流程，与 Do/Check/Act 无关
- grill 的 `disable-model-invocation: true` 语义不变

## 下一轮建议
PRD 和代码修改已在记录前完成，验证通过后直接归档。
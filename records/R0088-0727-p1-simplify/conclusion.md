---
schema: pdca.asset/v1
id: R0088-0727-p1-simplify
phase: check
source_ids: [evt-grill, evt-grilling, evt-triage, evt-writing-great-skills]
---

## 上下文
基于 mattpocock/skills 的对比分析，实施 P1 两项：极简化 user-invoked 技能 + 创建元技能。

## 分析

| 变更 | 行数变化 | 说明 |
|------|----------|------|
| `skills/grill` | 60→6 (-54) | 薄壳化，仅描述+委托 |
| `skills/grilling`（新增） | +52 | model-invoked，包含完整追问逻辑 |
| `skills/triage` | 121→53 (-68) | 删除冗余描述和模板 |
| `skills/writing-great-skills`（新增） | +76 | 元技能，定义编写规范 |
| flow 引用更新 | 3 files | grilling 替换 grill |

**组合效果**：
- `grill`（user-invoked，6行）→ 委托给 `grilling`（model-invoked，52行）
- 模式对齐 mattpocock：`grill-me` → `grilling`
- writing-great-skills 定义了 6 种失败模式的识别和修复方法

## 下一轮建议
P2（flow 引用技能而非内联步骤）已在 P0 中大部分完成。建议进入下一组优化或创建真实业务任务验证流程。
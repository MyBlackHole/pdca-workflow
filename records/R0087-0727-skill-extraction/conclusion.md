---
schema: pdca.asset/v1
id: R0087-0727-skill-extraction
phase: check
source_ids: [evt-register-evidence, evt-advance-phase, evt-verify-convergence, evt-write-conclusion, evt-ask-matt, evt-flow-do, evt-flow-check, evt-flow-plan]
---

## 上下文
参照 mattpocock/skills 的技能极简+可组合理念，从 flow-do/check/plan 中提取重复出现的步骤为独立 model-invoked 技能。

## 假设与结果
- **假设**：提取可复用技能 + 流程引用能减少冗余、提升可组合性
- **结果**：✅ 确认

## 分析

| 变更 | 文件 | 增减 |
|------|------|------|
| 新增 `register-evidence` | skills/ | +13 行 |
| 新增 `advance-phase` | skills/ | +12 行 |
| 新增 `verify-convergence` | skills/ | +13 行 |
| 新增 `write-conclusion` | skills/ | +17 行 |
| 新增 `ask-matt` | skills/（user-invoked） | +35 行 |
| 减重 `flow-do` | flows/ | -11 行（6 个证据步骤 + 6 个推进步骤→技能引用） |
| 减重 `flow-check` | flows/ | -32 行 |
| 减重 `flow-plan` | flows/ | -3 行 |
| **合计** | | **+90 / -46** |

效果：
- `register-evidence` 在 flow-do 的 6 条路径中复用 6 次，同时也可被 flow-check 引用
- `advance-phase` 在 flow-plan/do/check 三阶段复用
- 新技能增加了可组合性：任何流程步骤需要登记证据或推进阶段时，可直接加载对应技能
- 技能内容遵循 model-invoked 原则（无 `disable-model-invocation`），AI 可自主触发
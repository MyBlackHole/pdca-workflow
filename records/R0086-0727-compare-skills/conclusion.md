---
schema: pdca.asset/v1
id: R0086-0727-compare-skills
phase: check
source_ids: [evt-compare-report]
---

## 上下文
审查 mattpocock/skills 仓库的设计理念、技能结构和执行方式，与本 PDCA 工作流对比。

## 假设与结果
- **假设**：mattpocock/skills 在技能简洁度和可组合性上优于本流程
- **结果**：✅ 确认 — 具体差异见分析

## 分析

**本流程胜出领域**：
- 生命周期完整性（PDCA 四阶段）
- 不可变记录体系（records/ + manifest）
- 结论+判定机制（verdict / disposition）
- 知识沉淀（knowledge/）
- 场景分类（6 种 scenario_type）
- 跨会话桥接（handoff + 归档）

**mattpocock/skills 胜出领域**：
- 技能极简（grill-me 仅 3 行 vs 我们 60 行）
- 可组合性（implement→tdd→code-review 链式调用）
- 元技能保障（writing-great-skills）
- 用户/模型双通道分离（disable-model-invocation 运用更彻底）
- 路由器模式（ask-matt）

## 优化建议（5 项）

| 优先级 | 建议 | 说明 |
|--------|------|------|
| P0 | 提取可复用循环为独立技能 | register-evidence / verify-convergence / write-conclusion |
| P0 | 创建 ask-matt 路由器 | 解决用户不知如何入手的问题 |
| P1 | 极简化 user-invoked 技能 | 技能文件只负责描述和委托 |
| P1 | 创建 writing-great-skills 元技能 | 定义技能编写规范 |
| P2 | flow 引用技能而非内联步骤 | 减重 flow 文件 |

## 下一轮建议
开始实施 P0 优化项。
---
schema: pdca.asset/v1
id: ontology:concept/failure-mode
type: concept
layer: Knowledge
status: active
summary: AI 四大失效模式：驱动技能矩阵设计的根本分类
relations:
  specializes:
  - ontology:concept/pdca-task
attributes:
- name: applicability
  desc: 适用于所有新技能/流程资产的设计前置
  constraint: 见正文
  testable_signal: 检查新技能是否声明其针对的失效模式；治不了明确病的技能不应存在
---

# Failure Mode（失效模式）

AI 四大失效模式驱动技能矩阵设计——每个技能可回溯到它治的病。设计任何技能/流程资产时先写"它治哪个失效模式"；治不了明确病的技能不该存在。

## 四大失效模式

| 失效模式 | 修复技能族 |
|---------|-----------|
| #1 对齐失败（做出来的不是我想要的） | grilling 决策树族 |
| #2 冗长歧义（20 词说 1 词的事） | CONTEXT.md 共享语言 + wait-what 一句话纠偏 |
| #3 代码跑不起来（盲飞） | tdd @ pre-agreed seams + diagnosing-bugs 反馈回路 |
| #4 泥球化（AI 加速熵增） | codebase-design 深模块词汇 + improve-codebase-architecture 热点扫描 |

## 原则

- 新技能创建时必须声明其针对的失效模式
- 技能不应试图修复所有失效模式——聚焦一个，克制扩展
- 失效模式是技能分类的一等公民，不是事后注释

## 边界

失效模式枚举基于 mattpocock/skills v1.2.3 静态快照；项目活跃迭代，量化数据会过时。
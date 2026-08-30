---
schema: pdca.asset/v1
id: ontology:concept/codebase-design
name: Codebase Design
summary: 深模块设计：模块/接口/接缝/适配器/深度词汇
type: concept
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/domain-modeling
---

# Codebase Design

深模块设计是 AI 效率的核心词汇——用精确的架构术语替代模糊的通用词，让 agent 在讨论代码结构时零歧义。

## 词汇表（强制）

| 术语 | 含义 | 禁用词 |
|------|------|--------|
| **module** | 任何有接口与实现的单元（函数/类/包/跨层切片） | component, service |
| **interface** | 调用者使用模块所需的全部信息（类型签名+不变式+错误模式+配置） | API（过窄） |
| **seam** | 不编辑原地就能改变行为的位置；模块接口所在之处 | boundary |
| **adapter** | 在接缝处满足接口的具体实现，描述角色而非实质 | — |
| **depth** | 接口杠杆：每单位需学习的接口可驱动的行为量 | — |
| **leverage** | 调用者从深度获得的：每单位接口学习的更多能力 | — |
| **locality** | 维护者从深度获得的：变更/知识/验证集中于一处 | — |

## 深模块原则

1. **深模块优先**：大量行为通过简单接口暴露，而非暴露大量细节
2. **接口即契约**：interface 定义了调用者与模块之间的全部约定
3. **seam 即灵活性**：每个 seam 是一个可以替换 adapter 的位置
4. **depth 即效率**：深度越大，每单位接口学习的行为越多
5. **locality 即可维护性**：变更集中在少数位置

## AI 效率机制

- 精确词汇消除 agent 的歧义猜测
- 模块/接口/seam 词汇让架构讨论可验证
- depth/leverage/locality 提供量化评估维度
- 词汇表约束（禁用通用词）强制精确表达

## 边界

深模块词汇是设计时的判定标准，不是自动检查；契约测试只守护"词汇表存在"，不守护"用法正确"。


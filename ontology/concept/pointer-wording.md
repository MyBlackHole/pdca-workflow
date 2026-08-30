---
schema: pdca.asset/v1
id: ontology:concept/pointer-wording
type: concept
layer: Knowledge
status: active
summary: 指针措辞：上下文指针的措辞决定触发可靠性，弱措辞即方差 bug
relations:
  specializes:
  - ontology:concept/writing-for-agents
attributes:
- name: applicability
  desc: 适用于所有写给 AI 消费的上下文指针
  constraint: 见正文
  testable_signal: 检查指针是否前置首词；同义分支是否收拢；常载指针是否修剪
---

# Pointer Wording（指针措辞）

上下文指针的**措辞**（非其目标）决定触发可靠性——目标再强，弱措辞就是方差 bug：先改措辞，改不锋利才内联。

## 原则

- **前置首词**：指针靠首词做触发工作
- **一支路一触发词**：同义改写 = 同一分支写两遍，收拢；只保留真正不同的分支
- 常载指针每轮花费 token，比正文更需狠修剪
- 正文已携带的身份信息，指针不再重复

## 边界

指针措辞是写作时的判定标准，不是自动检查；契约测试只守护"章节存在"，不守护"用法正确"。
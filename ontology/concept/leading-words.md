---
schema: pdca.asset/v1
id: ontology:concept/leading-words
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/leading-words/1.0.0
summary: 锚定词：用预训练已有词锚定一类行为，以 token 而非句子重复
relations:
  specializes:
  - ontology:concept/writing-for-agents
attributes:
- name: applicability
  desc: 适用于所有写给 AI 消费的文档和技能
  constraint: 见正文
  testable_signal: 检查文档中是否存在自造词未用已有词锚定；同义短语是否收拢为单 token
---

# Leading Words（锚定词）

用预训练已有的词锚定一类行为，重复以 **token** 而非句子，累积分布式定义并招募模型已持有的先验。

## 原则

- 自造词不招募先验——要用定义 token 偿还，优先改用已有词
- 三处同义短语指一概念 → 收拢为单 token
- 双赢：更少 token + 更锋利的触发钩子
- 每个文档都在携带可被锚定词退休的复述

## 示例

- `_tight_` → "快速、确定性、低开销"的紧凑反馈循环
- `_red_` → "可证伪的失败信号"：模糊的门禁变成二值可观察状态（循环红了或没有）

## 边界

锚定词依赖模型先验——跨模型族（如中文模型）先验词不同，需本地验证。
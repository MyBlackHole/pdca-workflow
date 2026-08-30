---
schema: pdca.asset/v1
id: ontology:domain/skill-handoff-work
name: handoff-work
summary: Handle work handoffs between phases and team members.
description: Write a compact, redacted handoff record for a future session or agent.
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/handoff
    - ontology:concept/domain-modeling
---

---|-----|----------|------|
| 1 | 下一步需要本块作一手依据，或推理余量充足？ | **继续** | 零成本零损失，最先排除其余选项 |
| 2 | 本块全部内容对后续无关紧要？ | **清窗** | 最便宜的一手；误删相关上下文的代价单向（why 读 diff 也回不来） |
| 3 | 跨 harness/目录/同事/中途分叉支线？ | **交接（本技能）** | 买到的是可移植性；没有东西在旅行就不需要 |
| 4 | 任务可无人值守完成？ | **子代理** | 主会话原封不动 |
| 5 | 以上皆否 | **压缩** | 默认着陆点而非首选；压缩时下指令保住下一步所需 |

底层是一手源/二手源交换：除"继续"外每个动作都把一手源（信息全、噪声大、
腾挪小）换成二手源（有损、低噪、空间大）。只有当留下的成本大于收益才付
有损代价。

## 对话摘要存档（dialogue-log）

每次阶段转换前，向任务目录 `dialogue-log.md` **追加**一段摘要（≤2KB/段），四要素：

1. 本阶段讨论要点（≤5 条）
2. 被否决的备选及否决理由——防止后续 session 重新提议
3. 用户关键反应原话（与 clarifications 的 `captured:true` 条目互引）
4. 未解决即跳过的疑点

明确不做：全量逐句、常规 yes/no 确认、工具输出。涉密内容 Redact。

## 已知坑

- 记录须 compact 且保留决策链，供未来 session 恢复上下文；冗余细节会稀释可恢复性。
- 五问都是判断题且按序问——跳过前面直接压缩的典型失败是新会话对被摘要压扁的决策自信地错。

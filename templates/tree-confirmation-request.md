---
schema: pdca.tree-confirmation-request/v1.1
work_id: null
tree_revision: null
proposal_id: null
request_id: null
kind: tree_confirmation
manifest_ref: null
manifest_digest: null
work_conversation_ref: null
producer_ref: null
question: null
protocol_revision: 3.4.10
wait_policy_ref: null
wait_policy_digest: null
deadline: null
time_source_ref: null
graph_refs: []
readiness_ref: null
readiness_digest: null
---

# 工作级整树冻结request草稿

适用TREE-01/CONFIRM-01，不属于任何节点PDCA的任务请求；不得填写task_id或phase来复活旧根任务。所有null待真实填写，不预填批准。

## 对象、来源与核验

匹配work/tree/proposal/request/conversation和最终manifest_digest，读取全部固定闭包；旧seed确认、clarification、未定位来源、任何字节变化都不能冻结。response只允许confirmed/rejected/needs_change。receipt只有真实confirmed及复核闭包后才能形成。

## 拒绝或中断

拒绝保持未冻结，语义修订按节点新attempt；内容变化新proposal，冻结后变化新tree_revision。保留旧请求与回应；未知并发或部分写先核查，不伪造批准。清单不引用自身摘要及未来响应，回执单向引用已存在对象。

CONTROL-01负责请求终局和发布停止资格；过期只保持提案未冻结。freeze回执引用实际request-decision和图检查，不只引用response。时间/事件未知保持阻断，不让已结束节点重新发消息。

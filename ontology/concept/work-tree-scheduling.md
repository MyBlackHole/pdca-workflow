---
schema: pdca.asset/v2
id: ontology:concept/work-tree-scheduling
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: SCHED-01：就绪不自动派发
---

# SCHED-01：从 ready 事实产生候选，不自动派发

SCHED-01 不计算 dependency ready；它只消费 DEPENDENCY-01 已固定的 ready/stale 事实、工作树组成关系与用户已定义的 task seed，形成“现在有哪些候选可以提示用户”。只有用户明确选择的具名任务才有创建资格；根/child ready 或还有执行容量都不触发自动 spawn。

modeling 可按根→叶组织候选；projection/verification 的组合顺序只根据当前固定 dependency ready 事实和 scene 要求产生建议。SCHED 不重新验证 deliverable/version，也不读取依赖 task 活动历史。

具名批次授权只涵盖已经定义的任务和固定范围；后续展开出的孩子、新场景、新attempt另行操作。每阶段确认独立，任务A等待不影响任务B已获准执行。父Agent不轮询进度、不主动要求状态汇报、不把待用户状态当超时失败。

宿主只在真实事件或用户操作时处理候选与结果；未知创建只查原 request。共享资源资格由 RESOURCE-01/GATE-01 判断，上下文由 CONTEXT-01 选择；SCHED 不为填满容量改变这些事实。

新attempt需旧执行资格与副作用安全结束、用户明确授权；任务名可相同但原生实例不可复用。只允许读固定交付进行组合，不导入兄弟历史或用其PASS代替本节点验证。

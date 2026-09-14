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

# SCHED-01：就绪不自动派发

工作树表达组成，不是父Agent指挥链。宿主可以从固定seed、图与交付判断可用输入，但只有用户明确选择的任务才有创建资格；“根已完成”“孩子就绪”“还有容量”只产生建议，不触发自动spawn。

modeling按根→叶，孩子需要父seed固定交付；projection按叶→根，父组合需要必需孩子可用交付；verification先局部后组合。各节点仍完整PDCA，各自与用户沟通阶段目标。

具名批次授权只涵盖已经定义的任务和固定范围；后续展开出的孩子、新场景、新attempt另行操作。每阶段确认独立，任务A等待不影响任务B已获准执行。父Agent不轮询进度、不主动要求状态汇报、不把待用户状态当超时失败。

宿主只在真实事件或用户操作时处理消息／资源／结果；未知创建只查原请求。共享写资源互斥与上下文独立分开；无安全写权则阻断冲突，不为填满容量违权。

新attempt需旧执行资格与副作用安全结束、用户明确授权；任务名可相同但原生实例不可复用。只允许读固定交付进行组合，不导入兄弟历史或用其PASS代替本节点验证。

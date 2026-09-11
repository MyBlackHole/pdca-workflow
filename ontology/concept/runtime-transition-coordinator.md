---
schema: pdca.asset/v2
id: ontology:concept/runtime-transition-coordinator
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.0.0
summary: 宿主写入协调，不是父 Agent 审批
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-task
  - ontology:concept/capability-protocol
  - ontology:concept/pdca-transition
  - ontology:process/independent-work-review
---

# 宿主写入协调，不是父 Agent 审批

运行时只提供写入交接、消息路由、调度事件和恢复辅助；不担任每任务Do→Check的审查批准者，也不与子Agent同时写task.md。

当前Agent依据GATE-01和TRANSITION-01自行推进。真实用户确认由可信消息通道记录；独立审查由第三场景新Agent执行。

single_writer_best_effort不是文件锁、CAS或跨文件事务。任务要求更强语义时由CAP-01核验宿主能力；派发未知、重复写入者、固定包漂移或分叉按RECOVERY-01阻断。

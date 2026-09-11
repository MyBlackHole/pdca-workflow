---
schema: pdca.asset/v2
id: ontology:process/pdca-flow-model
type: process
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.0.0
summary: 三场景与当前任务阶段入口
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/process
  relates_to:
  - ontology:concept/pdca
  - ontology:concept/pdca-task
  - ontology:concept/pdca-recovery
  - ontology:process/work-scenarios
  - ontology:process/flow-plan
  - ontology:process/flow-do
  - ontology:process/flow-check
  - ontology:process/flow-act
---

# 三场景与当前任务阶段入口

新工作读取TREE-01/SCENE-01/SCHED-01，先从根建模；已有树按场景覆盖与就绪派发，不能跳过目标生成或把整树当一个任务。派发需TASK-01/CAP-01真实能力。

新节点任务Plan前分配全新Agent。已有task先RECOVERY-01恢复；不能因重复消息再spawn。新attempt与原恢复不同，必须新身份。

| phase | 动作协议 |
|---|---|
| plan | ontology:process/flow-plan |
| do | ontology:process/flow-do |
| check | ontology:process/flow-check |
| act | ontology:process/flow-act |
| archive | 只读；新attempt另起完整PDCA |

各阶段按需读取权威；每个任务均执行自己的TEST-01套件。独立审查属于REVIEW-01新场景，不是此分发器的父审批。

---
schema: pdca.asset/v2
id: ontology:concept/skill-mechanics
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.6
summary: 技能与流程的分工
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/skill-invocation-contract
  - ontology:concept/pdca-architecture
---

# 技能与流程的分工

流程决定当前阶段，技能描述如何完成契约内某动作。本项目领域skill节点可以直接阅读，不需要独立skills目录或专用命令。入口只指向本体，不复制规则。


## 定义、调用、实例

知识资产描述可复用动作；调用契约确定本次合法输入/输出、前置和失败处理；records记录真实任务的一次调用及证据。三者不得互相冒充。`skill-as-ontology`、`ontology-skill-model`是解释性资料，不为本条增加第二套权威或线性知识依赖。Agent只是使用者，能力与原生工具绑定按CAP-01；不要求平台专用adapter。

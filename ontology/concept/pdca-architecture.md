---
schema: pdca.asset/v2
id: ontology:concept/pdca-architecture
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.0.0
summary: 规则、执行与事实的三层边界
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca
  - ontology:concept/capability-protocol
  - ontology:concept/ontology-asset
---

# 规则、执行与事实的三层边界

本体是唯一规则来源，宿主提供工具执行，当前任务记录保存事实。入口负责定位，不复制规则；技能负责局部动作，不拥有生命周期。

核心质量约束分别归属根规则索引中的权威节点。检索知识按适用性和来源选取，阶段判定回链真实证据，知识候选与活动规则隔离。没有额外Registry、全局守护进程、平行JSON schema或脚本常量。

不同项目以明确授权根和任务契约区分；不自动写用户已有AGENTS、安装钩子或创建平台权限。引用路径必须可解析，缺失不以默认值替代。

工作组织遵循TREE-01的目标生成、逐节点执行和独立审查；知识图不是替代目标树的任务DAG。无父Agent阶段审批；宿主调度/路由与节点Agent的推理职责严格分离。

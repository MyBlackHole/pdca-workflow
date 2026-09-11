---
schema: pdca.asset/v2
id: ontology:concept/frontier
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.2.0
summary: 可执行树节点前沿
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/work-tree-scheduling
  - ontology:concept/pdca-task
  - ontology:process/work-scenarios
  - ontology:concept/work-dependency-graph
  - ontology:concept/resource-ownership
---

# 可执行树节点前沿

前沿是SCENE-01当前场景内尚未执行且满足SCHED-01就绪、输入和资源要求的节点集合。建模前沿自根向孩子推进；执行前沿从叶向组合父节点推进；审查先局部后汇聚。

父节点是否进入前沿只引用SCHED-01按scene判定。对于projection，必需直接孩子必须已完成完整任务、交付可用且版本固定；孩子仅ready/running或归档失败时，父不得启动。无需等待无关分支。归档失败不是可用交付；额外依赖不得形成环。宿主调度只使用公开固定输入/产物，不读取子Agent活动对话。节点内步骤计划与全树任务前沿区分。

前沿消费DEPENDENCY-01的已授权固定图；资源资格按RESOURCE-01，不拿active或知识库弱关联图推导启动。取消/接续使用CONTROL-01。

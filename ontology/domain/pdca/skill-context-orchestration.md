---
schema: pdca.asset/v2
id: ontology:domain/skill-context-orchestration
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 阶段上下文组织
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/select-task-subgraph
  - ontology:concept/pdca-task
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 阶段上下文组织

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

保留根规则索引、当前任务身份、固定契约与当前阶段必要指引；领域资料按需加载。当前任务恢复只读持久化记录。不得将协调器或其他任务活动对话复制给新子Agent。输出当前使用的文件/ID/版本清单，而不是声称上下文隔离已经实现。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。

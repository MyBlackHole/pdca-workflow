---
schema: pdca.asset/v2
id: ontology:domain/skill-context-retrieval
type: domain
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 精准上下文检索
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
aliases:
- skill:context-retrieval
source_ids:
- knowledge:information-architecture.four-layer-context-model
- knowledge:information-architecture.task-fingerprint-reranking
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:process/select-task-subgraph
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 精准上下文检索

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

按CONTEXT-01执行：目标/职责/AC选种子，核验适用性，加载必要依赖，固定版本并记录选择理由。无需doctor、推荐服务或平台adapter。无语义搜索时使用实际递归文件搜索。

输出当前任务最小可信子图及理由；不遍历其他任务活动目录，不把相关链接全部展开。来源冲突、摘要漂移或权限缺失时停用该材料并说明。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。

---
schema: pdca.asset/v2
id: ontology:domain/skill-register-evidence
type: domain
semantic_kind: individual
layer: Knowledge
status: archived
authority: reference
revision: 3.1.1
summary: 登记可复核证据
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-26'
relations:
  instance_of:
  - ontology:concept/knowledge-artifact
  relates_to:
  - ontology:concept/pdca-evidence
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

> 归档说明（2026-09-26）：本页重述证据登记方法，未提供独立领域案例或运行证据；归档用于避免维护平行操作说明，不表示原文已被证伪。
> 当前方法与格式见 [EVIDENCE-01](../../concept/pdca-evidence.md) 和 [evidence 记录契约](../../contracts/record-shapes/evidence.md)。
> 下方保留原正文供比较，不作为新任务操作入口；替代链接不自动迁移既有采用，验证状态仍为 unverified。

# 登记可复核证据

## 适用条件

当前执行契约包含本动作时按需读取；本技能不拥有阶段转换或授权权力。

## 动作与判据

读取真实产物/输出，核对授权路径和来源，使用真实摘要工具，写evidence.md条目并关联AC。依据EVIDENCE-01选择类型，更正使用新版本。只有工具实际运行才登记运行结果；没有输出则记录未执行或未知，不填pass。

## 失败处理

缺必需输入、来源或工具时报告具体缺项及影响；未执行与未知结果不得写成成功。

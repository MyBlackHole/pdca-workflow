---
schema: pdca.asset/v2
id: ontology:concept/version-bump-rule
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-10
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/version-bump-rule/3.1.0
summary: 本体正文变更必改版本元数据：modified 取落盘日，versionIRI 修订号加一
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:domain/skill-advance-phase
revision: 3.1.0
authority: reference
validation:
  structural_checks:
  - 递归解析本节点身份及关系列表；目标 ID 必须可定位。引用数量不作为行为验证。
  claim_status: unverified
  adoption: claim_review_required
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# 改时 Bump 规则（version-bump-rule）

来源：T2138。依据：87 节点 `dcterms_modified` 全停 2026-09-04 而正文含 T2092/T2103/T0513 等后期修订，版本不可信。

## 规则

凡改本体节点正文（`---` 后 Markdown），必须双改：

1. `dcterms_modified` 取落盘当日（`YYYY-MM-DD`）。
2. `owl_versionIRI` 修订号加一（`x.y.z` → `x.y.z+1`）。

仅改 `testable_signal` 的 N 基线、改错别字、改格式不断语义时，可只改 1 不改 2，但须在提交信息注明。

## 检查方法

门禁比对正文 digest 与版本字段：正文变而双字段不变即阻断（`VERSION_STALE`）。

## 适用边界

新建节点不受此限（created=modified=当日，版本 1.0.0）；历史失真存量分批补，不阻塞新变更。
